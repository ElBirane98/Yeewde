"""
Injecte des commandes ERP « en cours » (sans receipt_date) dans la couche Bronze.
Usage : python -m data_sources.simulate_live_feed --n 15
"""
from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data_sources" / "raw_erp" / "purchase_orders.csv"
BRONZE_PO = ROOT / "data" / "bronze" / "purchase_orders.parquet"


def _next_po_ids(existing: pd.Series, n: int) -> list[str]:
    numeric = (
        existing.str.extract(r"(\d+)", expand=False).dropna().astype(int).max()
        if not existing.empty
        else 0
    )
    start = int(numeric) + 1
    return [f"PO{start + i:06d}" for i in range(n)]


def simulate(n: int = 15, seed: int = 7) -> dict:
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"CSV source introuvable : {RAW_CSV}")

    base = pd.read_csv(RAW_CSV, parse_dates=["order_date", "promised_date", "receipt_date"])
    rng = np.random.default_rng(seed)

    sample = base.sample(n=min(n * 3, len(base)), random_state=seed).reset_index(drop=True)
    po_ids = _next_po_ids(base["po_id"], n)

    today = pd.Timestamp.today().normalize()
    rows: list[dict] = []
    for idx in range(n):
        template = sample.iloc[idx % len(sample)]
        order_date = today - timedelta(days=int(rng.integers(1, 20)))
        lead = int((template["promised_date"] - template["order_date"]).days)
        lead = max(lead, 7)
        promised_date = order_date + timedelta(days=lead)
        rows.append(
            {
                "po_id": po_ids[idx],
                "supplier_id": template["supplier_id"],
                "site_id": template["site_id"],
                "part_id": template["part_id"],
                "order_date": order_date.strftime("%Y-%m-%d"),
                "promised_date": promised_date.strftime("%Y-%m-%d"),
                "receipt_date": pd.NA,
                "ordered_qty": int(template["ordered_qty"]),
                "received_qty": 0,
            }
        )

    simulated = pd.DataFrame(rows)
    merged = pd.concat([base, simulated], ignore_index=True)

    BRONZE_PO.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(BRONZE_PO, index=False)

    return {
        "added_rows": n,
        "total_rows": len(merged),
        "new_po_ids": po_ids,
        "bronze_path": str(BRONZE_PO),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=15, help="Nombre de commandes simulées")
    args = parser.parse_args()
    result = simulate(n=args.n)
    print(f"[OK] {result['added_rows']} commandes injectées -> {result['bronze_path']}")
    print("Relancez dbt build pour intégrer les commandes en cours.")


if __name__ == "__main__":
    main()
