"""
Moteur RAG pour Yeewde AI - Interrogation LLM via Groq API
"""

from __future__ import annotations

import os
import re

import duckdb
from dotenv import load_dotenv

from ml_engine.config import DUCKDB_PATH
from rag_engine.retriever import extract_supplier_id, retrieve, retrieve_for_supplier

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_MAX_TOKENS = 2048
GROQ_TEMPERATURE = 0.5


def _classify_question(user_query: str) -> str:
    """Détermine le type de question métier pour ajuster le fallback."""
    text = (user_query or "").lower()
    if re.search(r"\b(supplier|fournisseur|sup\d+)\b", text):
        return "supplier"
    if "incident" in text or "qualit" in text or "défaut" in text or "non conforme" in text:
        return "incident"
    if "commande" in text or "po" in text or "ordre" in text:
        return "order"
    if "otif" in text or "livraison" in text or "retard" in text:
        return "otif"
    return "general"


def _build_db_backed_fallback(user_query: str, docs: list[str] | None = None) -> str:
    """Prépare une réponse métier à partir des KPIs réels de DuckDB."""
    supplier_id = extract_supplier_id(user_query)
    question_type = _classify_question(user_query)
    context = "\n- ".join(doc for doc in (docs or []) if doc and doc.strip())

    try:
        with duckdb.connect(str(DUCKDB_PATH), read_only=True) as conn:
            if supplier_id:
                row = conn.execute(
                    """
                    SELECT supplier_id, supplier_risk_class, otif_rate, on_time_rate, in_full_rate,
                           avg_delay_days, max_delay_days, total_incidents, critical_incidents, total_orders
                    FROM gold.marts_supplier_kpi
                    WHERE lower(supplier_id) = lower(?)
                    LIMIT 1
                    """,
                    [supplier_id],
                ).fetchone()
                if row:
                    (
                        supplier_id_db,
                        risk_class,
                        otif_rate,
                        on_time_rate,
                        in_full_rate,
                        avg_delay_days,
                        max_delay_days,
                        total_incidents,
                        critical_incidents,
                        total_orders,
                    ) = row
                    return (
                        f"⚠️ Clé GROQ_API_KEY non configurée. Fallback local basé sur DuckDB pour {supplier_id_db}.\n\n"
                        f"- Classe de risque : {risk_class}\n"
                        f"- OTIF : {float(otif_rate or 0):.1%}\n"
                        f"- Livraison à temps : {float(on_time_rate or 0):.1%}\n"
                        f"- Quantité complète : {float(in_full_rate or 0):.1%}\n"
                        f"- Délai moyen : {float(avg_delay_days or 0):.1f} jours\n"
                        f"- Retard max : {float(max_delay_days or 0):.1f} jours\n"
                        f"- Incidents : {int(total_incidents or 0)} (critiques : {int(critical_incidents or 0)})\n"
                        f"- Commandes : {int(total_orders or 0)}\n\n"
                        "Diagnostic : la performance du fournisseur est évaluée sur OTIF, délais, incidents et cohérence de livraison. "
                        "Les écarts de risque viennent généralement d’une accumulation de retards ou d’incidents qualité."
                    )

            if question_type in {"otif", "general"}:
                row = conn.execute(
                    """
                    SELECT AVG(otif_score) AS global_otif,
                           AVG(CASE WHEN is_on_time THEN 1.0 ELSE 0.0 END) AS on_time_rate,
                           AVG(CASE WHEN is_in_full THEN 1.0 ELSE 0.0 END) AS in_full_rate,
                           COUNT(*) AS total_orders
                    FROM gold.marts_otif_kpi
                    WHERE otif_score IS NOT NULL
                    """
                ).fetchone()
                if row and row[0] is not None:
                    global_otif, on_time_rate, in_full_rate, total_orders = row
                    return (
                        "⚠️ Clé GROQ_API_KEY non configurée. Fallback local basé sur les KPI Gold.\n\n"
                        f"- OTIF global : {float(global_otif or 0):.1%}\n"
                        f"- Livraison à temps : {float(on_time_rate or 0):.1%}\n"
                        f"- Quantité complète : {float(in_full_rate or 0):.1%}\n"
                        f"- Commandes analysées : {int(total_orders or 0)}\n\n"
                        "Diagnostic : le niveau de performance global doit être évalué à partir du vrai OTIF métier et non via une moyenne de 3 fournisseurs isolés. "
                        "Les écarts les plus sensibles se concentrent sur les fournisseurs à forte criticité et forte variabilité de délais."
                    )

            if row := conn.execute(
                """
                SELECT supplier_id, supplier_risk_class, otif_rate, avg_delay_days, total_incidents, critical_incidents
                FROM gold.marts_supplier_kpi
                ORDER BY otif_rate ASC NULLS LAST
                LIMIT 5
                """
            ).fetchall():
                items = "\n- ".join(
                    f"{supplier_id} | risque {risk_class} | OTIF {float(otif_rate or 0):.1%} | délai {float(avg_delay_days or 0):.1f}j | incidents {int(total_incidents or 0)}"
                    for supplier_id, risk_class, otif_rate, avg_delay_days, total_incidents, _ in row
                )
                return (
                    "⚠️ Clé GROQ_API_KEY non configurée. Fallback local activé.\n\n"
                    f"Contexte disponible :\n- {items}\n\n"
                    "Analyse métier : ces indicateurs sont directement extraits de la base Gold Yeewde et doivent servir de base pour les recommandations de performance fournisseur."
                )
    except Exception as exc:
        return (
            "⚠️ Clé GROQ_API_KEY non configurée. Fallback local activé.\n\n"
            f"Contexte disponible :\n- {context if context else 'Aucun contexte métier retrouvé.'}\n\n"
            f"Note de diagnostic : la base DuckDB n’était pas exploitable pour un calcul direct ({exc})."
        )

    return (
        "⚠️ Clé GROQ_API_KEY non configurée. Fallback local activé.\n\n"
        f"Contexte disponible :\n- {context if context else 'Aucun contexte métier retrouvé.'}\n\n"
        "Analyse métier : le système Yeewde conserve les indicateurs OTIF, le délai moyen, les incidents qualité et la performance fournisseur dans DuckDB."
    )


