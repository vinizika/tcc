import streamlit as st

from services.api import send_chat


def initialize_chat():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "last_voice_message" not in st.session_state:
        st.session_state.last_voice_message = None


def process_message(prompt: str):

    if not prompt:
        return

    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Mostra mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)

    # Consulta a VetAI
    with st.chat_message("assistant"):

        with st.spinner("Consultando IA..."):

            response = send_chat(prompt)

            answer = response["answer"]

            st.markdown(answer)

    # Adiciona resposta ao histórico
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


def render_chat(voice_prompt=None):

    initialize_chat()

    # Mostra histórico
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Processa mensagem de voz
    if voice_prompt:

        if voice_prompt != st.session_state.last_voice_message:

            st.session_state.last_voice_message = voice_prompt

            process_message(voice_prompt)

    # Entrada de texto
    prompt = st.chat_input(
        "Digite sua pergunta..."
    )

    if prompt:

        process_message(prompt)