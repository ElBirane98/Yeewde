"""
rag_engine/logging.py
Journalise chaque appel RAG dans une table DuckDB (gold/rag_logs.duckdb).
"""
import time
import duckdb
from pathlib import Path

from rag_engine.config import RAG_LOG_DB


def log_rag_call(
    prompt: str,
    response: str,
    latency_ms: float,
    tokens_used: int,
    retrieved_docs: list[str],
) -> None:
    """Insere un enregistrement de log RAG dans DuckDB."""
    # Cree le dossier si besoin
    Path(RAG_LOG_DB).parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(RAG_LOG_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rag_logs (
            ts          DOUBLE,
            prompt      TEXT,
            response    TEXT,
            latency_ms  DOUBLE,
            tokens_used INTEGER,
            docs_retrieved INTEGER
        )
    """)
    conn.execute(
        "INSERT INTO rag_logs VALUES (?, ?, ?, ?, ?, ?)",
        [time.time(), prompt, response, latency_ms, tokens_used, len(retrieved_docs)]
    )
    conn.close()


def get_rag_stats() -> dict:
    """Retourne des statistiques aggregees sur les appels RAG."""
    if not Path(RAG_LOG_DB).exists():
        return {"total_calls": 0, "avg_latency_ms": 0, "total_tokens": 0}

    conn = duckdb.connect(RAG_LOG_DB, read_only=True)
    try:
        row = conn.execute("""
            SELECT
                COUNT(*)            AS total_calls,
                AVG(latency_ms)     AS avg_latency_ms,
                SUM(tokens_used)    AS total_tokens
            FROM rag_logs
        """).fetchone()
        return {
            "total_calls":    row[0],
            "avg_latency_ms": round(row[1] or 0, 1),
            "total_tokens":   row[2] or 0,
        }
    finally:
        conn.close()
