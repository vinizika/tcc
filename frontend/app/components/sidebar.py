import streamlit as st

from app.components.pet_form import render_tutor_and_pet


def render_sidebar():

    with st.sidebar:

        st.title("VetAI")

        st.markdown("---")

        render_tutor_and_pet()

        st.markdown("---")

        if st.button("🗑 Limpar conversa"):

            st.session_state.messages = []
            st.session_state.conversation_id = None

            st.rerun()
