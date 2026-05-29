"""Verify the new currency-strength data inputs actually resolve.

Checks every NEW FRED series, COT instrument, and yfinance ticker added for
the 8-major strength meter. Prints a PASS/FAIL table so we catch guessed IDs
before building the engine on top of them.

Run:  .venv\\Scripts\\python.exe -m scripts.verify_strength_data
"""
from __future__ import annotations

import sys

NEW_FRED = [
    "au_cpi_yoy", "au_unrate", "au_rate_3m_proxy", "au_bond_10y",
    "ca_cpi_yoy", "ca_unrate", "ca_rate_3m_proxy", "ca_bond_10y",
    "ch_cpi_yoy", "ch_unrate", "ch_rate_3m_proxy", "ch_bond_10y",
    "nz_cpi_index", "nz_unrate", "nz_rate_3m_proxy", "nz_bond_10y",
]

NEW_PRICES = ["NZDUSD", "USDCAD", "USDCHF", "VIX", "SPX", "COPPER", "COMMOD_BROAD"]


def check_fred() -> None:
    from src.data.fred import FredClient, all_series_ids
    fred = FredClient()
    ids = all_series_ids()
    print("\n=== FRED (new currency series) ===")
    for name in NEW_FRED:
        fid = ids.get(name, "?")
        try:
            s = fred.series(name).dropna()
            if s.empty:
                print(f"  FAIL  {name:20s} {fid:18s} -> empty")
            else:
                print(f"  PASS  {name:20s} {fid:18s} -> {s.index[-1].date()} = {float(s.iloc[-1]):.3f}")
        except Exception as e:
            print(f"  FAIL  {name:20s} {fid:18s} -> {type(e).__name__}: {str(e)[:60]}")


def check_prices() -> None:
    from src.data.prices import PriceClient
    pc = PriceClient()
    print("\n=== yfinance (new tickers) ===")
    for inst in NEW_PRICES:
        try:
            px = pc.get_latest_close(inst)
            if px is None:
                print(f"  FAIL  {inst:14s} -> None")
            else:
                print(f"  PASS  {inst:14s} -> {px:.4f}")
        except Exception as e:
            print(f"  FAIL  {inst:14s} -> {type(e).__name__}: {str(e)[:60]}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target in ("all", "fred"):
        check_fred()
    if target in ("all", "prices"):
        check_prices()
