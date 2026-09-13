"""
`/chat/` com tutor_id/pet_id/conversation_id.

Cobre o que test_api_chat.py não cobre: sem nenhum dos três campos, nada
deste arquivo deveria rodar (comportamento idêntico a antes desta extensão
existir) — é o que o primeiro teste trava.
"""

from conftest import (
    LLMClientFalso,
    QueryClientFalso,
    RerankerFalso,
    RetrievalClientFalso,
)

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_chat_pipeline
from app.exceptions.pet_exception import PetNotFoundException
from app.main import app
from app.pipeline.chat_pipeline import ChatPipeline
from app.schemas.pet import PetResponse, Sex, Species
from app.services import chat_service


@pytest.fixture
def llm():
    return LLMClientFalso()


@pytest.fixture
def client(llm):

    def pipeline_falso():
        return ChatPipeline(
            query_client=QueryClientFalso(),
            retrieval_client=RetrievalClientFalso([]),
            reranker=RerankerFalso,
            llm_client=llm,
        )

    app.dependency_overrides[get_chat_pipeline] = pipeline_falso

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _pet(**overrides) -> PetResponse:

    dados = {
        "id": "pet-1",
        "tutor_id": "tutor-1",
        "name": "Bidu",
        "species": Species.CAO,
        "sex": Sex.MACHO,
        "neutered": True,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    dados.update(overrides)

    return PetResponse(**dados)


def test_sem_nenhum_id_nao_toca_pet_nem_historico(client, monkeypatch):

    def explode(*args, **kwargs):
        raise AssertionError("não deveria ser chamado sem tutor/pet/conversation_id")

    monkeypatch.setattr(chat_service.PetService, "get", explode)
    monkeypatch.setattr(chat_service.ConversationService, "append_turn", explode)

    resposta = client.post("/chat/", json={"question": "meu cão vomitou"})

    assert resposta.status_code == 200
    assert resposta.json()["conversation_id"] is None


def test_pet_id_acrescenta_o_cadastro_ao_prompt(client, llm, monkeypatch):

    monkeypatch.setattr(chat_service.PetService, "get", lambda pet_id: _pet(id=pet_id))
    monkeypatch.setattr(
        chat_service.ConversationService, "append_turn", lambda **kwargs: None
    )

    resposta = client.post(
        "/chat/",
        json={"question": "ele vomitou hoje", "pet_id": "pet-1"},
    )

    assert resposta.status_code == 200

    mensagens = llm.chamadas[-1]["messages"]
    conteudo_usuario = mensagens[-1]["content"]

    assert "Dados cadastrais do animal" in conteudo_usuario
    assert "Espécie: cão" in conteudo_usuario
    assert "castrado" in conteudo_usuario


def test_pet_id_inexistente_propaga_404_e_nao_grava_historico(client, monkeypatch):

    def nao_encontrado(pet_id):
        raise PetNotFoundException(pet_id)

    monkeypatch.setattr(chat_service.PetService, "get", nao_encontrado)

    resposta = client.post(
        "/chat/",
        json={"question": "meu cão vomitou", "pet_id": "nao-existe"},
    )

    assert resposta.status_code == 404


def test_tutor_id_grava_historico_e_devolve_conversation_id(client, monkeypatch):

    chamadas = []

    def gravar(**kwargs):
        chamadas.append(kwargs)
        return "conv-123"

    monkeypatch.setattr(chat_service.ConversationService, "append_turn", gravar)

    resposta = client.post(
        "/chat/",
        json={"question": "meu cão vomitou", "tutor_id": "tutor-1"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["conversation_id"] == "conv-123"
    assert chamadas[0]["tutor_id"] == "tutor-1"
    assert chamadas[0]["conversation_id"] is None


def test_conversation_id_enviado_e_repassado_ao_historico(client, monkeypatch):

    chamadas = []

    def gravar(**kwargs):
        chamadas.append(kwargs)
        return kwargs["conversation_id"]

    monkeypatch.setattr(chat_service.ConversationService, "append_turn", gravar)

    resposta = client.post(
        "/chat/",
        json={"question": "e agora?", "conversation_id": "conv-existente"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["conversation_id"] == "conv-existente"
    assert chamadas[0]["conversation_id"] == "conv-existente"


def test_historico_indisponivel_nao_derruba_a_triagem(client, monkeypatch):
    """
    ConversationService.append_turn já engole falha de Mongo (testado em
    test_conversation_service.py); aqui confere que o /chat/ não presume
    que sempre há um conversation_id de volta.
    """

    monkeypatch.setattr(
        chat_service.ConversationService, "append_turn", lambda **kwargs: None
    )

    resposta = client.post(
        "/chat/",
        json={"question": "meu cão vomitou", "tutor_id": "tutor-1"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["conversation_id"] is None
