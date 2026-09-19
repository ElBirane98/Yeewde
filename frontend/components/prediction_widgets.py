"""Widgets de prédiction ML."""

from __future__ import annotations

import streamlit as st


def render_prediction_form(request_fn) -> None:
    st.caption("Saisissez un identifiant de commande présent dans la table Gold.")
    with st.form("ml_predict_form"):
        po_id = st.text_input("Identifiant de commande (PO)", value="PO000123")
        submitted = st.form_submit_button("Évaluer le risque")

    result_container = st.empty()
    if submitted:
        if not po_id.strip():
            result_container.warning("Saisissez un identifiant de commande.")
            return

        with st.spinner("Évaluation du risque ML..."):
            result = request_fn(f"/predict/{po_id.strip()}")

        with result_container.container():
            if "error" in result:
                st.error(result["error"])
                return

            risk_score = float(result.get("risk_score") or 0)
            otif_probability = float(result.get("otif_proba") or 0)
            risk_level = str(result.get("risk_level") or "INCONNU")
            risk_percent = int(round(risk_score * 100))

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("Risque de non-OTIF", f"{risk_score:.1%}")
            col2.metric("Probabilité OTIF", f"{otif_probability:.1%}")
            col3.metric("Niveau de risque", risk_level)

            st.progress(risk_percent, text=f"Risque estimé : {risk_percent} %")
            st.markdown(
                f"📋 **Diagnostic pour {po_id.strip()} :** la commande présente un risque "
                f"**{risk_level.lower()}** de non-OTIF. Utilisez le **Simulateur ERP (Et si)** "
                "pour tester un autre délai ou fournisseur."
            )
