import requests
import streamlit as st

st.title("Triagem Veterinária")

relato = st.text_area("Digite o relato do tutor:")

if st.button("Enviar"):
    resposta = requests.post(
        "http://localhost:8000/triagem",
        json={
            "relato": relato,
            "especie": None,
            "idade": None
        }
    )

    dados = resposta.json()

    st.write("Resposta da LLM:")
    st.write(dados["resposta_modelo"])