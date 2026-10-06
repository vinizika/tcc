import requests

API_URL = "http://backend:8000"


def send_chat(
    question: str,
    conversation_id: str | None = None,
):

    # Esta tela sempre guarda o histórico: o backend devolve o id da conversa
    # na primeira resposta, e os próximos turnos continuam nela.
    payload = {"question": question, "save_history": True}

    if conversation_id:
        payload["conversation_id"] = conversation_id

    response = requests.post(f"{API_URL}/chat/", json=payload)

    response.raise_for_status()

    return response.json()


def send_voice(audio_file):

    response = requests.post(
        f"{API_URL}/voice/",
        files={
            "audio": audio_file
        }
    )

    response.raise_for_status()

    return response.json()

