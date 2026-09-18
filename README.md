# 👁️ Yeewde AI — Plateforme DataOps & Système RAG pour la Supply Chain Aérospatiale

> **Yeewde** *(Pulaar : "voir / observer")* — Yeewde AI est une tour de contrôle décisionnelle qui **voit** la Supply Chain avant qu'elle ne dérape : monitoring descriptif, prédictif et explicable du KPI OTIF.

> **Sujet de mémoire :** *Conception d'un pipeline DataOps et d'un système RAG pour le monitoring prédictif et l'explicabilité de l'OTIF en Supply Chain*
> **Contexte :** Master 2 GDIL (Gestion des Données et Ingénierie Logicielle) — Université Gaston Berger (UGB), Sénégal

[![Architecture](https://img.shields.io/badge/Architecture-Medallion-blue.svg)](#-architecture-technique-local-first)
[![Orchestration](https://img.shields.io/badge/Orchestration-Dagster-0ea5e9.svg)](#-orchestration-dagster)
[![Stack](https://img.shields.io/badge/Stack-DuckDB%20%7C%20dbt%20%7C%20FastAPI%20%7C%20Streamlit-green.svg)](#-stack-technique)
[![MLOps](https://img.shields.io/badge/MLOps-MLflow-0194E2.svg)](#-module-prédictif--mlops)
[![DataQuality](https://img.shields.io/badge/Data%20Quality-dbt--expectations%20%7C%20Elementary-9146ff.svg)](#-data-quality--observabilité-dbt)
[![Drift](https://img.shields.io/badge/Drift%20Monitoring-Evidently%20AI-ff5722.svg)](#-drift-monitoring-evidently-ai)
[![LLM](https://img.shields.io/badge/AI-LangChain%20%7C%20ChromaDB%20%7C%20Groq-orange.svg)](#-module-explicabilité--rag)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black.svg)](#-cicd--gouvernance-dataops)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#-auteur--licence)

---

## 📖 Table des matières

1. [Présentation](#-présentation-du-projet)
2. [Pourquoi "Yeewde"](#-pourquoi-yeewde)
3. [Le problème métier : l'OTIF](#-le-problème-métier--lotif)
4. [Sources de données](#-sources-de-données)
5. [⛔ Scope figé — ce qui N'EST PAS dans Yeewde](#-scope-figé--ce-qui-nest-pas-dans-yeewde)
6. [Architecture technique (local-first)](#-architecture-technique-local-first)
7. [Architecture cible (production/cloud, documentée seulement)](#-architecture-cible-productioncloud-documentée-seulement)
8. [Stack technique](#-stack-technique)
9. [Environnements à installer](#-environnements-à-installer)
10. [Structure du projet](#-structure-du-projet)
11. [Orchestration Dagster](#-orchestration-dagster)
12. [Data Quality & Observabilité dbt](#-data-quality--observabilité-dbt)
13. [Module Prédictif & MLOps](#-module-prédictif--mlops)
14. [Drift Monitoring (Evidently AI)](#-drift-monitoring-evidently-ai)
15. [Module Explicabilité & RAG](#-module-explicabilité--rag)
16. [API & Cockpit](#-api--cockpit)
17. [CI/CD & Gouvernance DataOps](#-cicd--gouvernance-dataops)
18. [🗓️ Feuille de route par phases](#️-feuille-de-route-par-phases)
19. [Démarrage rapide](#-démarrage-rapide)
20. [Tests](#-tests)
21. [Limites & Perspectives](#-limites--perspectives)
22. [Glossaire](#-glossaire)
23. [Auteur & Licence](#-auteur--licence)

---

## 📌 Présentation du Projet

**Yeewde AI** est une **Plateforme DataOps & Système RAG** conçue pour la Supply Chain aérospatiale. Elle applique les principes du **DataOps** (architecture Medallion, transformations déclaratives via dbt, orchestration via Dagster, tests, CI/CD) combinés à du **MLOps** (MLflow, monitoring de dérive) pour la prédiction, et à l'**IA Générative (RAG)** pour l'explicabilité, dans le but d'automatiser la détection, la prédiction et l'explication des défaillances du KPI **OTIF (On-Time In-Full)**.

**Objectif métier :** passer d'un pilotage réactif — *"le KPI OTIF a chuté"* — à un pilotage **prédictif et explicable** — *"le KPI OTIF risque de chuter la semaine prochaine sur le fournisseur X, avec 82% de confiance, car son taux de retard historique atteint 18% et 3 commandes critiques sont en cours ; recommandation : augmenter le stock de sécurité."*

Le système répond à quatre questions, dans cet ordre :

| Question | Couche qui répond | Techno |
|---|---|---|
| **Que s'est-il passé ?** (descriptif) | Moteur Analytique | dbt + DuckDB |
| **Que va-t-il se passer ?** (prédictif) | Moteur Prédictif | LightGBM + MLflow |
| **Pourquoi cela va-t-il se passer ?** (explicatif) | Feature importance + RAG | LangChain + Groq + ChromaDB |
| **Le système est-il toujours fiable ?** (méta-monitoring) | Data Quality + Drift Monitoring | Elementary + Evidently AI |

> 🎯 **Choix d'architecture assumé :** Yeewde privilégie la **fiabilité d'exécution** à la sophistication d'infrastructure. Tout tourne en local, sans Docker, sans cloud, sauf l'appel API Groq pour le RAG. Ce choix garantit un système démontrable de bout en bout sur une machine standard (16 Go RAM), avec une architecture cible cloud **documentée** en perspective, jamais implémentée prématurément.

---

## 🗣️ Pourquoi "Yeewde"

Le nom du projet vient du **Pulaar** (langue parlée notamment dans le nord du Sénégal), où *yeewde* signifie **"voir", "observer", "veiller sur"**. C'est exactement la fonction d'une Control Tower : elle ne se contente pas d'afficher des chiffres, elle **surveille activement**, **anticipe** les problèmes et **explique** ce qu'elle observe.

---

## 🎯 Le problème métier : l'OTIF

**OTIF (On-Time In-Full)** mesure le pourcentage de commandes livrées :
- **On Time** — à la date promise ou avant,
- **In Full** — avec la quantité complète commandée.

```
OTIF = (Commandes livrées à temps ET en quantité complète) / (Total des commandes)
```

Dans l'aérospatial, un OTIF faible a des conséquences en cascade : retards de production, pénalités contractuelles, risques de non-conformité réglementaire. **Prédire** une rupture avant qu'elle ne survienne — plutôt que de la constater après coup — est la valeur ajoutée centrale de ce projet.

---

## 📊 Sources de données

4 tables réelles, reliées par des clés communes (`part_id`, `supplier_id`, `site_id`, `po_id`) :

| Fichier | Volume | Rôle | Colonnes clés |
|---|---|---|---|
| `parts_master.csv` | ~300 lignes | Référentiel pièces | `part_id`, `part_family`, `criticality_class`, `unit_cost`, `lead_time_days`, `supplier_id_primary`, `supplier_risk_class`, `is_repairable`, `shelf_life_days` |
| `purchase_orders.csv` | ~29 666 lignes | **Base du calcul OTIF** | `po_id`, `supplier_id`, `site_id`, `part_id`, `order_date`, `promised_date`, `receipt_date`, `ordered_qty`, `received_qty` |
| `quality_incidents.csv` | ~369 lignes | **Contexte texte pour le RAG** | `incident_id`, `incident_date`, `part_id`, `supplier_id`, `site_id`, `defect_severity`, `defect_type`, `scrap_qty` |
| `supply_chain_history.csv` | ~280 801 lignes | **Source principale de features ML** | `date`, `site_id`, `part_id`, `planned_maintenance`, `consumption_qty`, `on_hand_qty`, `backorder_qty`, `blocked_qty`, `forecast_qty`, `forecast_type`, `forecast_uplift_pct` |

**Volume total : ~17 Mo, ~311 000 lignes** — DuckDB en local suffit largement.

### Simulateur de flux "vivant"

Ces 4 fichiers sont figés (2022–2024). Un générateur complémentaire (`simulate_live_feed.py`) injecte périodiquement de **nouvelles commandes "en cours"** (sans `receipt_date`), basées sur les distributions statistiques réelles — ce sont ces commandes que le modèle prédictif score, et que le drift monitoring compare aux données d'entraînement.

> ⚠️ Cette distinction (réel vs simulé) est documentée explicitement dans le mémoire.

---

## ⛔ Scope figé — ce qui N'EST PAS dans Yeewde

Cette section existe pour ne plus revenir sur ces choix. Toute nouvelle suggestion d'outil doit être confrontée à cette liste avant d'être considérée.

| Outil écarté | Pourquoi |
|---|---|
| **Docker / Docker Compose / Devcontainers** | Sature la RAM (16 Go), ajoute un point de défaillance réseau/config le jour de la démo |
| **MinIO** | DuckDB + Parquet local couvre déjà le besoin de stockage à ce volume (17 Mo) |
| **Kubernetes** | Aucune raison d'orchestrer des conteneurs pour un pipeline solo en local |
| **Terraform** | Provisionnerait un cloud jamais déployé — travail sans objet réel dans ce mémoire |
| **Argo CD / GitOps** | Nécessite un cluster Kubernetes, qui n'existe pas dans ce projet |
| **Prometheus / Grafana** | Observabilité système pensée pour de la prod à fort trafic, pas un POC solo |
| **LangFuse / Arize Phoenix** | Nouveau service externe, nouvelle dépendance réseau ; le logging RAG maison (DuckDB) suffit au volume d'un mémoire |
| **Great Expectations (standalone)** | `dbt-expectations` donne 90% de la valeur sans nouvel outil séparé |
| **MLflow Model Registry distribué** | Le Tracking local (SQLite) suffit ; le Registry est documenté en architecture cible seulement |

**Règle à partir de maintenant : si un outil a besoin d'un cluster, d'un serveur dédié, d'un compte cloud payant, ou d'un conteneur supplémentaire pour exister, il n'entre pas dans Yeewde.**

---

## 🏗️ Architecture Technique (Local-First)

Architecture **implémentée et démontrée** — celle qui tourne réellement sur votre machine.

```text
┌────────────────────────────────────────────────────────────────────┐
│                  GITHUB ACTIONS & CI/CD                             │
│  • dbt test + dbt-expectations (qualité des données)                │
│  • Linting Python                                                    │
│  • Tests API (FastAPI)                                               │
│  Déclenché à chaque push / pull request                             │
└───────────────────────────────┬───────────────────────────────────────┘
                                │ valide & sécurise
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                    DAGSTER ORCHESTRATOR (UI)                        │
│  Assets : Ingestion ➔ dbt (Silver/Gold) ➔ ML Training ➔            │
│           Drift Check ➔ RAG Index                                   │
│  • Dépendances explicites, logs centralisés (dagster dev, local)    │
└───────────────┬─────────────────────────────┬─────────────────────────┘
                │                             │
                ▼                             ▼
   ┌─────────────────────┐        ┌───────────────────────┐
   │  COUCHE MEDALLION     │        │   MOTEUR PRÉDICTIF     │
   │  (DuckDB + Parquet)   │        │   LightGBM             │
   │                       │───────▶│                        │
   │  🥇 Gold : KPI OTIF   │features│  → score de risque     │
   │      + features ML   │        │  → feature importance  │
   │  🥈 Silver : Cleaning │        └──────────┬─────────────┘
   │  🥉 Bronze : 4 CSV    │                   │ log runs
   │     ERP + flux simulé │                   ▼
   │                       │        ┌───────────────────────┐
   │  ✅ dbt-expectations  │        │  MLflow Tracking        │
   │  ✅ Elementary Data   │        │  (local, SQLite)        │
   │     (dashboard, tests │        └──────────┬────────────┘
   │      anomalie, lineage)│                  │
   └───────────┬───────────┘                   ▼
              │                    ┌───────────────────────┐
              │                    │  Evidently AI            │
              │                    │  Drift Monitoring        │
              │                    └──────────┬────────────┘
              │ contextes métier               │ alerte si dérive
              ▼                               ▼ (widget Streamlit)
   ┌─────────────────────────────────────────┐
   │        MOTEUR RAG & EXPLICABILITÉ        │
   │   ChromaDB (vector store) + LangChain    │
   │   + Groq API (Llama 3)                   │
   │   + Logging maison → DuckDB               │
   │     (latence, tokens, retrieval)          │
   └───────────────────┬───────────────────────┘
                       ▼
   ┌─────────────────────────────────────────┐
   │     API Backend — FastAPI                │
   │  /kpi  /predict  /explain  /chat  /drift │
   └───────────────────┬───────────────────────┘
                       ▼
   ┌─────────────────────────────────────────┐
   │     Cockpit — Streamlit                   │
   │  KPI OTIF • Scores de risque •            │
   │  Feature importance • Chat RAG •          │
   │  Alerte drift • Dashboard Elementary       │
   └─────────────────────────────────────────┘
```

### Flux de données détaillé

1. **Ingestion** (asset Dagster) — Les 4 CSV ERP chargés en Parquet local → **Bronze**.
2. **Silver** (asset Dagster → dbt) — Nettoyage, typage, déduplication, validés par `dbt-expectations`.
3. **Gold** (dbt) — KPI OTIF réel, features ML, contextes RAG — le tout surveillé par **Elementary** (dashboard de santé, détection d'anomalies de volumétrie).
4. **Entraînement** (asset Dagster) — LightGBM entraîné, chaque run loggé dans **MLflow**.
5. **Scoring** — Score de risque par commande, y compris pour les commandes "en cours" simulées.
6. **Drift Check** (asset Dagster) — Evidently AI compare nouvelles commandes vs données d'entraînement.
7. **Indexation** (asset Dagster) — Contextes vectorisés dans ChromaDB.
8. **RAG** — FastAPI orchestre LangChain + Groq, chaque appel journalisé (latence, tokens, retrieval).
9. **Cockpit** — Streamlit affiche tout, y compris les 3 indicateurs de confiance (Data Health / Model Health / RAG Health).

---

## ☁️ Architecture Cible (Production/Cloud, documentée seulement)

**Non implémentée. Présentée en soutenance comme trajectoire de montée en charge, pas comme réalisation.**

```text
DuckDB local          → BigQuery / Snowflake / Databricks
Dagster dev (local)   → Dagster Cloud
MLflow SQLite local   → MLflow Server (PostgreSQL + S3), Model Registry
Parquet local         → Data lake objet (S3 / GCS)
Logging RAG maison    → LangFuse / Arize Phoenix (si volume le justifie)
Pas d'authentification → SSO / gestion des rôles
Batch quotidien        → Kafka en amont de Bronze
(non testé)            → Terraform (IaC), Kubernetes, Argo CD (GitOps),
                          Prometheus/Grafana (observabilité système)
```

> **Analogie à utiliser en soutenance :** *"Le local-first n'est pas une architecture 'moins bonne' que le cloud — c'est l'architecture appropriée pour un POC académique à ce volume de données (17 Mo). Utiliser BigQuery ou Kubernetes ici serait analogue à utiliser un camion pour transporter un sac à dos : fonctionnel, mais disproportionné."* Ne jamais présenter cette section comme implémentée.

---

## 🧰 Stack Technique

| Couche | Technologie | Statut |
|---|---|---|
| Stockage & Traitement | **DuckDB**, Parquet | ✅ Implémenté |
| Transformation | dbt Core | ✅ Implémenté |
| Data Quality | **dbt-expectations** | ✅ Implémenté |
| Observabilité dbt | **Elementary Data** | ✅ Implémenté (Phase 4) |
| Orchestration | **Dagster** (`dagster dev`) | ✅ Implémenté |
| Machine Learning | LightGBM | ✅ Implémenté |
| MLOps Tracking | MLflow (SQLite local) | ✅ Implémenté |
| Drift Monitoring | **Evidently AI** | ✅ Implémenté (Phase 3) |
| IA Générative / RAG | LangChain, Groq API (Llama 3), ChromaDB | ✅ Implémenté |
| RAG Observability | Logging maison (DuckDB) | ✅ Implémenté |
| API Backend | FastAPI | ✅ Implémenté |
| Interface / Cockpit | Streamlit, Plotly | ✅ Implémenté |
| CI/CD | GitHub Actions | ✅ Implémenté |
| Ingestion avancée | dlt | 🟡 Bonus optionnel, fin de projet |
| Langage | Python 3.12 | ✅ Implémenté (testé, installation validée) |

---

## 💻 Environnements à installer

**Tout tourne en local, dans un seul environnement virtuel Python. Aucun compte cloud payant requis.**

### 1. Outils système (une seule fois)

| Outil | Version | Vérifier avec |
|---|---|---|
| Python | **3.12** (recommandé et testé) | `python --version` dans le `.venv` activé. Python 3.13 peut poser des soucis de compatibilité de wheels précompilés (LightGBM, ChromaDB) sous Windows : en cas d'échec `pip install`, recréer le venv avec `py -3.12 -m venv .venv` |
| Git | Récent | `git --version` |
| Un éditeur/IDE | VS Code ou Claude Code (recommandé) | — |

### 2. Compte et clé API (gratuit)

| Service | Pourquoi | Où l'obtenir |
|---|---|---|
| **Groq** | Génération RAG (Llama 3) | `console.groq.com` → créer une clé API, tier gratuit |
| **GitHub** | Repo, portfolio, GitHub Actions | Compte déjà probablement existant |

### 3. Installation du projet

```bash
# Cloner le repo
git clone https://github.com/yourname/yeewde.git
cd yeewde

# Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Installer toutes les dépendances Python en une fois
pip install -r requirements.txt
```

### 4. Contenu de `requirements.txt`

```text
# Data & transformation
duckdb
dbt-core
dbt-duckdb
dbt-expectations
elementary-data

# Orchestration
dagster
dagster-webserver

# Machine Learning & MLOps
lightgbm
scikit-learn
mlflow
evidently

# RAG / IA Générative
langchain
langchain-groq
langchain-community
chromadb

# API & Cockpit
fastapi
uvicorn
streamlit
plotly

# Utilitaires
pandas
python-dotenv
pytest
flake8
```

### 5. Configuration de la clé API

```bash
cp .env.example .env
# Ouvrir .env et renseigner :
# GROQ_API_KEY=votre_clé_ici
```

### 6. Vérification que tout est bien installé

```bash
dbt --version
dagster --version
mlflow --version
python -c "import lightgbm, evidently, chromadb; print('OK')"
```

> ✅ **Aucun Docker, aucun cluster, aucune carte bancaire requise.** Si une de ces installations échoue, c'est un problème d'environnement Python local à corriger avant d'avancer — pas un signe qu'il faut ajouter de l'infrastructure supplémentaire.

---

## 📂 Structure du Projet

```text
yeewde/
├── requirements.txt
├── .env.example
├── .env                          # (exclu git)
├── .gitignore
├── README.md
├── LICENSE
│
├── .github/workflows/
│   ├── dbt-test.yml
│   ├── lint.yml
│   └── api-tests.yml
│
├── data_sources/
│   ├── raw_erp/
│   │   ├── parts_master.csv
│   │   ├── purchase_orders.csv
│   │   ├── quality_incidents.csv
│   │   └── supply_chain_history.csv
│   ├── ingest_erp_extract.py
│   └── simulate_live_feed.py
│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/                     # inclut rag_logs.duckdb
│
├── dagster_orchestrator/
│   ├── definitions.py
│   └── assets/
│       ├── ingestion.py
│       ├── dbt_assets.py
│       ├── ml_assets.py
│       ├── drift_assets.py
│       └── rag_assets.py
│
├── dbt_yeewde/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── packages.yml               # dbt-expectations + elementary
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── tests/
│
├── ml_engine/
│   ├── config.py
│   ├── feature_engineering.py
│   ├── train.py                   # LightGBM
│   ├── evaluate.py                # Métriques + comparaison baseline
│   ├── predict.py                 # Scoring des commandes en cours
│   ├── explainability.py          # Feature importance
│   └── drift_monitor.py           # Evidently AI
│
├── mlruns/                        # Tracking store MLflow (auto-généré)
│
├── rag_engine/
│   ├── config.py
│   ├── indexer.py                 # Chunking + embeddings (quality_incidents)
│   ├── retriever.py                # Recherche ChromaDB
│   ├── generator.py                # Appel LLM via Groq
│   ├── evaluator.py                # Évaluation RAG (bonus Phase 4, si le temps permet)
│   └── logging.py                  # Traçabilité des requêtes (DuckDB)
│
├── vector_db/
│   └── chroma_data/
│
├── monitoring/
│   └── pipeline_health.py         # Agrège Elementary + Evidently + logs RAG pour le cockpit
│
├── backend/
│   ├── main.py
│   └── database.py
│
├── frontend/
│   ├── app.py
│   └── components/
│       ├── kpi_cards.py
│       ├── prediction_widgets.py
│       ├── rag_chatbot.py
│       ├── feature_importance_plot.py
│       └── drift_widget.py
│
├── tests/
│   ├── test_pipeline_e2e.py
│   ├── test_data_quality.py
│   ├── test_ml.py
│   └── test_api.py
│
├── docs/
│   ├── ARCHITECTURE_CIBLE.md      # perspective cloud/IaC, documentation seulement
│   ├── DATA_DICTIONARY.md         # dictionnaire des 4 CSV réels
│   ├── MODEL_CARD.md              # fiche modèle : hyperparamètres, métriques, limites
│   └── RAG_DOCUMENTATION.md       # documentation du pipeline RAG
│
└── scripts/
    └── setup_local_env.sh
```

---

## 🚀 Orchestration Dagster

```python
# dagster_orchestrator/assets/ml_assets.py
from dagster import asset
import os

@asset
def ingestion_bronze():
    os.system("python data_sources/ingest_erp_extract.py")

@asset(deps=["ingestion_bronze"])
def dbt_gold_marts():
    os.system("dbt run --project-dir dbt_yeewde")
    os.system("dbt test --project-dir dbt_yeewde")

@asset(deps=["dbt_gold_marts"])
def train_lightgbm_model():
    os.system("python ml_engine/train.py")

@asset(deps=["train_lightgbm_model"])
def check_data_drift():
    os.system("python ml_engine/drift_monitor.py")

@asset(deps=["dbt_gold_marts"])
def index_rag_context():
    os.system("python rag_engine/indexer.py")
```

---

## ✅ Data Quality & Observabilité dbt

**`dbt-expectations`** pour des tests précis, **Elementary Data** pour le dashboard global et la détection d'anomalies — les deux sont des packages dbt natifs, sans nouveau service à héberger.

```yaml
# dbt_yeewde/packages.yml
packages:
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.11.0"]
  - package: elementary-data/elementary
    version: [">=0.15.0", "<0.16.0"]
```

```yaml
# dbt_yeewde/models/marts/schema.yml
models:
  - name: marts_otif_kpi
    columns:
      - name: otif_score
        tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 1
      - name: promised_date
        tests:
          - dbt_expectations.expect_column_values_to_not_be_null
```

```bash
# Après chaque dbt run/test, générer le rapport Elementary
edr monitor report --project-dir dbt_yeewde
```

---

## 🔮 Module Prédictif & MLOps

```python
# ml_engine/train.py (extrait)
import mlflow
import mlflow.lightgbm
from sklearn.metrics import roc_auc_score, precision_score, recall_score

mlflow.set_tracking_uri("./mlruns")
mlflow.set_experiment("otif-risk-prediction")

with mlflow.start_run(description="LightGBM OTIF risk classifier"):
    mlflow.log_params(LGB_PARAMS)
    model = train_lgb_model(X_train, y_train)

    y_pred = model.predict(X_test)
    mlflow.log_metric("auc", roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
    mlflow.log_metric("precision", precision_score(y_test, y_pred))
    mlflow.log_metric("recall", recall_score(y_test, y_pred))

    mlflow.lightgbm.log_model(model, "model")
```

---

## 📉 Drift Monitoring (Evidently AI)

```python
# ml_engine/drift_monitor.py
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def check_drift(reference_data, current_data):
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_data, current_data=current_data)
    result = report.as_dict()
    return {
        "drift_detected": result["metrics"][0]["result"]["dataset_drift"],
        "drift_share": result["metrics"][0]["result"]["drift_share"],
    }
```

> 📌 Codé en **Phase 3**, une fois le pipeline de base et le simulateur de flux stables.

---

## 💬 Module Explicabilité & RAG

```python
# rag_engine/retriever.py (extrait)
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
import time
from rag_engine.logging import log_rag_call

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
vectorstore = Chroma(persist_directory="./vector_db/chroma_data")

def explain_risk(supplier_id: str, risk_score: float, question: str) -> str:
    start = time.time()
    context_docs = vectorstore.similarity_search(
        f"incidents et historique fournisseur {supplier_id}", k=5
    )
    context = "\n".join([doc.page_content for doc in context_docs])
    prompt = f"""Score de risque OTIF pour {supplier_id} : {risk_score:.0%}.
Contexte historique : {context}
Question : {question}
Réponds en langage clair et actionnable."""

    response = llm.invoke(prompt).content
    latency_ms = (time.time() - start) * 1000
    log_rag_call(prompt, response, latency_ms, tokens_used=len(prompt.split()), retrieved_docs=context_docs)
    return response
```

```python
# rag_engine/logging.py
import time
import duckdb

def log_rag_call(prompt, response, latency_ms, tokens_used, retrieved_docs):
    conn = duckdb.connect("data/gold/rag_logs.duckdb")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rag_logs (
            ts DOUBLE, prompt TEXT, response TEXT,
            latency_ms DOUBLE, tokens_used INT, docs_retrieved INT
        )
    """)
    conn.execute("INSERT INTO rag_logs VALUES (?, ?, ?, ?, ?, ?)",
                  [time.time(), prompt, response, latency_ms, tokens_used, len(retrieved_docs)])
```

---

## 🌐 API & Cockpit

| Endpoint | Méthode | Rôle |
|---|---|---|
| `/kpi/otif` | GET | KPI OTIF global et par fournisseur |
| `/predict/{po_id}` | GET | Score de risque pour une commande |
| `/explain/{po_id}` | GET | Feature importance + explication RAG |
| `/chat` | POST | Question libre au moteur RAG |
| `/drift/status` | GET | Statut de dérive des données |

**Pages Streamlit :** KPI OTIF · Prédictions · Explications · Monitoring (drift + lien MLflow + dashboard Elementary).

---

## ⚙️ CI/CD & Gouvernance DataOps

| Pilier | Mise en œuvre |
|---|---|
| **Automatisation** | Dagster orchestre tout le pipeline sans intervention manuelle |
| **CI/CD** | GitHub Actions : dbt test + dbt-expectations, linting, tests API |
| **Qualité des données** | dbt-expectations + Elementary |
| **Observabilité** | UI Dagster, MLflow, Evidently, Elementary, logging RAG |

```yaml
# .github/workflows/dbt-test.yml
name: DataOps Quality Checks
on: [push, pull_request]
jobs:
  dbt-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: dbt deps --project-dir dbt_yeewde
      - run: dbt test --project-dir dbt_yeewde
```

---

## 🗓️ Feuille de route par phases

**Règle d'or : ne jamais démarrer une phase avant que la précédente tourne de bout en bout. Ne jamais ajouter un outil hors de la liste "Scope figé" ci-dessus.**

| Phase | Semaines indicatives | Contenu | Objectif |
|---|---|---|---|
| **1 — Fondations** | 1-3 | Ingestion des 4 CSV, dbt Bronze→Silver→Gold, KPI OTIF réel calculé | Un pipeline simple qui tourne, données visibles |
| **2 — MVP end-to-end** | 4-7 | Un modèle ML simple + un RAG basique connecté | Chemin complet fonctionnel, CSV → explication RAG |
| **3 — Enrichissement** | 8-12 | Dagster propre, MLflow, LightGBM finalisé, **Evidently AI** | Sophistication sur un socle déjà stable |
| **4 — Robustesse** | 13-15 | CI/CD GitHub Actions, tests, **Elementary Data**, logging RAG, UI soignée | Fiabilisation avant démo |
| **5 — Rédaction mémoire** | 13-18 (parallèle) | Rédaction continue, pas en fin de parcours | Ne pas tout écrire en 3 semaines |
| **6 — Finalisation** | 16-19 | Relecture, polish démo, slides, répétitions orales | Prêt pour la soutenance |
| **Marge de sécurité** | 20 | Buffer imprévus | — |

**Action immédiate : ouvrir Claude Code, commencer la Phase 1. Plus aucune décision d'architecture à prendre avant que ça tourne.**

---

## 🚀 Démarrage Rapide

```bash
# 1. Cloner & installer (voir section Environnements ci-dessus pour le détail)
git clone https://github.com/yourname/yeewde.git
cd yeewde
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configurer la clé Groq
cp .env.example .env

# 3. Placer les 4 CSV ERP dans data_sources/raw_erp/

# 4. Installer les packages dbt
dbt deps --project-dir dbt_yeewde

# 5. Lancer Dagster
dagster dev -f dagster_orchestrator/definitions.py
# → http://localhost:3000

# 6. (Optionnel démo) Injecter de nouvelles commandes
python data_sources/simulate_live_feed.py --n 15

# 7. Lancer l'API et le cockpit
uvicorn backend.main:app --reload &
streamlit run frontend/app.py
```

---

## 🧪 Tests

| Type | Commande |
|---|---|
| Qualité des données | `dbt test --project-dir dbt_yeewde` |
| Pipeline end-to-end | `pytest tests/test_pipeline_e2e.py` |
| API FastAPI | `pytest backend/tests/` |
| Linting | `flake8 ml_engine/ backend/ frontend/ rag_engine/` |

---

## ⚠️ Limites & Perspectives

- **Local-first, pas production-scale** — trajectoire de montée en charge documentée, non implémentée.
- **Données historiques figées (2022–2024)** — flux "temps réel" simulé statistiquement.
- **Batch, pas de flux continu** — Kafka serait nécessaire pour du vrai temps réel.
- **Pas d'authentification** sur le cockpit.
- **Performance prédictive à interpréter avec prudence** — classes déséquilibrées (ruptures rares).
- **RAG Observability simplifiée** — logging maison, pas dimensionné pour de la production à fort trafic.
- **Dépendance réseau unique et identifiée** — seul l'appel Groq nécessite internet.

---

## 📘 Glossaire

| Terme | Définition |
|---|---|
| **OTIF** | On-Time In-Full |
| **Medallion Architecture** | Bronze (brut) / Silver (nettoyé) / Gold (analytique) |
| **DataOps** | Principes DevOps appliqués au cycle de vie de la donnée |
| **MLOps** | Principes DevOps appliqués à la gouvernance des modèles ML |
| **RAG** | Retrieval-Augmented Generation |
| **Data Drift** | Dérive statistique entre données d'entraînement et données observées |
| **Local-first** | Architecture qui privilégie l'exécution locale avant toute dépendance cloud |

---

## 👤 Auteur & Licence

Projet réalisé dans le cadre du Master 2 GDIL — Université Gaston Berger (UGB), Sénégal.
Distribué sous licence MIT.