def _format_local_fallback(user_query: str, docs: list[str]) -> str:
    """Construit une réponse exploitable même sans clé Groq."""
    if docs:
        db_relevant = _build_db_backed_fallback(user_query, docs)
        if db_relevant:
            return db_relevant
    return _build_db_backed_fallback(user_query, docs)


def ask_rag_engine(user_query: str) -> str:
    """Interroge l'assistant RAG via l'API Groq ou le fallback local."""
    user_query = (user_query or "").strip()
    if not user_query:
        return "Merci de poser une question métier valide sur les KPI, fournisseurs ou incidents de la supply chain."

    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        docs = retrieve(user_query, 4) or [
            "Aucun contexte métier n'a été trouvé dans la base Yeewde pour cette requête.",
            "Les tables gold.marts_supplier_kpi et gold.marts_otif_kpi restent disponibles pour l'analyse opérationnelle.",
        ]
        return _format_local_fallback(user_query, docs)

    try:
        from langchain_groq import ChatGroq

        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            max_tokens=GROQ_MAX_TOKENS,
            temperature=GROQ_TEMPERATURE,
        )

        context = "\n\n".join(retrieve(user_query, 3))
        prompt = f"""
    Tu es l'assistant expert en Supply Chain et OTIF pour Yeewde AI.

    Base-toi rigoureusement sur le contexte suivant :
    {context}

    Question : {user_query}

    Consignes de restitution :
    1. Présente les tableaux avec des colonnes courtes (Rang, Fournisseur, Classe, OTIF %, Délai (j), Incidents).
    2. Ne mets pas de longs textes ou paragraphes à l'intérieur des cellules de tableau.
    3. Place les analyses détaillées, commentaires de tendance et actions prioritaires sous le tableau avec des puces Markdown.
    4. N'utilise aucune balise HTML brute (comme <br>).
    5. N'invente aucune valeur absente du contexte. Si une information manque, indique-le clairement.
    6. Réponds en français, de façon précise et concise.
    """

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        context = "\n\n".join(retrieve(user_query, 3))
        return (
            f"⚠️ Erreur lors de la génération RAG : {str(e)}\n\n"
            f"Contexte disponible :\n{context}"
        )
