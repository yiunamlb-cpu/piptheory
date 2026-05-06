"""Loads markdown agent prompt files from agents/ directory.

Agent prompts are markdown documents with frontmatter-like metadata at the top
(model tier, run cadence, input/output contracts). The parser extracts the
metadata where possible and uses the full document as the system prompt.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.config import AGENTS_DIR
from src.llm import ModelTier


@dataclass(frozen=True)
class AgentPrompt:
    """A loaded agent prompt — full markdown body plus extracted metadata."""

    path: Path
    name: str
    body: str  # full markdown — used as system prompt
    tier: ModelTier  # parsed from "Model tier:" line


_TIER_LINE_RE = re.compile(
    r"\*\*Model tier:\*\*\s*(.*?)(?:\n|$)", re.IGNORECASE
)


def _infer_tier(body: str) -> ModelTier:
    """Parse the 'Model tier' line from the prompt header.

    Recognizes 'Frontier' (case-insensitive) → FRONTIER; everything else → CHEAP.
    Phase A defaults to CHEAP when ambiguous.
    """
    match = _TIER_LINE_RE.search(body)
    if not match:
        return ModelTier.CHEAP
    text = match.group(1).lower()
    if "frontier" in text and "required" in text:
        return ModelTier.FRONTIER
    if text.lstrip().startswith("**frontier"):
        return ModelTier.FRONTIER
    if "frontier" in text and "cheap" not in text:
        return ModelTier.FRONTIER
    return ModelTier.CHEAP


def load_agent(relative_or_absolute: str | Path) -> AgentPrompt:
    """Load an agent prompt by path.

    Accepts:
      - A path relative to the agents/ root (e.g. 'layer1_specialists/fed_watcher.md')
      - An absolute path
      - A name without extension (e.g. 'layer1_specialists/fed_watcher')
    """
    p = Path(relative_or_absolute)
    if not p.is_absolute():
        p = AGENTS_DIR / p
    if p.suffix == "":
        p = p.with_suffix(".md")
    if not p.exists():
        raise FileNotFoundError(f"Agent prompt not found: {p}")

    body = p.read_text(encoding="utf-8")
    name = p.stem
    tier = _infer_tier(body)
    return AgentPrompt(path=p, name=name, body=body, tier=tier)
