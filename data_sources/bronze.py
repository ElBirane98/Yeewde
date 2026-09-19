"""Materialise the local Bronze layer from the tracked ERP extracts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data_sources" / "raw_erp"
BRONZE_DIR = ROOT / "data" / "bronze"
SOURCE_FILES = (
    "parts_master.csv",
    "purchase_orders.csv",
    "quality_incidents.csv",
    "supply_chain_history.csv",
)


def materialize_bronze() -> dict[str, object]:
    """Convert every tracked CSV input into a fresh Parquet Bronze dataset."""
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    files: list[str] = []
    row_count = 0

    for filename in SOURCE_FILES:
        source = RAW_DIR / filename
        if not source.exists():
            if filename == "supply_chain_history.csv":
                from data_sources.generate_supply_chain_history import generate

                generate()
                source = RAW_DIR / filename
            else:
                raise FileNotFoundError(f"Source ERP introuvable : {source}")
        frame = pd.read_csv(source)
        target = BRONZE_DIR / f"{source.stem}.parquet"
        frame.to_parquet(target, index=False)
        files.append(str(target))
        row_count += len(frame)

    return {"files": files, "row_count": row_count}


if __name__ == "__main__":
    print(materialize_bronze())
