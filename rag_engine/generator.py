"""
rag_engine/generator.py
Genere une explication en langage naturel via Groq (LLaMA 3.1 70B)
a partir du contexte recupere et du score de risque ML.
Usage : python -m rag_engine.generator
"""
import os
import time
from groq import Groq

from rag_engine.config import (
    GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE
)
from rag_engine.retriever import retrieve, retrieve_for_supplier
from rag_engine.logging import log_rag_call


SYSTEM_PROMPT = """Tu es Yeewde AI, un assistant expert en Supply Chain aerospatiale.
Tu analyses des donnees de performance fournisseur (KPI OTIF) et fournis des explications
claires, factuelles et actionnables en francais.
Reponds toujours de facon structuree : diagnostic, causes probables, recommandation."""


def _get_groq_client() -> Groq:
    """Instancie le client Groq en recupérant la cle de facon dynamique."""
    api_key = os.getenv("GROQ_API_KEY") or GROQ_API_KEY
    if not api_key or not api_key.strip():
        raise ValueError(
            "La cle GROQ_API_KEY est manquante ou vide. "
            "Definissez-la dans le fichier .env ou via $env:GROQ_API_KEY."
        )
    return Groq(api_key=api_key.strip())


def explain_po_risk(po_id: str, risk_result: dict, supplier_id: str = None) -> str:
    """
    Genere une explication RAG pour une commande a risque.
    """
    start = time.time()

    # -- Recuperation du contexte ----------------------------------------------
    if supplier_id:
        context_docs = retrieve_for_supplier(supplier_id)
        if not context_docs:
            context_docs = retrieve(
                f"fournisseur {supplier_id} performance OTIF retard risque"
            )
    else:
        context_docs = retrieve(
            f"commande {po_id} risque OTIF non livraison retard"
        )

    context = "\n\n".join(context_docs) if context_docs else "Pas de contexte disponible."

    # -- Construction du prompt ------------------------------------------------
    risk_pct = int(risk_result.get("risk_score", 0) * 100)
    otif_proba = int(risk_result.get("otif_proba", 0) * 100)
    risk_level = risk_result.get("risk_level", "INCONNU")

    user_prompt = f"""Analyse de la commande {po_id} :
- Score de risque Non-OTIF : {risk_pct}% (niveau : {risk_level})
- Probabilite de livraison OTIF : {otif_proba}%

Donnees historiques du fournisseur :
{context}

Explique en 3-4 phrases pourquoi cette commande est a risque et donne une recommandation concrete."""

    # -- Appel Groq ------------------------------------------------------------
    client = _get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=GROQ_MAX_TOKENS,
        temperature=GROQ_TEMPERATURE,
    )

    explanation = response.choices[0].message.content
    latency_ms = (time.time() - start) * 1000
    tokens_used = response.usage.total_tokens if response.usage else 0

    # -- Log ------------------------------------------------------------------
    log_rag_call(
        prompt=user_prompt,
        response=explanation,
        latency_ms=latency_ms,
        tokens_used=tokens_used,
        retrieved_docs=context_docs,
    )

    return explanation


def chat(question: str) -> str:
    """
    Interface de chat libre sur les donnees Supply Chain.
    """
    start = time.time()
    context_docs = retrieve(question)
    context = "\n\n".join(context_docs) if context_docs else "Pas de contexte disponible."

    user_prompt = f"""Question : {question}

Contexte disponible :
{context}

Reponds de facon claire et factuelle en t'appuyant sur le contexte."""

    client = _get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=GROQ_MAX_TOKENS,
        temperature=GROQ_TEMPERATURE,
    )

    answer = response.choices[0].message.content
    latency_ms = (time.time() - start) * 1000
    tokens_used = response.usage.total_tokens if response.usage else 0

    log_rag_call(
        prompt=user_prompt,
        response=answer,
        latency_ms=latency_ms,
        tokens_used=tokens_used,
        retrieved_docs=context_docs,
    )

    return answer


if __name__ == "__main__":
    print("Test du generateur RAG...")
    answer = chat("Quels sont les fournisseurs avec le taux OTIF le plus bas ?")
    print("\nReponse :")
    print(answer)