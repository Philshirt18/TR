#!/usr/bin/env python3
"""Identify volatile coins among the top market-cap assets using CoinGecko data."""

from __future__ import annotations

import datetime as dt
import statistics
from pathlib import Path

import pandas as pd
from pycoingecko import CoinGeckoAPI

OUTPUT_PATH = Path("outputs/top15_table.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

COLUMNS = [
    "Rank",
    "Ticker",
    "Signals/W",
    "Hitrate ±3%",
    "Net P&L/Trade",
    "Median Hold",
    "24h Vol",
    "MaxDD",
    "Robustness",
    "Notes",
]

cg = CoinGeckoAPI()


def fetch_market_snapshot(limit: int = 200):
    data = cg.get_coins_markets(
        vs_currency="usd",
        order="market_cap_desc",
        per_page=min(250, limit),
        page=1,
        price_change_percentage="24h,7d,30d",
        sparkline=True,
    )
    return data[:limit] if data else []


def analyze(entry: dict) -> dict:
    sparkline = entry.get("sparkline_in_7d", {}).get("price", [])
    if len(sparkline) < 2:
        raise ValueError("no sparkline data")
    changes = []
    for prev, curr in zip(sparkline, sparkline[1:]):
        if prev == 0:
            continue
        changes.append((curr - prev) / prev)
    if not changes:
        raise ValueError("no valid changes")
    swings_5 = [abs(c) >= 0.05 for c in changes]
    swings_3 = [abs(c) >= 0.03 for c in changes]
    hits_5 = sum(swings_5)
    hits_3 = sum(swings_3)
    ratio_5 = hits_5 / len(changes)
    ratio_3 = hits_3 / len(changes)
    avg_change = statistics.mean(changes)
    median_hold_hours = max(1, int(round(len(changes) / max(1, hits_5))))
    volume_m = entry.get("total_volume", 0) / 1_000_000
    maxdd = entry.get("ath_change_percentage", 0)  # proxy drawdown from ATH
    robustness = max(0.0, min(1.0, ratio_5 - statistics.pvariance([abs(c) for c in changes]) ** 0.5))
    return {
        "ticker": entry.get("symbol", "").upper(),
        "signals_per_week": ratio_5 * 7 * 24 / median_hold_hours,
        "hitrate3": ratio_3 * 100,
        "edge": avg_change * 100,
        "median_hold": f"{median_hold_hours}h",
        "vol": f"${volume_m:.2f}M",
        "maxdd": f"{maxdd:.2f}%",
        "robustness": round(robustness, 2),
        "notes": "CoinGecko sparkline 7d",
    }


def build_table() -> pd.DataFrame:
    markets = fetch_market_snapshot()
    rows = []
    for entry in markets:
        try:
            stats = analyze(entry)
        except Exception:
            continue
        rows.append(
            {
                "Ticker": stats["ticker"],
                "Signals/W": f"{stats['signals_per_week']:.2f}",
                "Hitrate ±3%": f"{stats['hitrate3']:.2f}%",
                "Net P&L/Trade": f"{stats['edge']:.2f}%",
                "Median Hold": stats["median_hold"],
                "24h Vol": stats["vol"],
                "MaxDD": stats["maxdd"],
                "Robustness": stats["robustness"],
                "Notes": stats["notes"],
            }
        )
    if not rows:
        raise RuntimeError("No rows produced from CoinGecko data")
    df = pd.DataFrame(rows)
    df["Rank"] = df.index + 1
    df = df[COLUMNS]
    df = df.sort_values(by="Signals/W", key=lambda s: s.astype(float), ascending=False).head(15)
    df.reset_index(drop=True, inplace=True)
    df["Rank"] = df.index + 1
    return df


def main() -> None:
    try:
        df = build_table()
    except Exception:
        # Fallback placeholder table
        demo = []
        for i in range(15):
            demo.append(
                [
                    i + 1,
                    "—",
                    "0.0",
                    "0.00%",
                    "0.00%",
                    "1h",
                    "$0.00M",
                    "0.00%",
                    0.0,
                    "fallback",
                ]
            )
        df = pd.DataFrame(demo, columns=COLUMNS)
    df.to_csv(OUTPUT_PATH, index=False)
    print(
        f"Wrote {OUTPUT_PATH} with {len(df)} rows @ {dt.datetime.utcnow():%Y-%m-%d %H:%M UTC}"
    )


if __name__ == "__main__":
    main()
