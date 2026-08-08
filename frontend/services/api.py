import requests

API_URL = "http://backend:8000"


def send_chat(question: str):

    response = requests.post(
        f"{API_URL}/chat/",
        json={
            "question": question
        }
    )

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