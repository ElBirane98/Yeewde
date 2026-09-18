"""
ml_engine/feature_engineering.py
Lit la table Gold (marts_otif_kpi) depuis DuckDB et retourne
un DataFrame prêt pour l'entraînement ou la prédiction.
"""
import duckdb
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from ml_engine.config import DUCKDB_PATH, FEATURE_COLS, TARGET_COL


def load_gold_data() -> pd.DataFrame:
    """Charge marts_otif_kpi depuis DuckDB Gold."""
    conn = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    df = conn.execute("SELECT * FROM gold.marts_otif_kpi").df()
    conn.close()
    print(f"[feature_engineering] {len(df):,} lignes chargées depuis gold.marts_otif_kpi")
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme le DataFrame Gold en features ML :
    - Encode les colonnes catégorielles
    - Remplit les valeurs manquantes
    - Retourne uniquement les colonnes utiles + target
    """
    df = df.copy()

    # ── Encodage catégoriel ────────────────────────────────────────────────────
    cat_cols = {
        "part_family":          "part_family_enc",
        "criticality_class":    "criticality_class_enc",
        "supplier_risk_class":  "supplier_risk_class_enc",
    }
    for raw_col, enc_col in cat_cols.items():
        if raw_col in df.columns:
            le = LabelEncoder()
            df[enc_col] = le.fit_transform(df[raw_col].fillna("UNKNOWN"))
        else:
            df[enc_col] = 0

    # ── Booléen → int ─────────────────────────────────────────────────────────
    if "is_repairable" in df.columns:
        df["is_repairable"] = df["is_repairable"].astype(int)

    # ── Valeurs manquantes ────────────────────────────────────────────────────
    numeric_cols = [c for c in FEATURE_COLS if c in df.columns]
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # ── Filtre : lignes avec target connue (commandes livrées) ────────────────
    if TARGET_COL in df.columns:
        df = df.dropna(subset=[TARGET_COL])

    return df


def get_X_y(df: pd.DataFrame):
    """Retourne X (features) et y (target) pour sklearn/lightgbm."""
    available_features = [f for f in FEATURE_COLS if f in df.columns]
    missing = set(FEATURE_COLS) - set(available_features)
    if missing:
        print(f"[feature_engineering] ⚠️  Features absentes (mises à 0) : {missing}")
        for col in missing:
            df[col] = 0

    X = df[FEATURE_COLS]
    y = df[TARGET_COL].astype(int)
    print(f"[feature_engineering] X={X.shape}, y distribution: {y.value_counts().to_dict()}")
    return X, y


if __name__ == "__main__":
    raw = load_gold_data()
    features_df = build_features(raw)
    X, y = get_X_y(features_df)
    print(features_df[FEATURE_COLS].describe())
