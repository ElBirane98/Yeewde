# -*- coding: utf-8 -*-
"""
ml_engine/train.py
Entraîne un LightGBM pour prédire l'OTIF (0/1) et logue tout dans MLflow.
Usage : python -m ml_engine.train
"""
import pickle
import mlflow
import mlflow.lightgbm
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
)

from ml_engine.config import (
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME,
    LGBM_PARAMS,
    MODEL_PATH,
    TEST_SIZE,
    RANDOM_STATE,
)
from ml_engine.feature_engineering import load_gold_data, build_features, get_X_y


def train():
    print("=" * 60)
    print("  Yeewde AI — Entraînement du modèle OTIF (LightGBM)")
    print("=" * 60)

    # ── 1. Données ────────────────────────────────────────────────────────────
    raw_df = load_gold_data()
    features_df = build_features(raw_df)
    X, y = get_X_y(features_df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\nTrain : {len(X_train):,} | Test : {len(X_test):,}")

    # ── 2. MLflow ─────────────────────────────────────────────────────────────
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run(run_name="lgbm_otif_v1"):

        # ── 3. Entraînement ───────────────────────────────────────────────────
        model = LGBMClassifier(**LGBM_PARAMS)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
        )

        # ── 4. Évaluation ─────────────────────────────────────────────────────
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "roc_auc":  round(roc_auc_score(y_test, y_proba), 4),
            "f1":       round(f1_score(y_test, y_pred), 4),
            "precision":round(precision_score(y_test, y_pred), 4),
            "recall":   round(recall_score(y_test, y_pred), 4),
            "train_size": len(X_train),
            "test_size":  len(X_test),
        }

        print("\n-- Metriques ------------------------------------------")
        for k, v in metrics.items():
            print(f"  {k:<15} {v}")
        print()
        print(classification_report(y_test, y_pred, target_names=["Non-OTIF", "OTIF"]))

        # -- 5. Log MLflow -----------------------------------------------------
        mlflow.log_params(LGBM_PARAMS)
        mlflow.log_metrics({k: v for k, v in metrics.items() if isinstance(v, float)})
        mlflow.lightgbm.log_model(model, name="lgbm_otif_model")

        # -- 6. Feature importance ---------------------------------------------
        importances = dict(zip(X.columns, model.feature_importances_))
        importances_sorted = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
        print("-- Feature importance (top 5) ---------------------------------")
        for feat, imp in list(importances_sorted.items())[:5]:
            print(f"  {feat:<35} {imp}")

        # -- 7. Sauvegarde locale ----------------------------------------------
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
        print(f"\n[OK] Modele sauvegarde -> {MODEL_PATH}")

        from ml_engine.explainability import save_importance_snapshot

        save_importance_snapshot()

        run_id = mlflow.active_run().info.run_id
        print(f"[OK] MLflow run_id : {run_id}")
        print(f"     mlflow ui --backend-store-uri {MLFLOW_TRACKING_URI}")

    return model, metrics


if __name__ == "__main__":
    train()
