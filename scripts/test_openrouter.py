"""Quick connectivity check: prove we can call OpenRouter and get a response.

Usage:
    python scripts/test_openrouter.py
"""
from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel

from src.config import settings
from src.llm import ModelTier, OpenRouterClient

console = Console()


def main() -> int:
    console.print(Panel.fit(
        f"[cyan]Model:[/cyan] {settings.model_cheap}\n"
        f"[cyan]Daily budget:[/cyan] ${settings.daily_budget_usd:.2f}",
        title="OpenRouter connectivity test",
    ))

    client = OpenRouterClient()
    result = client.complete(
        system=(
            "You are a connectivity test endpoint. "
            "Respond with exactly: 'CONNECTED' followed by a 1-sentence haiku about macro trading."
        ),
        user="Confirm.",
        tier=ModelTier.CHEAP,
        temperature=0.7,
    )

    console.print(Panel(
        result.content,
        title=f"Response from {result.model}",
        border_style="green",
    ))

    console.print(
        f"[dim]tokens: {result.input_tokens} in / {result.output_tokens} out  |  "
        f"cost: ${result.cost_usd:.6f}  |  "
        f"spent today: ${client.budget.spent_today():.6f}  |  "
        f"remaining: ${client.budget.remaining_today():.4f}[/dim]"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
