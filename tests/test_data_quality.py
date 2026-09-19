import pandas as pd

from ml_engine.feature_engineering import build_features, get_X_y


def test_build_features_keep_expected_columns():
    df = pd.DataFrame(
        {
            "ordered_qty": [100, 200],
            "unit_cost": [10, 20],
            "total_order_cost": [1000, 4000],
            "standard_lead_time_days": [10, 12],
            "is_repairable": [1, 0],
            "shelf_life_days": [60, 90],
            "part_family": ["A", "B"],
            "criticality_class": ["high", "low"],
            "supplier_risk_class": ["medium", "high"],
            "otif_score": [1, 0],
        }
    )

    features_df = build_features(df)
    assert {"part_family_enc", "criticality_class_enc", "supplier_risk_class_enc"}.issubset(features_df.columns)
    assert "otif_score" in features_df.columns


def test_get_x_y_has_feature_matrix():
    df = pd.DataFrame(
        {
            "ordered_qty": [10, 11],
            "unit_cost": [1.5, 2.0],
            "total_order_cost": [15, 22],
            "standard_lead_time_days": [5, 6],
            "is_repairable": [1, 0],
            "shelf_life_days": [30, 45],
            "part_family_enc": [0, 1],
            "criticality_class_enc": [1, 0],
            "supplier_risk_class_enc": [0, 1],
            "otif_score": [1, 0],
        }
    )

    X, y = get_X_y(df)
    assert X.shape[1] >= 9
    assert len(X) == len(y) == 2
    assert set(y.unique()).issubset({0, 1})
