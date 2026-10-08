"""
`/chat/` com histórico de conversa (`save_history`, `conversation_id`).

Cobre o que test_api_chat.py não cobre: sem nenhum dos dois campos, nada
deste arquivo deveria rodar (comportamento idêntico ao do runner de
avaliação) — é o que o primeiro teste trava. Até 06/10 o histórico também
começava por `tutor_id`/`pet_id` (cadastro no Supabase), que saiu na
rodada 25 do Ryu.
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
from app.main import app
from app.pipeline.chat_pipeline import ChatPipeline
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


def test_sem_historico_pedido_nao_grava_nada(client, monkeypatch):

    def explode(*args, **kwargs):
        raise AssertionError("não deveria gravar sem save_history nem conversation_id")

    monkeypatch.setattr(chat_service.ConversationService, "append_turn", explode)

    resposta = client.post("/chat/", json={"question": "meu cão vomitou"})

    assert resposta.status_code == 200
    assert resposta.json()["conversation_id"] is None


def test_campos_do_cadastro_antigo_sao_ignorados(client, llm, monkeypatch):
    """Quem ainda mandar tutor_id/pet_id recebe a triagem, sem cadastro nem histórico."""

    def explode(*args, **kwargs):
        raise AssertionError("tutor_id/pet_id não abrem mais histórico")

    monkeypatch.setattr(chat_service.ConversationService, "append_turn", explode)

    resposta = client.post(
        "/chat/",
        json={"question": "ele vomitou hoje", "tutor_id": "t-1", "pet_id": "p-1"},
    )

    assert resposta.status_code == 200
    assert "Dados cadastrais do animal" not in llm.chamadas[-1]["messages"][-1]["content"]


def test_save_history_grava_e_devolve_conversation_id(client, monkeypatch):

    chamadas = []

    def gravar(**kwargs):
        chamadas.append(kwargs)
        return "conv-123"

    monkeypatch.setattr(chat_service.ConversationService, "append_turn", gravar)

    resposta = client.post(
        "/chat/",
        json={"question": "meu cão vomitou", "save_history": True},
    )

    assert resposta.status_code == 200
    assert resposta.json()["conversation_id"] == "conv-123"
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
        json={"question": "meu cão vomitou", "save_history": True},
    )

    assert resposta.status_code == 200
    assert resposta.json()["conversation_id"] is None
