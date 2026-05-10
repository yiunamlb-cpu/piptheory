"""FTMO informational guardrails — not enforcement.

Audit feedback: a swing trader on FTMO needs to see (a) trailing
drawdown headroom, (b) whether new positions correlate with held ones,
(c) weekend gap risk, (d) running swap costs. These are *informational*
— the system never enforces sizing or refuses trades. The user's job is
discipline; this widget supplies the numbers so they can exercise it.

Configuration is in data/ftmo_config.yaml — user can update if their
account size, drawdown limits, or rules change. Defaults assume a
$100,000 account with a 5% trailing drawdown (FTMO's typical setup).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from src.config import ROOT


# ─── Config ──────────────────────────────────────────────────────────────


_DEFAULT_CONFIG = {
    "account_size_usd": 100000.0,
    "trailing_drawdown_pct": 5.0,         # FTMO swing typical: 5%
    "max_drawdown_pct": 10.0,             # FTMO total: 10%
    "weekend_gap_high_risk_symbols": ["GC", "CL", "DXY"],   # commodities + dollar most prone to weekend gaps
    # Correlation groups — if two positions are in the same group,
    # they're considered correlated for the same-direction warning.
    "correlation_groups": {
        "USD_BULL": ["DXY", "USDJPY"],     # USD strength expressions
        "USD_BEAR": ["EURUSD", "GBPUSD", "AUDUSD"],   # USD weakness expressions
        "RISK_ON": ["ES", "NQ", "AUDUSD"],
        "INFLATION_HEDGE": ["GC", "CL"],
    },
    # Approximate daily swap cost in USD per standard lot (rough — actual
    # depends on pair + broker side). Negative = cost; positive = earn.
    # These are typical 2026-era values, conservative on the cost side.
    "swap_cost_per_lot_per_day": {
        "GC": -8.0,     "CL": -6.0,
        "ES": -3.0,     "NQ": -3.0,
        "DXY": -2.0,
        "EURUSD": -2.5, "GBPUSD": -3.0, "AUDUSD": -3.5, "USDJPY": +1.5,
    },
}


_CONFIG_PATH = ROOT / "data" / "ftmo_config.yaml"


def load_config() -> dict:
    if not _CONFIG_PATH.exists():
        return dict(_DEFAULT_CONFIG)
    try:
        with _CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        # Shallow-merge over defaults
        merged = dict(_DEFAULT_CONFIG)
        merged.update(data)
        return merged
    except Exception:
        return dict(_DEFAULT_CONFIG)


# ─── Computation ─────────────────────────────────────────────────────────


@dataclass
class FtmoStatus:
    account_size: float
    trailing_dd_remaining_usd: float       # estimated headroom (account_size - net_loss_so_far)
    trailing_dd_remaining_pct: float
    open_unrealised_pnl_usd: float         # rough — uses pnl_pct * notional estimate
    correlation_warnings: list[str]        # human-readable strings
    weekend_gap_warning: str | None        # set if Friday + held high-gap-risk position
    estimated_daily_swap_usd: float        # negative = cost
    open_position_count: int


def _estimate_notional_per_lot(instrument: str, price: float) -> float:
    """Rough notional value per standard lot in USD. Used to convert
    pct P&L to dollar P&L. Numbers are typical FTMO contract specs.
    """
    # Standard lot sizes in base units, then multiplied by USD price.
    contracts = {
        "GC": 100,          # 100oz × $price
        "CL": 1000,         # 1000bbl × $price
        "ES": 50,           # $50 × index
        "NQ": 20,           # $20 × index
        "DXY": 1000,        # $1000 × index
        "EURUSD": 100000,   # 100k base
        "GBPUSD": 100000,
        "AUDUSD": 100000,
        "USDJPY": 100000,
    }
    return contracts.get(instrument, 100000) * (price or 1.0)


def compute_ftmo_status(
    open_trades: list[dict],
    config: dict | None = None,
    today: date | None = None,
) -> FtmoStatus:
    """Build the FTMO informational summary.

    open_trades is the list produced by _build_open_trades_block(). Each
    item has at least: instrument, direction, entry_price, current_price,
    pnl_pct, size_units (if recorded — defaults to 0.01 lot if unset).
    """
    cfg = config or load_config()
    today = today or date.today()
    account_size = float(cfg.get("account_size_usd", 100000.0))
    dd_pct = float(cfg.get("trailing_drawdown_pct", 5.0))

    # Sum unrealised P&L in USD across open trades. Use a conservative
    # per-instrument notional × pnl_pct.
    pnl_usd = 0.0
    for t in open_trades:
        price = (t.get("current_price") or t.get("entry_price")) or 0.0
        notional = _estimate_notional_per_lot(t["instrument"], price)
        # If size_units not recorded, assume 0.01 lot (minimal)
        size_units = float(t.get("size_units") or 0.01)
        pnl_usd += notional * size_units * (float(t.get("pnl_pct") or 0.0) / 100.0)

    # Trailing drawdown: when no losses, full headroom. Approximation —
    # FTMO's actual trailing DD is computed against the highest equity
    # reached, not just current balance. Without realised-trade history
    # plumbed in, this is a rough lower bound: assumes account at
    # starting balance, deducts only losing unrealised P&L.
    dd_consumed = -pnl_usd if pnl_usd < 0 else 0.0
    dd_remaining_usd = (account_size * dd_pct / 100.0) - dd_consumed
    dd_remaining_pct = max(0.0, dd_remaining_usd / account_size * 100.0)

    # Correlation: if two open trades are in the same group AND in the
    # same direction, that's accidentally doubled exposure on one theme.
    warnings: list[str] = []
    groups = cfg.get("correlation_groups", {}) or {}
    by_dir = {"long": [], "short": []}
    for t in open_trades:
        d = t.get("direction", "").lower()
        if d in by_dir:
            by_dir[d].append(t["instrument"])
    for direction, syms in by_dir.items():
        for grp_name, members in groups.items():
            in_grp = [s for s in syms if s in members]
            if len(in_grp) >= 2:
                warnings.append(
                    f"{direction.upper()} {' & '.join(in_grp)} all express "
                    f"{grp_name.replace('_', ' ').lower()} — count as one risk unit."
                )

    # Weekend gap: if it's Friday AND any open position is in the
    # high-risk symbol list
    weekend_warning = None
    high_risk = set(cfg.get("weekend_gap_high_risk_symbols", []) or [])
    if today.weekday() == 4 and high_risk.intersection({t["instrument"] for t in open_trades}):
        affected = sorted(high_risk.intersection({t["instrument"] for t in open_trades}))
        weekend_warning = (
            f"It's Friday — {', '.join(affected)} have elevated weekend-gap "
            f"risk (commodities + dollar). Consider trimming or flat into close."
        )

    # Swap cost — daily total across positions
    swap_table = cfg.get("swap_cost_per_lot_per_day", {}) or {}
    swap_total = 0.0
    for t in open_trades:
        per_lot = swap_table.get(t["instrument"], -2.0)
        size_units = float(t.get("size_units") or 0.01)
        swap_total += per_lot * size_units * 100  # 100 to scale 0.01 lot back

    return FtmoStatus(
        account_size=account_size,
        trailing_dd_remaining_usd=dd_remaining_usd,
        trailing_dd_remaining_pct=dd_remaining_pct,
        open_unrealised_pnl_usd=pnl_usd,
        correlation_warnings=warnings,
        weekend_gap_warning=weekend_warning,
        estimated_daily_swap_usd=swap_total,
        open_position_count=len(open_trades),
    )
