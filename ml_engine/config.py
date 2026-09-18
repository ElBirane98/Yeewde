"""
ml_engine/config.py
Chemins et hyperparamètres centralisés pour tout le moteur ML.
"""
from pathlib import Path

# ── Racine du projet ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent

# ── DuckDB Gold ───────────────────────────────────────────────────────────────
DUCKDB_PATH = ROOT / "data" / "yeewde.duckdb"

# ── MLflow ────────────────────────────────────────────────────────────────────
MLFLOW_TRACKING_URI = f"sqlite:///{ROOT / 'mlruns' / 'mlflow.db'}"
MLFLOW_EXPERIMENT_NAME = "yeewde_otif_prediction"

# ── Modèle ────────────────────────────────────────────────────────────────────
MODEL_DIR = ROOT / "mlruns" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "lgbm_otif.pkl"

# ── Features utilisées pour le modèle ─────────────────────────────────────────
# IMPORTANT : uniquement des features connues AU MOMENT de la commande
# (pas de delay_days, fill_rate, actual_lead_time_days, received_qty
#  → ces valeurs ne sont connues qu'APRÈS la livraison = data leakage)
FEATURE_COLS = [
    # Caractéristiques de la commande (connues à l'ordre)
    "ordered_qty",
    "unit_cost",
    "total_order_cost",
    "standard_lead_time_days",
    # Caractéristiques de la pièce (statiques)
    "is_repairable",
    "shelf_life_days",
    # Encodées (catégorielles)
    "part_family_enc",
    "criticality_class_enc",
    "supplier_risk_class_enc",
]

TARGET_COL = "otif_score"

# ── Hyperparamètres LightGBM ──────────────────────────────────────────────────
LGBM_PARAMS = {
    "objective": "binary",
    "metric": "binary_logloss",
    "n_estimators": 300,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "max_depth": -1,
    "min_child_samples": 20,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "class_weight": "balanced",
    "random_state": 42,
    "verbose": -1,
}

TEST_SIZE = 0.2
RANDOM_STATE = 42
