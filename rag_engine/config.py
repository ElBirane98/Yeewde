"""
rag_engine/config.py
Configuration centralisee pour le moteur RAG.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent

# -- ChromaDB ------------------------------------------------------------------
CHROMA_DIR = str(ROOT / "vector_db" / "chroma_data")
CHROMA_COLLECTION = "yeewde_supply_chain"

# -- Embedding -----------------------------------------------------------------
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # local, rapide, ~80MB
N_RESULTS = 5                            # docs recuperes par requete

# -- LLM Groq ------------------------------------------------------------------
# os.getenv cherche le nom de la variable d'environnement 'GROQ_API_KEY'
# Remplacez la valeur en dur par la lecture depuis l'environnement
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
GROQ_MODEL = "openai/gpt-oss-120b"     # Modèle actif validé sur votre compte
GROQ_MAX_TOKENS = 2048
GROQ_TEMPERATURE = 0.5

# -- Logging RAG ---------------------------------------------------------------
RAG_LOG_DB = str(ROOT / "data" / "gold" / "rag_logs.duckdb")