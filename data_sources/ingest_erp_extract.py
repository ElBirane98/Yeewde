"""
Yeewde AI — Ingestion Bronze
Lit les 4 CSV ERP réels et les convertit en Parquet dans data/bronze/,
sans transformation (couche Bronze = données brutes).
"""

from pathlib import Path
import pandas as pd

# Chemins relatifs à la racine du projet
RAW_ERP_DIR = Path("data_sources/raw_erp")
BRONZE_DIR = Path("data/bronze")

# Les 4 fichiers réels du projet Yeewde AI
FILES = [
    "parts_master",
    "purchase_orders",
    "quality_incidents",
    "supply_chain_history",
]


def ingest() -> None:
    """Charge chaque CSV et l'écrit en Parquet dans la couche Bronze."""
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    for name in FILES:
        csv_path = RAW_ERP_DIR / f"{name}.csv"

        if not csv_path.exists():
            print(f"⚠️  Fichier introuvable : {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        parquet_path = BRONZE_DIR / f"{name}.parquet"
        df.to_parquet(parquet_path, index=False)

        print(f"✅ {name} : {len(df):>7} lignes, {len(df.columns)} colonnes -> {parquet_path}")

    print("\nIngestion Bronze terminée.")


if __name__ == "__main__":
    ingest()