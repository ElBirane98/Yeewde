# Architecture cible (cloud / production)

Document de perspective uniquement — **non implémentée** dans Yeewde local-first.

| Composant local | Cible production |
|---|---|
| DuckDB + Parquet | BigQuery / Snowflake / lake objet (S3, GCS) |
| Dagster dev | Dagster Cloud |
| MLflow SQLite | MLflow Server (PostgreSQL + artefact store) |
| ChromaDB local | Service vectoriel managé |
| Logging RAG DuckDB | LangFuse / Phoenix si volume élevé |
| Batch CSV | Kafka / CDC ERP en amont de Bronze |
| Cockpit sans auth | SSO + RBAC |

Montée en charge justifiée lorsque le volume, le multi-équipe ou les SLA production l'exigent.
