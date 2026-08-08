import streamlit as st

from services.api import send_chat


def render_chat():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Histórico
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Caixa de entrada
    prompt = st.chat_input(
        "Digite sua pergunta..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Consultando IA..."):

                response = send_chat(prompt)

                answer = response["answer"]

                st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )