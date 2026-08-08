import requests


BACKEND_URL = "http://backend:8000"


def transcribe_audio(audio_bytes: bytes):

    response = requests.post(
        f"{BACKEND_URL}/voice/",
        files={
            "audio": (
                "audio.wav",
                audio_bytes,
                "audio/wav",
            )
        },
    )

    response.raise_for_status()

    return response.json()