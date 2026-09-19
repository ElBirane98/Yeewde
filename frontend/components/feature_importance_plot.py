"""Graphique d'importance des features."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def render_feature_importance(importance_payload: list[dict] | None) -> None:
    if not importance_payload:
        st.info("Importance des features indisponible (entraînez le modèle).")
        return
    frame = pd.DataFrame(importance_payload)
    figure = px.bar(
        frame,
        x="importance",
        y="feature",
        orientation="h",
        title="Importance globale des features (LightGBM)",
        labels={"importance": "Score", "feature": "Feature"},
    )
    st.plotly_chart(figure, width="stretch")
