"""
ml_engine/drift_monitor.py
Compare les features de référence (commandes livrées) aux commandes récentes / en cours
via Evidently AI. Persiste data/gold/drift_report.json pour l'API et le cockpit.
Usage : python -m ml_engine.drift_monitor
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ml_engine.config import FEATURE_COLS, ROOT
from ml_engine.feature_engineering import build_features, load_gold_data

DRIFT_REPORT_PATH = ROOT / "data" / "gold" / "drift_report.json"


def _prepare_feature_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = load_gold_data()
    features = build_features(raw, require_target=False)

    for col in FEATURE_COLS:
        if col not in features.columns:
            features[col] = 0

    if "receipt_date" in raw.columns:
        reference_mask = raw["receipt_date"].notna()
        current_mask = raw["receipt_date"].isna()
    elif "is_delivered" in raw.columns:
        reference_mask = raw["is_delivered"] == True  # noqa: E712
        current_mask = raw["is_delivered"] == False  # noqa: E712
    else:
        split = int(len(features) * 0.8)
        reference_mask = pd.Series([True] * split + [False] * (len(features) - split))
        current_mask = ~reference_mask

    reference = features.loc[reference_mask.values, FEATURE_COLS]
    current = features.loc[current_mask.values, FEATURE_COLS]

    if current.empty:
        current = features[FEATURE_COLS].tail(min(500, len(features)))

    if len(reference) > 5000:
        reference = reference.sample(5000, random_state=42)

    return reference, current


def run_drift_check() -> dict:
    reference, current = _prepare_feature_frames()

    drift_detected = False
    drift_share = 0.0
    details: dict = {"reference_rows": len(reference), "current_rows": len(current)}

    try:
        from evidently import Dataset
        from evidently.core.report import Report
        from evidently.presets import DataDriftPreset

        report = Report([DataDriftPreset()])
        snapshot = report.run(
            Dataset.from_pandas(current),
            Dataset.from_pandas(reference),
        )
        payload = snapshot.dict() if hasattr(snapshot, "dict") else {}
        for metric in payload.get("metrics", []):
            value = metric.get("value") or {}
            if isinstance(value, dict) and "share" in value:
                drift_share = max(drift_share, float(value["share"]))
                drift_detected = drift_detected or float(value.get("count", 0)) > 0
        details["evidently_metrics"] = payload.get("metrics", [])
    except Exception as exc:
        details["evidently_error"] = str(exc)
        # Fallback statistique simple si Evidently indisponible
        for col in FEATURE_COLS:
            ref_mean = float(reference[col].mean())
            cur_mean = float(current[col].mean())
            if ref_mean != 0 and abs(cur_mean - ref_mean) / abs(ref_mean) > 0.25:
                drift_detected = True
                drift_share = max(drift_share, 0.35)

    result = {
        "drift_detected": drift_detected,
        "drift_share": round(drift_share, 4),
        "status": "measured",
        "summary": (
            "Dérive détectée sur les features de scoring."
            if drift_detected
            else "Pas de dérive significative sur l'échantillon courant."
        ),
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }

    DRIFT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DRIFT_REPORT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def load_drift_report() -> dict:
    if not DRIFT_REPORT_PATH.exists():
        return {
            "drift_detected": None,
            "status": "not_measured",
            "summary": "Aucun rapport de dérive récent. Lancez python -m ml_engine.drift_monitor",
        }
    try:
        report = json.loads(DRIFT_REPORT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "drift_detected": None,
            "status": "invalid_report",
            "summary": "Le rapport de dérive est illisible. Relancez le contrôle de drift.",
            "error": str(exc),
        }
    if not isinstance(report, dict):
        return {
            "drift_detected": None,
            "status": "invalid_report",
            "summary": "Le rapport de dérive n'a pas le format attendu.",
        }
    return report


if __name__ == "__main__":
    print(json.dumps(run_drift_check(), indent=2))
