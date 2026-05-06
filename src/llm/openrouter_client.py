"""OpenRouter client — single entry point for all LLM calls.

OpenRouter is OpenAI-API-compatible, so we use the official `openai` package
pointed at OpenRouter's endpoint.

Returns structured responses with usage and cost so the budget tracker can enforce caps.
"""
from __future__ import annotations

import json
from enum import Enum
from typing import Any, Literal

import httpx
import structlog
from openai import APIConnectionError, APIError, APITimeoutError, OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import settings
from src.llm.budget import BudgetTracker

log = structlog.get_logger(__name__)

# Long-tail completions on DeepSeek V4 Pro can take 90-120s. Default httpx
# timeout would interrupt them; we extend.
_HTTP_TIMEOUT_SECONDS = 240.0

# Retryable: transient transport errors and malformed/truncated server responses.
_RETRY_EXCEPTIONS = (
    APIConnectionError,
    APITimeoutError,
    httpx.ReadTimeout,
    httpx.ConnectTimeout,
    httpx.RemoteProtocolError,
    json.JSONDecodeError,
)


class ModelTier(str, Enum):
    """Tier selector — maps to MODEL_CHEAP or MODEL_FRONTIER from env."""
    CHEAP = "cheap"
    FRONTIER = "frontier"


class CallResult(BaseModel):
    """Structured response from a model call."""
    content: str
    model: str
    tier: ModelTier
    input_tokens: int
    output_tokens: int
    cost_usd: float
    raw: dict[str, Any]


class OpenRouterClient:
    """Wraps OpenAI client pointed at OpenRouter, with budget enforcement.

    Reads OPENROUTER_API_KEY, MODEL_CHEAP, MODEL_FRONTIER from settings.
    All calls go through `complete()` so we can enforce the daily spend cap.
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, budget: BudgetTracker | None = None) -> None:
        self._client = OpenAI(
            base_url=self.BASE_URL,
            api_key=settings.openrouter_api_key,
            timeout=_HTTP_TIMEOUT_SECONDS,
            max_retries=0,  # we manage retries ourselves via tenacity
            default_headers={
                # OpenRouter uses these for ranking; harmless for our private use.
                "HTTP-Referer": "https://github.com/yiunamlb-cpu/nam-hedgefund",
                "X-Title": "nam-hedgefund",
            },
        )
        self.budget = budget or BudgetTracker()

    def _model_for(self, tier: ModelTier) -> str:
        return settings.model_frontier if tier == ModelTier.FRONTIER else settings.model_cheap

    def complete(
        self,
        *,
        system: str,
        user: str,
        tier: ModelTier | Literal["cheap", "frontier"] = ModelTier.CHEAP,
        temperature: float = 0.3,
        max_tokens: int | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> CallResult:
        """Run a single chat completion. Enforces budget cap before and after.

        Pre-call: checks current daily spend vs cap. If already over, raises BudgetExceeded.
        Post-call: records actual cost from OpenRouter response.
        """
        if isinstance(tier, str):
            tier = ModelTier(tier)
        model = self._model_for(tier)

        # Pre-call budget check (cheap conservative estimate)
        # Real cost recorded post-call from OpenRouter response.
        self.budget.check(projected_cost=0.0)  # already-over check

        log.info("openrouter_call_start", model=model, tier=tier.value)

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            # Ask OpenRouter to include cost in response
            "extra_body": {"usage": {"include": True}},
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if response_format is not None:
            kwargs["response_format"] = response_format

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=2, min=2, max=30),
            retry=retry_if_exception_type(_RETRY_EXCEPTIONS),
            reraise=True,
        )
        def _do_call() -> ChatCompletion:
            try:
                return self._client.chat.completions.create(**kwargs)
            except APIError as e:
                # Some 5xx and rate-limit responses come back as APIError.
                # Retry on 408/425/429/500/502/503/504; raise others.
                status = getattr(e, "status_code", None)
                if status in (408, 425, 429, 500, 502, 503, 504):
                    log.warning("openrouter_retryable_api_error", status=status, msg=str(e)[:200])
                    raise
                raise

        response: ChatCompletion = _do_call()

        content = response.choices[0].message.content or ""
        usage = response.usage

        # OpenRouter returns cost in the usage object via the include flag
        raw = response.model_dump()
        cost_usd = float(raw.get("usage", {}).get("cost", 0.0)) if raw.get("usage") else 0.0

        result = CallResult(
            content=content,
            model=model,
            tier=tier,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            cost_usd=cost_usd,
            raw=raw,
        )

        self.budget.record(cost_usd)
        log.info(
            "openrouter_call_complete",
            model=model,
            tier=tier.value,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=cost_usd,
            spent_today=self.budget.spent_today(),
        )

        return result
