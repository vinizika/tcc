import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.title("Bia")

        st.markdown("---")

        if st.button("🗑 Limpar conversa"):

            st.session_state.messages = []
            st.session_state.conversation_id = None

            st.rerun()
