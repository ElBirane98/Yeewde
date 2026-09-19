"""
ml_engine/evaluate.py
Évalue le modèle sauvegardé sur un jeu de test hold-out (mêmes features que train.py).
Usage : python -m ml_engine.evaluate
"""
from __future__ import annotations

import json
from pathlib import Path

from sklearn.metrics import (
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from ml_engine.config import MODEL_PATH, RANDOM_STATE, ROOT, TEST_SIZE
from ml_engine.feature_engineering import build_features, get_X_y, load_gold_data
from ml_engine.predict import load_model


REPORT_PATH = ROOT / "data" / "gold" / "model_eval_report.json"


def evaluate_model() -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_PATH}. Lancez python -m ml_engine.train"
        )

    raw_df = load_gold_data()
    features_df = build_features(raw_df)
    X, y = get_X_y(features_df)

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    model = load_model()
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "test_size": int(len(y_test)),
        "baseline_otif_rate": round(float(y.mean()), 4),
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(classification_report(y_test, y_pred, target_names=["Non-OTIF", "OTIF"]))
    print(f"[OK] Rapport d'évaluation -> {REPORT_PATH}")
    return metrics


if __name__ == "__main__":
    evaluate_model()
