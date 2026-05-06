"""Daily spend tracking. Persists to state/daily_spend.json so cost survives restarts.

Thread-safe — when agents run in parallel, multiple threads call check() and
record() concurrently. A single re-entrant lock around all state mutations
prevents the 'both pass cap-check before either records' race that would
briefly exceed the budget.
"""
from __future__ import annotations

import json
import threading
from datetime import date
from pathlib import Path

from src.config import STATE_DIR, settings


class BudgetExceeded(Exception):
    """Raised when a call would push daily spend over the configured cap."""


class BudgetTracker:
    """Tracks cumulative USD spend per UTC day. Thread-safe."""

    def __init__(self, state_path: Path | None = None) -> None:
        self.state_path = state_path or (STATE_DIR / "daily_spend.json")
        self.cap_usd = settings.daily_budget_usd
        self._lock = threading.RLock()
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
        with self._lock:
            return self._state.get(self._today(), 0.0)

    def remaining_today(self) -> float:
        return max(0.0, self.cap_usd - self.spent_today())

    def check(self, projected_cost: float) -> None:
        """Raise BudgetExceeded if recording the projected_cost would breach the cap."""
        with self._lock:
            if self._state.get(self._today(), 0.0) + projected_cost > self.cap_usd:
                raise BudgetExceeded(
                    f"Daily budget ${self.cap_usd:.2f} would be exceeded "
                    f"(spent ${self._state.get(self._today(), 0.0):.4f}, "
                    f"projected +${projected_cost:.4f})"
                )

    def record(self, cost_usd: float) -> None:
        with self._lock:
            today = self._today()
            self._state[today] = self._state.get(today, 0.0) + cost_usd
            cutoff = (date.today().toordinal()) - 30
            self._state = {
                d: v for d, v in self._state.items()
                if date.fromisoformat(d).toordinal() >= cutoff
            }
            self._save()
