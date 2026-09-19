"""Widget de monitoring de dérive."""

from __future__ import annotations

import streamlit as st


def render_drift_status(drift: dict) -> None:
    st.subheader("Dérive des données")
    if drift.get("status") in {"not_measured", "invalid_report"}:
        if drift.get("status") == "invalid_report":
            st.error(drift.get("summary", "Le rapport de dérive est invalide."))
            return
        st.warning(drift.get("summary", "Aucune mesure disponible."))
        return
    if "error" in drift:
        st.error(drift["error"])
        return

    detected = drift.get("drift_detected")
    drift_share = float(drift.get("drift_share") or 0)
    metric_col, status_col = st.columns(2)
    metric_col.metric("Part de variables dérivées", f"{drift_share:.0%}")
    status_col.metric("État du drift", "À surveiller" if detected is True else "Stable")

    if detected is True:
        st.warning("Une dérive significative a été détectée. Vérifiez les nouvelles données avant le prochain scoring.")
    elif detected is False:
        st.info("Aucune dérive significative détectée sur le dernier contrôle.")

    details = drift.get("details", {})
    reference_rows = details.get("reference_rows")
    current_rows = details.get("current_rows")
    if reference_rows is not None and current_rows is not None:
        st.caption(
            f"Comparaison effectuée sur {int(reference_rows):,} commandes de référence "
            f"et {int(current_rows):,} commandes courantes."
        )
    st.caption(
        "Le drift mesure une différence de distribution entre deux populations ; "
        "il ne signifie pas automatiquement que les données sont erronées."
    )
