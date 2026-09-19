"""Cockpit Streamlit de Yeewde AI."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from frontend.components.drift_widget import render_drift_status
    from frontend.components.feature_importance_plot import render_feature_importance
    from frontend.components.kpi_cards import render_kpi_cards
    from frontend.components.prediction_widgets import render_prediction_form
    from frontend.components.rag_chatbot import render_rag_chat
else:
    from .components.drift_widget import render_drift_status
    from .components.feature_importance_plot import render_feature_importance
    from .components.kpi_cards import render_kpi_cards
    from .components.prediction_widgets import render_prediction_form
    from .components.rag_chatbot import render_rag_chat

load_dotenv()

st.set_page_config(
    page_title="Yeewde IA — Control Tower logistique",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: #252525;
        --muted: #666666;
        --accent: #666666;
        --accent-soft: #e8e8e8;
        --paper: #f4f4f4;
        --line: #d2d2d2;
    }

    .stApp {
        background:
            radial-gradient(circle at 92% 4%, rgba(110, 110, 110, 0.10), transparent 24rem),
            linear-gradient(135deg, #f4f4f4 0%, #e9e9e9 100%);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        color: var(--ink) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: 0 !important;
    }

    h1 { font-size: clamp(2rem, 4vw, 3.4rem) !important; }
    [data-testid='stSidebar'] {
        background: #3b3b3b;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid='stSidebar'] h1 {
        font-size: 1.35rem !important;
        margin-bottom: 0.2rem !important;
    }
    [data-testid='stSidebar'] * { color: #e8f1f2 !important; }
    [data-testid='stSidebar'] .stRadio label { font-size: 0.9rem; }
    [data-testid='stMetric'] {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid var(--line);
        border-left: 4px solid var(--accent);
        border-radius: 8px;
        padding: 1rem 1.1rem;
        box-shadow: 0 8px 24px rgba(16, 42, 67, 0.06);
    }
    [data-testid='stMetricLabel'] { color: var(--muted); }
    [data-testid='stMetricValue'] { color: var(--ink); font-family: 'Space Grotesk', sans-serif; }
    [data-testid='stAlert'] {
        background: #e4e4e4 !important;
        border: 1px solid #c4c4c4 !important;
        border-left: 4px solid #666666 !important;
        color: var(--ink) !important;
    }
    [data-testid='stAlert'] p,
    [data-testid='stAlert'] span,
    [data-testid='stAlert'] div {
        color: var(--ink) !important;
    }
    .control-tower-kicker {
        color: var(--accent);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0 0 0.35rem;
    }
    .control-tower-subtitle {
        color: var(--muted);
        font-size: 1.02rem;
        margin: -1rem 0 1.6rem;
    }
    .stDataFrame, [data-testid='stPlotlyChart'] {
        background: rgba(255, 255, 255, 0.68);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.35rem;
    }
    .stButton > button, .stFormSubmitButton > button {
        background: #555555;
        border: 0;
        border-radius: 6px;
        color: white;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

API_BASE_URL = os.getenv("YEEWDE_API_URL", "http://127.0.0.1:8000").rstrip("/")


def _request(path: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        f"{API_BASE_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8")
        try:
            return {"error": json.loads(detail).get("detail", detail), "status_code": exc.code}
        except json.JSONDecodeError:
            return {"error": detail, "status_code": exc.code}
    except URLError:
        return {"error": f"API indisponible à l'adresse {API_BASE_URL}. Démarrez FastAPI avant le cockpit."}


@st.cache_data(ttl=30, show_spinner=False)
def api_get(path: str) -> dict:
    return _request(path)


def _supplier_diagnostic(row: dict) -> tuple[str, str]:
    """Retourne une tendance et une recommandation lisibles pour le fournisseur."""
    otif_rate = float(row.get("otif_rate") or 0)
    avg_delay = float(row.get("avg_delay_days") or 0)
    total_incidents = int(row.get("total_incidents") or 0)
    critical_incidents = int(row.get("critical_incidents") or 0)

    if otif_rate < 0.05 or critical_incidents >= 2 or avg_delay >= 5:
        return (
            "Dégradation",
            "OTIF très faible, délai élevé ou incidents critiques : action corrective urgente.",
        )
    if critical_incidents == 0 and total_incidents <= 3 and avg_delay <= 3:
        return (
            "Légère amélioration",
            "Les délais et incidents restent maîtrisés : consolider les bonnes pratiques et viser un OTIF supérieur à 30 %.",
        )
    return (
        "Stable / légèrement en baisse",
        "La performance reste fragile : suivi rapproché et indicateurs de prévention des incidents recommandés.",
    )


def render_supplier_diagnostic(suppliers: pd.DataFrame) -> None:
    """Affiche le diagnostic opérationnel des trois fournisseurs les moins performants."""
    required_columns = {
        "supplier_id",
        "otif_rate",
        "supplier_risk_class",
        "avg_delay_days",
        "total_incidents",
        "critical_incidents",
    }
    if not required_columns.issubset(suppliers.columns):
        return

    weakest = suppliers.sort_values(["otif_rate", "supplier_id"]).head(3).copy()
    diagnostics = []
    for row in weakest.to_dict("records"):
        trend, recommendation = _supplier_diagnostic(row)
        diagnostics.append(
            {
                "Rang": len(diagnostics) + 1,
                "Fournisseur": row["supplier_id"],
                "Classe": row["supplier_risk_class"] or "—",
                "OTIF %": f"{float(row['otif_rate'] or 0):.1%}",
                "Délai moyen (j)": f"{float(row['avg_delay_days'] or 0):.1f}",
                "Incidents (total / critiques)": (
                    f"{int(row['total_incidents'] or 0)} / "
                    f"{int(row['critical_incidents'] or 0)}"
                ),
                "Tendance estimée": trend,
            }
        )

    st.markdown("### 🤖 Diagnostic et recommandation")
    st.markdown("**Top 3 des fournisseurs les plus faibles (OTIF % de la période analysée)**")
    st.dataframe(pd.DataFrame(diagnostics), hide_index=True, width="stretch")

    st.markdown("#### Synthèse des tendances")
    for row, diagnostic in zip(weakest.to_dict("records"), diagnostics):
        st.markdown(
            f"- **{row['supplier_id']}** : {diagnostic['Tendance estimée']} — "
            f"OTIF à **{diagnostic['OTIF %']}**, délai moyen de "
            f"**{diagnostic['Délai moyen (j)']} j**, "
            f"{diagnostic['Incidents (total / critiques)']} incidents total / critiques. "
            f"{_supplier_diagnostic(row)[1]}"
        )

    if diagnostics:
        priority = diagnostics[0]["Fournisseur"]
        st.info(
            f"Priorité du mois : remettre à niveau {priority}, puis renforcer le suivi des fournisseurs "
            "suivants du classement."
        )


def render_observability(health: dict, drift: dict) -> None:
    """Présente l'état des couches Data, ML et RAG sans exposer le JSON interne."""
    if "error" in health:
        st.error(health["error"])
        return

    data_health = health.get("data_health", {})
    model_health = health.get("model_health", {})
    rag_health = health.get("rag_health", {})
    status = "Opérationnel" if health.get("healthy") else "Action requise"

    st.markdown("### État de la plateforme")
    overview = st.columns(4)
    overview[0].metric("Pipeline", status)
    overview[1].metric("DuckDB", "Prêt" if data_health.get("duckdb_ready") else "Absent")
    overview[2].metric("Modèle ML", "Disponible" if model_health.get("model_present") else "Absent")
    overview[3].metric("Appels RAG", f"{int(rag_health.get('total_calls') or 0):,}")

    checks = health.get("checks", {})
    if checks:
        check_rows = [
            {
                "Contrôle": label.replace("_", " ").title(),
                "État": "OK" if value else "À corriger",
            }
            for label, value in checks.items()
        ]
        st.markdown("### Contrôles des composants")
        st.dataframe(pd.DataFrame(check_rows), hide_index=True, width="stretch")

    st.markdown("### Santé du moteur RAG")
    rag_col1, rag_col2 = st.columns(2)
    rag_col1.metric("Latence moyenne", f"{float(rag_health.get('avg_latency_ms') or 0):.0f} ms")
    rag_col2.metric("Tokens consommés", f"{int(rag_health.get('total_tokens') or 0):,}")
    render_drift_status(drift)


