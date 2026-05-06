"""Dry-run a real agent prompt with stub data — proves the full pipeline works.

Loads agents/layer1_specialists/fed_watcher.md, hands it a stub task, prints the result.
This is NOT a real Fed analysis — just a connectivity proof for the agent layer.

Usage:
    python scripts/run_agent_dry.py
"""
from __future__ import annotations

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.agents import load_agent, run_agent
from src.llm import OpenRouterClient

console = Console()

STUB_USER_MESSAGE = """\
DRY RUN — connectivity test for the agent runtime.

This is a stub task to verify your prompt loads correctly and you produce
output in the schema specified in your prompt.

Pretend the most recent FOMC statement is hypothetical and produce your
output schema with PLACEHOLDER values (e.g., LANGUAGE_DRIFT_SCORE: 0,
POLICY_STANCE_NOW: <example>, etc.). Mark the output as DRY_RUN.

Keep the output under 50 lines. This is just to prove the pipeline works.
"""


def main() -> int:
    agent_path = "layer1_specialists/fed_watcher"
    console.rule(f"[cyan]Loading agent: {agent_path}[/cyan]")

    prompt = load_agent(agent_path)
    console.print(
        f"[dim]Loaded {prompt.path.name} | tier: {prompt.tier.value} | "
        f"prompt size: {len(prompt.body)} chars[/dim]"
    )

    client = OpenRouterClient()
    result = run_agent(prompt, STUB_USER_MESSAGE, client=client)

    console.rule("[green]Agent output[/green]")
    console.print(Panel(Markdown(result.content), border_style="green"))

    console.rule("[dim]Run stats[/dim]")
    console.print(
        f"[dim]model: {result.model}  |  "
        f"tokens: {result.input_tokens} in / {result.output_tokens} out  |  "
        f"cost: ${result.cost_usd:.6f}  |  "
        f"spent today: ${client.budget.spent_today():.6f}[/dim]"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
