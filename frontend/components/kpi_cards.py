"""Cartes KPI OTIF."""

from __future__ import annotations

import streamlit as st


def render_kpi_cards(payload: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Taux OTIF global", f"{payload['global_otif']:.1%}")
    col2.metric("Commandes On-Time", f"{payload['on_time_rate']:.1%}")
    col3.metric("Commandes In-Full", f"{payload['in_full_rate']:.1%}")
    col4.metric("Commandes livrées analysées", f"{payload['total_orders']:,}")
