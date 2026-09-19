"""Interface chat RAG."""

from __future__ import annotations

import streamlit as st


def render_rag_chat(request_fn) -> None:
    question = st.text_input(
        "Posez une question sur vos opérations de Supply Chain :",
        placeholder="Pourquoi l'OTIF du fournisseur SUP004 a-t-il chuté ?",
    )
    if not question:
        return
    with st.spinner("Recherche du contexte et génération de la réponse…"):
        response = request_fn("/chat", method="POST", payload={"question": question})
    if "error" in response:
        st.error(response["error"])
        return
    st.markdown("### 🤖 Diagnostic & recommandation")
    st.write(response["answer"])