st.sidebar.title("🔍 Yeewde IA")
st.sidebar.caption("Plateforme décisionnelle & Control Tower logistique")
page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Control Tower — OTIF",
        "🔮 Prédiction Risque ML",
        "💬 Assistant RAG",
        "🎛️ ERP simulateur (Et si)",
        "⚙️ Observabilité DataOps",
    ],
)

if page == "📊 Control Tower — OTIF":
    st.markdown('<p class="control-tower-kicker">Yeewde / Operations intelligence</p>', unsafe_allow_html=True)
    st.title("Control Tower")
    st.markdown(
        '<p class="control-tower-subtitle">Surveiller la performance fournisseurs, détecter les dérives et prioriser les actions.</p>',
        unsafe_allow_html=True,
    )
    payload = api_get("/kpi/otif")
    if "error" in payload:
        st.error(payload["error"])
        st.stop()

    render_kpi_cards(payload)

    suppliers = pd.DataFrame(payload["by_supplier"])
    if suppliers.empty:
        st.info("Aucune donnée fournisseur n'est disponible.")
    else:
        figure = px.bar(
            suppliers,
            x="supplier_id",
            y="otif_rate",
            color="otif_rate",
            hover_data=["total_orders"],
            title="Performance OTIF par fournisseur",
            color_continuous_scale="RdYlGn",
            labels={"supplier_id": "Fournisseur", "otif_rate": "Taux OTIF"},
        )
        figure.update_yaxes(tickformat=".0%", range=[0, 1])
        st.plotly_chart(figure, width="stretch")
        render_supplier_diagnostic(suppliers)

