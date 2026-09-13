import pytest
from fastapi.testclient import TestClient

from app.exceptions.conversation_exception import ConversationNotFoundException
from app.main import app
from app.schemas.conversation import ConversationMessage, ConversationResponse
from app.services.conversation_service import ConversationService


@pytest.fixture
def client():
    return TestClient(app)


def test_buscar_conversa(client, monkeypatch):

    conversa = ConversationResponse(
        id="conv-1",
        tutor_id="tutor-1",
        pet_id=None,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        messages=[
            ConversationMessage(
                role="tutor", content="oi", timestamp="2026-01-01T00:00:00Z"
            ),
        ],
    )

    monkeypatch.setattr(
        ConversationService, "get", lambda conversation_id: conversa
    )

    resposta = client.get("/conversations/conv-1")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == "conv-1"
    assert resposta.json()["messages"][0]["content"] == "oi"


def test_buscar_conversa_inexistente_devolve_404(client, monkeypatch):

    def nao_encontrada(conversation_id):
        raise ConversationNotFoundException(conversation_id)

    monkeypatch.setattr(ConversationService, "get", nao_encontrada)

    resposta = client.get("/conversations/nao-existe")

    assert resposta.status_code == 404
