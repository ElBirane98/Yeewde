from rag_engine.retriever import retrieve
from rag_engine.query import ask_rag_engine


def test_retrieve_uses_sql_fallback_when_index_is_missing(monkeypatch):
    def raise_missing():
        raise RuntimeError("missing collection")

    monkeypatch.setattr("rag_engine.retriever.get_collection", raise_missing)

    result = retrieve("fournisseur avec retard")
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(item, str) for item in result)


def test_ask_rag_engine_returns_local_summary_without_api_key(monkeypatch):
    monkeypatch.setattr("rag_engine.query.GROQ_API_KEY", "")
    response = ask_rag_engine("Quel est le risque fournisseur ?")
    assert isinstance(response, str)
    assert len(response) > 40


def test_ask_rag_engine_uses_supplier_context_in_fallback(monkeypatch):
    monkeypatch.setattr("rag_engine.query.GROQ_API_KEY", "")
    response = ask_rag_engine("Pourquoi le fournisseur SUP004 a-t-il chuté ?")
    text = response.lower()
    assert "sup004" in text or "fournisseur" in text
    assert any(word in text for word in ["otif", "retard", "délai", "incident"]) 
    assert len(response) > 120
