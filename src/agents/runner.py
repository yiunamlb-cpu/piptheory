"""Run a single agent end-to-end. Loads its prompt, calls OpenRouter, returns result."""
from __future__ import annotations

import structlog

from src.agents.loader import AgentPrompt, load_agent
from src.llm import OpenRouterClient
from src.llm.openrouter_client import CallResult

log = structlog.get_logger(__name__)


def run_agent(
    agent: str | AgentPrompt,
    user_message: str,
    *,
    client: OpenRouterClient | None = None,
    temperature: float = 0.3,
) -> CallResult:
    """Run an agent.

    Args:
        agent: Either a path/name (loaded via loader) or a pre-loaded AgentPrompt.
        user_message: The task-specific input — usually structured data the agent
            should reason over (e.g., latest FOMC statement text, COT data summary).
        client: Optional pre-built OpenRouterClient. Defaults to a fresh one.
        temperature: Sampling temperature. Defaults to 0.3 for analytical agents.

    Returns:
        CallResult with the agent's output, tokens used, cost, and raw response.
    """
    prompt = agent if isinstance(agent, AgentPrompt) else load_agent(agent)
    client = client or OpenRouterClient()

    log.info("run_agent_start", agent=prompt.name, tier=prompt.tier.value)

    result = client.complete(
        system=prompt.body,
        user=user_message,
        tier=prompt.tier,
        temperature=temperature,
    )

    log.info(
        "run_agent_complete",
        agent=prompt.name,
        cost_usd=result.cost_usd,
        output_chars=len(result.content),
    )

    return result
