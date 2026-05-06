"""Daily spend tracking. Persists to state/daily_spend.json so cost survives restarts."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from src.config import STATE_DIR, settings


class BudgetExceeded(Exception):
    """Raised when a call would push daily spend over the configured cap."""


class BudgetTracker:
    """Tracks cumulative USD spend per UTC day. Persists to JSON."""

    def __init__(self, state_path: Path | None = None) -> None:
        self.state_path = state_path or (STATE_DIR / "daily_spend.json")
        self.cap_usd = settings.daily_budget_usd
        self._state = self._load()

    def _load(self) -> dict[str, float]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def _save(self) -> None:
        self.state_path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    def _today(self) -> str:
        return date.today().isoformat()

    def spent_today(self) -> float:
        return self._state.get(self._today(), 0.0)

    def remaining_today(self) -> float:
        return max(0.0, self.cap_usd - self.spent_today())

    def check(self, projected_cost: float) -> None:
        """Raise BudgetExceeded if recording the projected_cost would breach the cap."""
        if self.spent_today() + projected_cost > self.cap_usd:
            raise BudgetExceeded(
                f"Daily budget ${self.cap_usd:.2f} would be exceeded "
                f"(spent ${self.spent_today():.4f}, projected +${projected_cost:.4f})"
            )

    def record(self, cost_usd: float) -> None:
        today = self._today()
        self._state[today] = self._state.get(today, 0.0) + cost_usd
        # Prune entries older than 30 days
        cutoff = (date.today().toordinal()) - 30
        self._state = {
            d: v for d, v in self._state.items()
            if date.fromisoformat(d).toordinal() >= cutoff
        }
        self._save()
