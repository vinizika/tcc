import requests

API_URL = "http://backend:8000"


def send_chat(
    question: str,
    tutor_id: str | None = None,
    pet_id: str | None = None,
    conversation_id: str | None = None,
):

    payload = {"question": question}

    # Só entram na requisição os que existem: sem cadastro, o /chat/ roda
    # exatamente como antes desta tela existir.
    if tutor_id:
        payload["tutor_id"] = tutor_id
    if pet_id:
        payload["pet_id"] = pet_id
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


def create_tutor(name: str, phone: str | None = None, email: str | None = None):

    payload = {"name": name}

    if phone:
        payload["phone"] = phone
    if email:
        payload["email"] = email

    response = requests.post(f"{API_URL}/tutors/", json=payload)

    response.raise_for_status()

    return response.json()


def list_tutor_pets(tutor_id: str):

    response = requests.get(f"{API_URL}/tutors/{tutor_id}/pets")

    response.raise_for_status()

    return response.json()


def create_pet(tutor_id: str, **campos):

    payload = {"tutor_id": tutor_id, **{k: v for k, v in campos.items() if v is not None}}

    response = requests.post(f"{API_URL}/pets/", json=payload)

    response.raise_for_status()

    return response.json()
