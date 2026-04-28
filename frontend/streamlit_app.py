import requests
import streamlit as st

st.title("Triagem Veterinária")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.write(mensagem["content"])

pergunta = st.chat_input("Digite sua mensagem")

if pergunta:
    st.session_state.mensagens.append({
        "role": "user",
        "content": pergunta
    })

    with st.chat_message("user"):
        st.write(pergunta)

    historico = ""

    for mensagem in st.session_state.mensagens:
        historico += f"{mensagem['role']}: {mensagem['content']}\n"

    resposta = requests.post(
        "http://localhost:8000/triagem",
        json={
            "relato": historico,
            "especie": None,
            "idade": None
        }
    )

    resposta_modelo = resposta.json()["resposta_modelo"]

    st.session_state.mensagens.append({
        "role": "assistant",
        "content": resposta_modelo
    })

    with st.chat_message("assistant"):
        st.write(resposta_modelo)