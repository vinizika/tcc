import streamlit as st

from app.components.chat import render_chat
from app.components.sidebar import render_sidebar
from app.components.voice_recorder import record_voice
from app.clients.voice_client import transcribe_audio


st.set_page_config(
    page_title="VetAI",
    page_icon="🐶",
    layout="wide"
)

st.title("🐶 VetAI")

st.subheader("Converse com a VetAI")


voice_prompt = None

audio = record_voice()

if audio is not None:

    with st.spinner("Transcrevendo áudio..."):

        result = transcribe_audio(audio["bytes"])

    voice_prompt = result["transcription"]


render_sidebar()

render_chat(voice_prompt)