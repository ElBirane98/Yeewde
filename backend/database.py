from __future__ import annotations

import duckdb

from ml_engine.config import DUCKDB_PATH

DB_PATH = str(DUCKDB_PATH)


def get_connection() -> duckdb.DuckDBPyConnection:
    """Ouvre une connexion en lecture au fichier DuckDB du projet."""
    return duckdb.connect(DB_PATH, read_only=True)


def get_db_connection(read_only: bool = True):
    if read_only:
        return get_connection()
    return duckdb.connect(DB_PATH, read_only=False)


def database_ready() -> bool:
    if not DUCKDB_PATH.exists():
        return False
    try:
        with duckdb.connect(str(DUCKDB_PATH), read_only=True) as conn:
            conn.execute("SHOW TABLES")
        return True
    except Exception:
        return False
