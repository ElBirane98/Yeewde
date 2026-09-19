from ml_engine.predict import predict_po


def test_predict_po_returns_structured_result_for_unknown_po():
    result = predict_po("PO-UNKNOWN-1")
    assert isinstance(result, dict)
    assert result["po_id"] == "PO-UNKNOWN-1"
    assert "risk_score" in result
    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["risk_level"] in {"FAIBLE", "MOYEN", "ÉLEVÉ"}
