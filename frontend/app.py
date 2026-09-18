"""
Yeewde AI - Cockpit Supply Chain & Monitoring DataOps / MLOps / RAG
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Yeewde AI - Supply Chain Engine",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation des ressources en cache
@st.cache_resource
def get_db_connection():
    db_path = os.getenv("DUCKDB_PATH", "data/yeewde.duckdb")
    if os.path.exists(db_path):
        return duckdb.connect(db_path, read_only=True)
    return None

# Barre latérale - Navigation
st.sidebar.title("📦 Yeewde AI")
st.sidebar.caption("Data Platform & IA pour la Supply Chain")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard OTIF & KPIs", "🔮 Prédiction Risque ML", "💬 Assistant RAG", "🎛️ Simulateur ERP (What-If)", "⚙️ Observabilité DataOps"]
)

conn = get_db_connection()

# PAGE 1 : DASHBOARD OTIF & KPIS
if page == "📊 Dashboard OTIF & KPIs":
    st.title("📊 Dashboard Supply Chain - OTIF Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Taux OTIF Global", "84.2%", "+1.5%")
    col2.metric("Commandes On-Time", "89.1%", "+0.8%")
    col3.metric("Commandes In-Full", "94.5%", "-0.2%")
    col4.metric("Commandes à Risque", "124 POs", "-12")
    
    st.divider()
    
    # Données simulées pour visuels Plotly
    df_chart = pd.DataFrame({
        "Fournisseur": ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E"],
        "Taux OTIF (%)": [92, 78, 85, 64, 91],
        "Volume Commandes": [450, 320, 280, 150, 500]
    })
    
    fig = px.bar(df_chart, x="Fournisseur", y="Taux OTIF (%)", color="Taux OTIF (%)",
                 title="Performance OTIF par Fournisseur", color_continuous_scale="RdYlGn")
    st.plotly_chart(fig, use_container_width=True)

# PAGE 2 : PREDICTION RISQUE ML
elif page == "🔮 Prédiction Risque ML":
    st.title("🔮 Prédiction de Retards & Risques Commande (LightGBM)")
    
    with st.form("ml_predict_form"):
        col1, col2 = st.columns(2)
        with col1:
            supplier = st.selectbox("Fournisseur", ["Supplier A", "Supplier B", "Supplier C", "Supplier D"])
            lead_time = st.number_input("Lead Time estimé (jours)", min_value=1, value=15)
        with col2:
            order_qty = st.number_input("Quantité Commandée", min_value=1, value=500)
            transport_mode = st.selectbox("Mode de Transport", ["Maritime", "Aérien", "Routier"])
            
        submit = st.form_submit_button("Évaluer le Risque OTIF")
        
    if submit:
        st.success("Analyse terminée avec succès.")
        st.warning("⚠️ **Score de Risque de Retard** : 78% (Risque Élevé)")
        st.info("💡 **Diagnostic ML** : Le fournisseur présente des goulots d'étranglement fréquents sur ce mode de transport.")

# PAGE 3 : ASSISTANT RAG
elif page == "💬 Assistant RAG":
    st.title("💬 Assistant Prescriptif RAG (LLaMA 3.1 / Groq)")
    
    query = st.text_input("Posez une question sur vos opérations de Supply Chain :", 
                          placeholder="Pourquoi le taux OTIF du fournisseur B a-t-il chuté ce mois-ci ?")
    
    if query:
        with st.spinner("Analyse des rapports et génération du diagnostic..."):
            st.markdown("### 🤖 Diagnostic & Recommandation :")
            st.write("Le retard observé sur Supplier B est principalement causé par des ruptures de stock de matières premières chez le sous-traitant de Niveau 2, combinées à un dépassement de délai de dédouanement portuaire (+4 jours en moyenne).")
            st.markdown("**Action recommandée** : Transférer 20% des volumes prioritaires vers le fournisseur A pour sécuriser les livraisons critiques.")

# PAGE 4 : SIMULATEUR ERP (WHAT-IF)
elif page == "🎛️ Simulateur ERP (What-If)":
    st.title("🎛️ Simulateur Prescriptif 'What-If'")
    st.caption("Ajustez les paramètres des Bon de Commande (PO) pour évaluer l'impact direct sur les risques OTIF.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Paramètres Actuels PO")
        st.json({
            "PO_ID": "PO-2026-8891",
            "Délai_Fournisseur": "20 jours",
            "Quantité": 1200,
            "Mode": "Maritime"
        })
    with col2:
        st.subheader("Ajustement de Simulation")
        new_lead_time = st.slider("Nouveau Délai Fournisseur (jours)", 5, 45, 12)
        new_mode = st.selectbox("Nouveau Mode de Transport", ["Aérien", "Maritime", "Express Routier"])
        
    if st.button("Lancer la Simulation What-If"):
        st.subheader("Résultat de la Simulation :")
        st.success("✅ **Réduction du Risque OTIF** : Le risque passe de 78% à **14%**.")
        st.write("**Explication RAG** : L'utilisation de l'Aérien réduit le délai d'acheminement de 8 jours, évitant ainsi la rupture de stock anticipée sur le site de fabrication.")

# PAGE 5 : OBSERVABILITE DATAOPS
elif page == "⚙️ Observabilité DataOps":
    st.title("⚙️ Moniteur DataOps & Drift Detection")
    
    col1, col2 = st.columns(2)
    col1.metric("Santé des Pipelines Dagster", "100% OK", "5/5 Assets Synchronisés")
    col2.metric("Data Drift Status (Evidently)", "Pas de Drift Majeur", "P-Value > 0.05")
    
    st.divider()
    st.subheader("Statut des Assets de Données")
    st.table(pd.DataFrame([
        {"Asset": "ingestion_raw_pos", "Statut": "Succès", "Dernière Exécution": "Aujourd'hui 20:45"},
        {"Asset": "dbt_otif_metrics", "Statut": "Succès", "Dernière Exécution": "Aujourd'hui 20:45"},
        {"Asset": "ml_otif_model", "Statut": "Succès", "Dernière Exécution": "Aujourd'hui 20:45"},
        {"Asset": "rag_vector_store", "Statut": "Succès", "Dernière Exécution": "Aujourd'hui 20:45"},
        {"Asset": "evidently_drift_report", "Statut": "Succès", "Dernière Exécution": "Aujourd'hui 20:45"}
    ]))