elif page == "🔮 Prédiction Risque ML":
    st.markdown('<p class="control-tower-kicker">Yeewde / Predictive control</p>', unsafe_allow_html=True)
    st.title("🔮 Prédiction du risque OTIF")
    render_prediction_form(_request)

    importance = api_get("/model/importance")
    if "features" in importance:
        render_feature_importance(importance["features"])

elif page == "💬 Assistant RAG":
    st.title("💬 Assistant RAG")
    render_rag_chat(_request)

elif page == "🎛️ ERP simulateur (Et si)":
    st.markdown('<p class="control-tower-kicker">Yeewde / Decision support</p>', unsafe_allow_html=True)
    st.title("Simulateur prescriptif What-If")
    st.caption("Comparez le risque ML avant et après modification d'une commande existante.")

    with st.form("what_if_form"):
        po_id = st.text_input("Numéro de commande (PO)", value="PO000123")
        new_lead = st.number_input(
            "Nouveau délai prévu (jours)", min_value=1, max_value=180, value=30
        )
        new_supplier = st.text_input("Nouveau fournisseur (optionnel)", value="SUP004")
        submitted = st.form_submit_button("Simuler l'impact")

    results_container = st.empty()
    if submitted:
        if not po_id.strip():
            results_container.warning("Saisissez un numéro de commande avant de lancer la simulation.")
        else:
            with st.spinner("Calcul de la simulation de risque ML..."):
                result = _request(
                    "/simulate",
                    method="POST",
                    payload={
                        "po_id": po_id.strip(),
                        "new_lead_time": int(new_lead),
                        "new_supplier_id": new_supplier.strip() or None,
                    },
                )

            with results_container.container():
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Risque initial", f"{result['initial_risk_score']:.1%}")
                    col2.metric("Risque simulé", f"{result['simulated_risk_score']:.1%}")
                    col3.metric(
                        "Delta",
                        f"{result['risk_delta']:+.1%}",
                        delta_color="inverse",
                    )

                    st.markdown("### Recommandation RAG")
                    recommendation = result.get(
                        "rag_recommendation", "Aucune recommandation disponible."
                    )
                    st.markdown(f"> {recommendation.replace(chr(10), chr(10) + '> ')}")

else:
    st.markdown('<p class="control-tower-kicker">Yeewde / Reliability monitor</p>', unsafe_allow_html=True)
    st.title("Observabilité de la plateforme")
    st.caption("Surveillance de la donnée, du modèle prédictif et de l’assistant RAG.")
    health = api_get("/health/pipeline")
    drift = api_get("/drift/status")
    render_observability(health, drift)
