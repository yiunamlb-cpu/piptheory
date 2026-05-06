"""Central config — loads env vars from .env and exposes typed settings."""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root — the directory containing pyproject.toml
ROOT = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(ROOT / ".env")


class Settings(BaseSettings):
    """Typed settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM gateway ---
    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")
    model_cheap: str = Field("deepseek/deepseek-v4-pro", alias="MODEL_CHEAP")
    model_frontier: str = Field("deepseek/deepseek-v4-pro", alias="MODEL_FRONTIER")

    # --- Macro data ---
    fred_api_key: str = Field("", alias="FRED_API_KEY")

    # --- FX data ---
    oanda_api_key: str = Field("", alias="OANDA_API_KEY")
    oanda_account_id: str = Field("", alias="OANDA_ACCOUNT_ID")
    oanda_env: str = Field("practice", alias="OANDA_ENV")

    # --- Observability (Phase B+) ---
    langfuse_public_key: str = Field("", alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field("", alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field("http://localhost:3000", alias="LANGFUSE_HOST")

    # --- Memory (Phase B+) ---
    letta_host: str = Field("http://localhost:8283", alias="LETTA_HOST")

    # --- Cost guardrails ---
    daily_budget_usd: float = Field(5.0, alias="DAILY_BUDGET_USD")


settings = Settings()  # type: ignore[call-arg]


# --- Project paths ---
AGENTS_DIR = ROOT / "agents"
PLAYBOOK_DIR = ROOT / "playbook"
DOCS_DIR = ROOT / "docs"
STATE_DIR = ROOT / "state"
BIAS_CARDS_DIR = ROOT / "bias_cards"
JOURNAL_DIR = ROOT / "journal"

# Ensure runtime directories exist
for d in (STATE_DIR, BIAS_CARDS_DIR, JOURNAL_DIR):
    d.mkdir(exist_ok=True)
