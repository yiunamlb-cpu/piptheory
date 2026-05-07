"""Position tracking — persists active and closed trades, advises hold/trim/close.

The system never executes; it only advises. Every advisory hook is read-only
on the trade. The user manually closes/trims on FTMO and reflects that here.
"""
from src.positions.advisor import Advice, advise_position
from src.positions.store import Position, PositionStore

__all__ = ["Position", "PositionStore", "Advice", "advise_position"]
