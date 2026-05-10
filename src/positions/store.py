"""Position store — persists active trades to state/positions.json and
closed trades to journal/closed_positions.jsonl (append-only).

Why two locations:
  - state/positions.json holds the *current* set of active positions plus
    a tail of recently-closed ones (last 30) so the dashboard can render
    a recent journal without parsing the full history.
  - journal/closed_positions.jsonl is the immutable audit log; one JSON
    object per closed position, never overwritten. This is what Layer 7
    Calibration will read once enough closed trades accumulate.

Concurrency: the dashboard is single-process (uvicorn + ThreadPoolExecutor
for run launches), but to be safe against concurrent POST requests on the
positions endpoint, all writes go through a per-process RLock.
"""
from __future__ import annotations

import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from src.config import JOURNAL_DIR, STATE_DIR

POSITIONS_PATH = STATE_DIR / "positions.json"
CLOSED_JOURNAL_PATH = JOURNAL_DIR / "closed_positions.jsonl"

# How many recent closed positions to keep in the live state file. The full
# history lives in the JSONL journal; this trims the working file so it
# doesn't grow unbounded across years of trading.
LIVE_CLOSED_TAIL = 30


@dataclass
class Position:
    """A single open or closed position.

    The `*_at_open` snapshot is the macro state at the moment the position
    was opened. The advisor compares the *current* macro state against this
    snapshot to detect "thesis weakened" or "thesis flipped" conditions.
    """
    id: str
    instrument: str
    direction: str            # "long" | "short"
    entry_price: float
    entry_date: str           # YYYY-MM-DD
    size_units: Optional[float] = None
    emergency_stop: Optional[float] = None
    notes: str = ""
    status: str = "active"    # "active" | "closed"

    # Snapshot of macro state when the trade was opened
    bias_at_open: str = ""               # "long" | "short" | "no_view"
    conviction_at_open: int = 0
    timeframe_at_open: str = ""
    thesis_at_open: str = ""             # 1-2 sentence macro narrative, frozen

    # Close fields (only set when status == "closed")
    close_price: Optional[float] = None
    close_date: Optional[str] = None
    close_reason: str = ""
    pnl_pct: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Position":
        # Tolerate older rows without newer fields.
        defaults = {f: getattr(cls, "__dataclass_fields__")[f].default
                    for f in cls.__dataclass_fields__}
        merged = {**defaults, **data}
        # Drop any unknown keys to avoid TypeError if schema diverges.
        merged = {k: v for k, v in merged.items()
                  if k in cls.__dataclass_fields__}
        return cls(**merged)

    def days_held(self, as_of: Optional[date] = None) -> int:
        as_of = as_of or date.today()
        try:
            opened = date.fromisoformat(self.entry_date)
        except ValueError:
            return 0
        return (as_of - opened).days


