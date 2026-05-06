"""Agent runtime — loads markdown agent prompts and dispatches via the LLM gateway."""

from src.agents.loader import AgentPrompt, load_agent
from src.agents.runner import run_agent

__all__ = ["AgentPrompt", "load_agent", "run_agent"]
