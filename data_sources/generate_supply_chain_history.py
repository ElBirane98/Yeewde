"""
Génère supply_chain_history.csv si le fichier réel n'est pas versionné.
Usage :
  python -m data_sources.generate_supply_chain_history
  python -m data_sources.generate_supply_chain_history --rows 280000
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data_sources" / "raw_erp"
OUTPUT = RAW_DIR / "supply_chain_history.csv"


def generate(rows: int = 8000, seed: int = 42) -> Path:
    parts_path = RAW_DIR / "parts_master.csv"
    orders_path = RAW_DIR / "purchase_orders.csv"
    if not parts_path.exists() or not orders_path.exists():
        raise FileNotFoundError("parts_master.csv et purchase_orders.csv sont requis.")

    parts = pd.read_csv(parts_path)
    orders = pd.read_csv(orders_path, parse_dates=["order_date", "promised_date", "receipt_date"])

    rng = np.random.default_rng(seed)
    site_ids = orders["site_id"].dropna().unique().tolist() or ["SITE01"]
    part_ids = parts["part_id"].tolist()

    start = orders["order_date"].min()
    end = orders["receipt_date"].max()
    if pd.isna(end):
        end = orders["promised_date"].max()
    date_range = pd.date_range(start=start, end=end, freq="D")

    records: list[dict] = []
    for _ in range(rows):
        day = rng.choice(date_range)
        part_id = rng.choice(part_ids)
        site_id = rng.choice(site_ids)
        on_hand = int(rng.integers(0, 500))
        consumption = int(rng.integers(0, max(1, on_hand // 3 + 1)))
        backorder = int(rng.integers(0, 40))
        blocked = int(rng.integers(0, 20))
        forecast = int(on_hand + rng.integers(-30, 80))
        records.append(
            {
                "date": day.strftime("%Y-%m-%d"),
                "site_id": site_id,
                "part_id": part_id,
                "planned_maintenance": bool(rng.choice([False, False, True])),
                "consumption_qty": consumption,
                "on_hand_qty": on_hand,
                "backorder_qty": backorder,
                "blocked_qty": blocked,
                "forecast_qty": max(0, forecast),
                "forecast_type": rng.choice(["Statistical", "Manual", "ML"]),
                "forecast_uplift_pct": round(float(rng.uniform(-0.1, 0.25)), 3),
            }
        )

    frame = pd.DataFrame(records)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT, index=False)
    print(f"[OK] {len(frame):,} lignes écrites -> {OUTPUT}")
    return OUTPUT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=8000, help="Nombre de lignes à générer")
    parser.add_argument("--force", action="store_true", help="Écrase un fichier existant")
    args = parser.parse_args()

    if OUTPUT.exists() and not args.force:
        print(f"Fichier déjà présent : {OUTPUT} (utilisez --force pour régénérer)")
        return
    generate(rows=args.rows)


if __name__ == "__main__":
    main()
