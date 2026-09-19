"""
ml_engine/explainability.py
Feature importance globale et explication structurée pour une commande (po_id).
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from ml_engine.config import FEATURE_COLS, MODEL_PATH
from ml_engine.feature_engineering import build_features
from ml_engine.predict import load_model, predict_po


def global_feature_importance(top_n: int = 10) -> list[dict[str, float]]:
    """Retourne les features les plus influentes du modèle LightGBM."""
    model = load_model()
    importances = model.feature_importances_
    pairs = sorted(
        zip(FEATURE_COLS, importances),
        key=lambda item: item[1],
        reverse=True,
    )
    return [
        {"feature": name, "importance": round(float(score), 4)}
        for name, score in pairs[:top_n]
    ]


def _local_contributions(model, row: pd.DataFrame) -> list[dict[str, float]]:
    """Approximation locale : importance globale × valeur normalisée de la feature."""
    global_imp = dict(zip(FEATURE_COLS, model.feature_importances_))
    contributions: list[dict[str, float]] = []
    for col in FEATURE_COLS:
        value = float(row[col].iloc[0]) if col in row.columns else 0.0
        contributions.append(
            {
                "feature": col,
                "value": round(value, 4),
                "contribution": round(float(global_imp.get(col, 0)) * abs(value), 4),
            }
        )
    contributions.sort(key=lambda item: item["contribution"], reverse=True)
    return contributions[:8]


def explain_po(po_id: str) -> dict[str, Any]:
    """Combine prédiction ML et importance des features pour une commande."""
    prediction = predict_po(po_id)
    if prediction.get("error"):
        return {"po_id": po_id, "error": prediction["error"]}

    import duckdb

    from ml_engine.config import DUCKDB_PATH

    with duckdb.connect(str(DUCKDB_PATH), read_only=True) as conn:
        df = conn.execute(
            "SELECT * FROM gold.marts_otif_kpi WHERE po_id = ?", [po_id]
        ).df()

    features_df = build_features(df)
    for col in FEATURE_COLS:
        if col not in features_df.columns:
            features_df[col] = 0
    row = features_df[FEATURE_COLS]

    model = load_model()
    top_features = _local_contributions(model, row)

    risk_score = float(prediction["risk_score"])
    if risk_score >= 0.6:
        narrative = (
            "Risque élevé : combinaison défavorable entre coût, délai standard, "
            "criticité pièce et profil fournisseur."
        )
    elif risk_score >= 0.3:
        narrative = "Risque modéré : surveiller le fournisseur et la fenêtre de livraison promise."
    else:
        narrative = "Risque faible : profil commande aligné avec un historique OTIF favorable."

    return {
        "po_id": po_id,
        "risk_score": prediction["risk_score"],
        "risk_level": prediction["risk_level"],
        "otif_proba": prediction["otif_proba"],
        "summary": narrative,
        "top_features": top_features,
        "global_importance": global_feature_importance(5),
    }


def save_importance_snapshot(path: str | None = None) -> str:
    """Persiste l'importance globale (utilisé par le cockpit)."""
    target = path or str(MODEL_PATH.parent / "feature_importance.json")
    payload = global_feature_importance()
    with open(target, "w", encoding="utf-8") as handle:
        import json

        json.dump(payload, handle, indent=2)
    return target


if __name__ == "__main__":
    import json

    print(json.dumps(global_feature_importance(), indent=2))
