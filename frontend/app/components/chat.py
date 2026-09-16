import streamlit as st

from services.api import send_chat


def initialize_chat():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "last_voice_message" not in st.session_state:
        st.session_state.last_voice_message = None

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None


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

            # tutor_id/pet_id vêm do cadastro na sidebar (pet_form.py); sem
            # cadastro, os três ficam None e o /chat/ roda como sempre rodou.
            response = send_chat(
                prompt,
                tutor_id=st.session_state.get("tutor_id"),
                pet_id=st.session_state.get("active_pet_id"),
                conversation_id=st.session_state.get("conversation_id"),
            )

            answer = response["answer"]

            st.markdown(answer)

    # O backend devolve o id da conversa quando grava no histórico (tutor,
    # pet ou conversation_id presentes); guardamos para os próximos turnos
    # continuarem a mesma conversa em vez de abrir uma nova a cada mensagem.
    st.session_state.conversation_id = response.get("conversation_id")

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
