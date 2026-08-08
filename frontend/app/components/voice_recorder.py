import streamlit as st

from streamlit_mic_recorder import mic_recorder


def record_voice():

    audio = mic_recorder(
        start_prompt="🎙️ Gravar áudio",
        stop_prompt="⏹️ Parar gravação",
        just_once=True,
        use_container_width=True,
        format="wav",
        key="voice_recorder",
    )

    return audio