import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.title("VetAI")

        st.markdown("---")

        st.write("Projeto TCC")

        st.markdown("---")

        if st.button("🗑 Limpar conversa"):

            st.session_state.messages = []

            st.rerun()