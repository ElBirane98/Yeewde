# Documentation RAG Yeewde

## 1. Objectif

Le moteur RAG de Yeewde sert à répondre à des questions métiers sur la performance fournisseur, les retards, les incidents qualité et les KPI OTIF. Il s’appuie sur des données déjà consolidées dans DuckDB, puis utilise un index vectoriel ChromaDB quand il est disponible.

## 2. Architecture

1. Indexation : [rag_engine/indexer.py](../rag_engine/indexer.py)
   - lit les données de [dbt_yeewde/models/marts/marts_supplier_kpi.sql](../dbt_yeewde/models/marts/marts_supplier_kpi.sql)
   - construit des documents texte lisibles par fournisseur
   - enregistre le vecteur dans [vector_db/chroma_data](../vector_db/chroma_data)

2. Retrieval : [rag_engine/retriever.py](../rag_engine/retriever.py)
   - essaye d’abord ChromaDB
   - si l’index est absent ou indisponible, bascule sur DuckDB
   - extrait automatiquement un identifiant fournisseur comme SUP004 pour améliorer la pertinence

3. Génération : [rag_engine/query.py](../rag_engine/query.py) et [rag_engine/generator.py](../rag_engine/generator.py)
   - utilise Groq quand la clé est configurée
   - sinon, renvoie un fallback local structuré et exploitable

4. Journalisation : [rag_engine/logging.py](../rag_engine/logging.py)
   - enregistre prompt, réponse, latence et nombre de documents
   - stocke les logs dans data/gold/rag_logs.duckdb

5. Évaluation : [rag_engine/evaluator.py](../rag_engine/evaluator.py)
   - vérifie si le retrieval renvoie bien du contexte utile

## 3. Données de référence

Le RAG s’appuie sur les tables Gold de la couche business :

- gold.marts_supplier_kpi
- gold.marts_otif_kpi

Ces tables contiennent notamment :

- fournisseur
- OTIF
- on_time_rate
- in_full_rate
- avg_delay_days
- max_delay_days
- critical_incidents
- total_incidents

## 4. Fallback local

Le fallback est important pour la robustesse du projet en local.

Il fonctionne ainsi :

- si ChromaDB manque, la requête est envoyée vers DuckDB
- si la question contient un fournisseur comme SUP004, une requête ciblée est faite sur ce fournisseur
- si la question est générale, la base retourne les fournisseurs les plus critiques / les moins performants

Cela garantit qu’une démo continue à tourner même sans clé Groq.

## 5. Configuration

Créer un fichier .env avec :

```bash
GROQ_API_KEY=votre_cle_ici
```

Sans clé, le projet reste fonctionnel en mode local avec le fallback métier.

## 6. Questions de test utiles

Voici des questions pertinentes pour vérifier le RAG :

```text
Quel est le niveau d’OTIF global ?
Quel est le risque fournisseur SUP004 ?
Pourquoi le fournisseur SUP004 a-t-il chuté ?
Quels fournisseurs ont le pire OTIF ?
Quels incidents qualité sont critiques ?
```

## 7. Validation rapide

```bash
python -m rag_engine.indexer
python -m rag_engine.evaluator
```

et pour le moteur complet :

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Puis tester l’endpoint :

```bash
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"question":"Pourquoi le fournisseur SUP004 a-t-il chuté ?"}'
```

## 8. Limites connues

- sans clé Groq, le système reste fonctionnel mais la réponse est structurelle et plus locale
- le mode local ne remplace pas un vrai LLM pour des synthèses très nuancées
- le retrieval est optimisé pour la business data, pas pour un grand corpus documentaire libre

## 9. En synthèse

Le RAG Yeewde est conçu pour rester utile même en environnement local :
- il restitue du contexte métier réel,
- il sait identifier les fournisseurs par leur ID,
- il garde un mode de secours fiable sans dépendre d’une API externe.

