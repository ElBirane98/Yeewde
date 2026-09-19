"""
Module ERP Simulator - Yeewde AI
Permet de simuler des modifications opérationnelles sur une commande (Purchase Order)
et d'évaluer l'impact sur le risque OTIF via le modèle ML et le moteur RAG.
"""

import os
import duckdb
import pandas as pd
from ml_engine.predict import predict_batch
from rag_engine.generator import explain_po_risk


DB_PATH = os.path.join("data", "yeewde.duckdb")


def get_po_details(po_id: str) -> pd.DataFrame:
    """Récupère les détails actuels d'un Bon de Commande sous forme de DataFrame depuis DuckDB."""
    conn = duckdb.connect(DB_PATH, read_only=True)
    query = """
        SELECT *
        FROM gold.marts_otif_kpi
        WHERE po_id = ?
        LIMIT 1
    """
    df = conn.execute(query, [po_id]).df()
    conn.close()

    if df.empty:
        raise ValueError(f"Commande {po_id} introuvable dans gold.marts_otif_kpi.")
    
    return df


def simulate_po_impact(
    po_id: str, 
    new_lead_time: int = None, 
    new_supplier_id: str = None, 
    new_quantity: int = None
) -> dict:
    """
    Simule une modification d'attributs de commande (Write-Back simulé)
    et évalue le nouveau score de risque ML + explication RAG.
    """
    # 1. Extraction du DataFrame d'origine
    initial_df = get_po_details(po_id)
    simulated_df = initial_df.copy()

    # 2. Application des modifications simulées sur les colonnes du DataFrame
    if new_lead_time is not None and "standard_lead_time_days" in simulated_df.columns:
        simulated_df["standard_lead_time_days"] = new_lead_time
    if new_supplier_id is not None and "supplier_id" in simulated_df.columns:
        simulated_df["supplier_id"] = new_supplier_id
    if new_quantity is not None and "ordered_qty" in simulated_df.columns:
        simulated_df["ordered_qty"] = new_quantity
        if "total_order_cost" in simulated_df.columns and "unit_cost" in simulated_df.columns:
            simulated_df["total_order_cost"] = (
                simulated_df["ordered_qty"] * simulated_df["unit_cost"]
            ).round(2)

    # 3. Prédiction du risque ML avec predict_batch (Avant vs Après)
    initial_pred = predict_batch(initial_df).iloc[0]
    simulated_pred = predict_batch(simulated_df).iloc[0]

    initial_risk = float(initial_pred['risk_score'])
    simulated_risk = float(simulated_pred['risk_score'])

    # Structure du résultat pour le moteur RAG
    risk_result = {
        "risk_score": simulated_risk,
        "otif_proba": float(simulated_pred['otif_proba']),
        "risk_level": str(simulated_pred['risk_level'])
    }

    supplier_id = str(simulated_df['supplier_id'].iloc[0]) if 'supplier_id' in simulated_df.columns else None

    # 4. Explication RAG via generator.explain_po_risk
    rag_explanation = explain_po_risk(
        po_id=po_id, 
        risk_result=risk_result, 
        supplier_id=supplier_id
    )

    return {
        "po_id": po_id,
        "initial_risk_score": round(initial_risk, 4),
        "simulated_risk_score": round(simulated_risk, 4),
        "risk_delta": round(simulated_risk - initial_risk, 4),
        "simulated_risk_level": risk_result["risk_level"],
        "rag_recommendation": rag_explanation
    }


if __name__ == "__main__":
    try:
        # Récupérer un po_id valide directement dans DuckDB pour le test
        conn = duckdb.connect(DB_PATH, read_only=True)
        sample_po = conn.execute("SELECT po_id FROM gold.marts_otif_kpi LIMIT 1").fetchone()[0]
        conn.close()

        print(f"--- TEST SIMULATION SUR {sample_po} ---")
        res = simulate_po_impact(sample_po, new_lead_time=25)
        print(f"Risque Initial : {res['initial_risk_score']:.1%}")
        print(f"Risque Simulé  : {res['simulated_risk_score']:.1%} (Niveau : {res['simulated_risk_level']})")
        print(f"\nExplication RAG :\n{res['rag_recommendation']}")
    except Exception as e:
        print(f"Erreur lors du test du simulateur : {e}")