"""
ml_engine/predict.py
Charge le modèle LightGBM sauvegardé et retourne un score de risque OTIF
pour une commande donnée (po_id) ou un DataFrame de features.
"""
import pickle
import duckdb
import pandas as pd

from ml_engine.config import DUCKDB_PATH, MODEL_PATH, FEATURE_COLS
from ml_engine.feature_engineering import build_features


def load_model():
    """Charge le modèle pkl depuis MODEL_PATH."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_PATH}\n"
            "Lancez d'abord : python -m ml_engine.train"
        )
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    return model


def predict_po(po_id: str) -> dict:
    """
    Retourne le score de risque OTIF pour une commande spécifique.

    Returns:
        {
          "po_id": str,
          "otif_proba": float,       # probabilité d'être OTIF (0→1)
          "risk_score": float,       # 1 - otif_proba (risque de non-OTIF)
          "risk_level": str,         # "FAIBLE" / "MOYEN" / "ÉLEVÉ"
          "predicted_otif": int,     # 0 ou 1
        }
    """
    conn = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    df = conn.execute(
        "SELECT * FROM gold.marts_otif_kpi WHERE po_id = ?", [po_id]
    ).df()
    conn.close()

    if df.empty:
        return {"error": f"po_id '{po_id}' introuvable dans gold.marts_otif_kpi"}

    features_df = build_features(df)

    # S'assurer que toutes les features sont présentes
    for col in FEATURE_COLS:
        if col not in features_df.columns:
            features_df[col] = 0

    X = features_df[FEATURE_COLS]
    model = load_model()

    otif_proba = float(model.predict_proba(X)[0, 1])
    risk_score = round(1.0 - otif_proba, 4)
    predicted_otif = int(model.predict(X)[0])

    if risk_score < 0.3:
        risk_level = "FAIBLE"
    elif risk_score < 0.6:
        risk_level = "MOYEN"
    else:
        risk_level = "ÉLEVÉ"

    return {
        "po_id": po_id,
        "otif_proba": round(otif_proba, 4),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "predicted_otif": predicted_otif,
    }


def predict_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prédit le score de risque OTIF pour un DataFrame entier.
    Utile pour le scoring en masse (Dagster, monitoring).
    """
    model = load_model()
    features_df = build_features(df)

    for col in FEATURE_COLS:
        if col not in features_df.columns:
            features_df[col] = 0

    X = features_df[FEATURE_COLS]
    probas = model.predict_proba(X)[:, 1]

    result = df[["po_id", "supplier_id"]].copy() if "po_id" in df.columns else pd.DataFrame()
    result["otif_proba"] = probas
    result["risk_score"] = 1.0 - probas
    result["risk_level"] = result["risk_score"].apply(
        lambda s: "FAIBLE" if s < 0.3 else ("MOYEN" if s < 0.6 else "ÉLEVÉ")
    )
    result["predicted_otif"] = (probas >= 0.5).astype(int)
    return result


if __name__ == "__main__":
    # Test rapide : prendre le premier po_id disponible
    conn = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    first_po = conn.execute("SELECT po_id FROM gold.marts_otif_kpi LIMIT 1").fetchone()[0]
    conn.close()

    print(f"Test sur po_id = {first_po}")
    result = predict_po(first_po)
    for k, v in result.items():
        print(f"  {k:<20} {v}")
