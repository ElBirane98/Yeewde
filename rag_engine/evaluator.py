"""
rag_engine/evaluator.py
Évaluation légère du RAG (couverture du retrieval + latence moyenne).
Usage : python -m rag_engine.evaluator
"""
from __future__ import annotations

from rag_engine.logging import get_rag_stats
from rag_engine.retriever import retrieve

SAMPLE_QUESTIONS = [
    "Quels fournisseurs ont le pire OTIF ?",
    "Incidents qualité critiques récents",
    "Retards de livraison sur pièces avioniques",
]


def evaluate_retrieval() -> dict:
    stats = get_rag_stats()
    evaluations: list[dict] = []

    for question in SAMPLE_QUESTIONS:
        docs = retrieve(question, n_results=3)
        evaluations.append(
            {
                "question": question,
                "docs_retrieved": len(docs),
                "has_context": len(docs) > 0 and len(docs[0]) > 20,
            }
        )

    success_rate = sum(1 for item in evaluations if item["has_context"]) / len(evaluations)
    return {
        "retrieval_success_rate": round(success_rate, 3),
        "samples": evaluations,
        "logging": stats,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(evaluate_retrieval(), indent=2))