class PositionStore:
    """File-backed CRUD store for positions. Single-instance pattern works
    because uvicorn runs a single Python process; multiple workers would
    need an OS-level lock or sqlite — out of scope for this single-user app.
    """

    def __init__(self, path: Optional[Path] = None,
                 journal_path: Optional[Path] = None) -> None:
        self.path = path or POSITIONS_PATH
        self.journal_path = journal_path or CLOSED_JOURNAL_PATH
        self._lock = threading.RLock()
        # Ensure directories exist (config.py does this on import, but be
        # defensive against test paths)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_all(self) -> dict[str, list[dict]]:
        if not self.path.exists():
            return {"active": [], "closed_recent": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            data.setdefault("active", [])
            data.setdefault("closed_recent", [])
            return data
        except (json.JSONDecodeError, OSError):
            return {"active": [], "closed_recent": []}

    def _write_all(self, data: dict[str, list[dict]]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=False),
                       encoding="utf-8")
        tmp.replace(self.path)

    # ----- Read API -----

    def list_active(self) -> list[Position]:
        with self._lock:
            return [Position.from_dict(d) for d in self._read_all()["active"]]

    def list_closed_recent(self) -> list[Position]:
        with self._lock:
            return [Position.from_dict(d)
                    for d in self._read_all()["closed_recent"]]

    def get(self, position_id: str) -> Optional[Position]:
        with self._lock:
            data = self._read_all()
            for bucket in ("active", "closed_recent"):
                for d in data[bucket]:
                    if d.get("id") == position_id:
                        return Position.from_dict(d)
        return None

    # ----- Write API -----

    def open(
        self,
        instrument: str,
        direction: str,
        entry_price: float,
        entry_date: Optional[str] = None,
        size_units: Optional[float] = None,
        emergency_stop: Optional[float] = None,
        notes: str = "",
        bias_at_open: str = "",
        conviction_at_open: int = 0,
        timeframe_at_open: str = "",
        thesis_at_open: str = "",
    ) -> Position:
        """Open a new position. Returns the created Position with assigned id."""
        if direction not in ("long", "short"):
            raise ValueError(f"direction must be 'long' or 'short', got {direction!r}")
        if entry_price <= 0:
            raise ValueError(f"entry_price must be positive, got {entry_price}")
        pos = Position(
            id=str(uuid.uuid4())[:8],
            instrument=instrument.upper(),
            direction=direction,
            entry_price=float(entry_price),
            entry_date=entry_date or date.today().isoformat(),
            size_units=float(size_units) if size_units is not None else None,
            emergency_stop=(float(emergency_stop)
                            if emergency_stop is not None else None),
            notes=notes.strip(),
            bias_at_open=bias_at_open,
            conviction_at_open=int(conviction_at_open or 0),
            timeframe_at_open=timeframe_at_open,
            thesis_at_open=thesis_at_open,
            status="active",
        )
        with self._lock:
            data = self._read_all()
            data["active"].append(pos.to_dict())
            self._write_all(data)
        return pos

    def close(
        self,
        position_id: str,
        close_price: float,
        close_reason: str = "",
        close_date: Optional[str] = None,
    ) -> Optional[Position]:
        """Move a position from active to closed. Computes pnl_pct.

        Also appends a JSON line to journal/closed_positions.jsonl — that's
        the immutable record that Layer 7 Calibration reads later.
        """
        if close_price <= 0:
            raise ValueError(f"close_price must be positive, got {close_price}")
        with self._lock:
            data = self._read_all()
            idx = next((i for i, d in enumerate(data["active"])
                        if d.get("id") == position_id), None)
            if idx is None:
                return None
            pos = Position.from_dict(data["active"].pop(idx))
            pos.status = "closed"
            pos.close_price = float(close_price)
            pos.close_date = close_date or date.today().isoformat()
            pos.close_reason = close_reason.strip()
            # P&L %: positive = profit, negative = loss; sign-aware on direction
            sign = 1.0 if pos.direction == "long" else -1.0
            pos.pnl_pct = round(
                sign * (pos.close_price - pos.entry_price) / pos.entry_price * 100,
                3,
            )
            # Prepend so most recent close is first in the recent-tail
            data["closed_recent"].insert(0, pos.to_dict())
            data["closed_recent"] = data["closed_recent"][:LIVE_CLOSED_TAIL]
            self._write_all(data)

            # Append to immutable journal (one position per line)
            with self.journal_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(pos.to_dict(), sort_keys=False) + "\n")
            return pos

    def delete(self, position_id: str) -> bool:
        """Remove a position outright (mistake recovery). Does NOT journal it.
        Use close() for normal trade exits.
        """
        with self._lock:
            data = self._read_all()
            for bucket in ("active", "closed_recent"):
                for i, d in enumerate(data[bucket]):
                    if d.get("id") == position_id:
                        data[bucket].pop(i)
                        self._write_all(data)
                        return True
        return False

    def add_note(self, position_id: str, note: str) -> Optional[Position]:
        """Append a timestamped note to a position. Notes accumulate."""
        note = note.strip()
        if not note:
            return self.get(position_id)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        line = f"[{stamp}] {note}"
        with self._lock:
            data = self._read_all()
            for bucket in ("active", "closed_recent"):
                for d in data[bucket]:
                    if d.get("id") == position_id:
                        existing = d.get("notes", "")
                        d["notes"] = f"{existing}\n{line}".strip() if existing else line
                        self._write_all(data)
                        return Position.from_dict(d)
        return None

    def update_emergency_stop(
        self, position_id: str, new_level: float,
    ) -> Optional[Position]:
        """Move the emergency stop. Used when the advisor recommends trailing.
        The user always types the new level; the system never silently moves it.
        """
        with self._lock:
            data = self._read_all()
            for d in data["active"]:
                if d.get("id") == position_id:
                    d["emergency_stop"] = float(new_level)
                    self._write_all(data)
                    return Position.from_dict(d)
        return None

    # Whitelist of fields the user can edit on an already-recorded
    # active position. Bias / conviction / thesis snapshots are
    # deliberately excluded — those are frozen at open by design (they're
    # the baseline the advisor compares "today" against; mutating them
    # would invalidate the cross-run continuity logic).
    _EDITABLE_FIELDS = (
        "entry_price",
        "size_units",
        "emergency_stop",
        "notes",
        "entry_date",
    )

    def update_fields(
        self,
        position_id: str,
        **fields,
    ) -> Optional[Position]:
        """Patch arbitrary editable fields on an active position.

        Used by the dashboard's Edit-trade flow. Type-coerces numeric
        fields. Pass any number of keyword args from _EDITABLE_FIELDS;
        keys outside the whitelist are silently ignored to keep the
        bias_at_open / conviction_at_open snapshot frozen.

        Returns the updated Position or None if the id doesn't match
        an active position.
        """
        coerced: dict[str, object] = {}
        for k, v in fields.items():
            if k not in self._EDITABLE_FIELDS:
                continue
            if v is None or v == "":
                continue
            if k in ("entry_price", "size_units", "emergency_stop"):
                try:
                    coerced[k] = float(v)
                except (TypeError, ValueError):
                    continue
            elif k == "notes":
                # `notes` here REPLACES — to append, use add_note().
                # The Edit flow uses replace because the user is editing
                # a single text area, not adding a timestamped log entry.
                coerced[k] = str(v)
            else:
                coerced[k] = str(v)
        if not coerced:
            return self.get(position_id)
        with self._lock:
            data = self._read_all()
            for d in data["active"]:
                if d.get("id") == position_id:
                    d.update(coerced)
                    self._write_all(data)
                    return Position.from_dict(d)
        return None
