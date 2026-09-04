"""
Contrato HTTP do /chat.

O frontend atual lê apenas "answer" e não pode quebrar; o runner de
avaliação depende dos campos novos. Estes testes fixam os dois lados.
"""

from conftest import (
    LLMClientFalso,
    QueryClientFalso,
    RerankerFalso,
    RetrievalClientFalso,
    documento,
)

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_chat_pipeline
from app.main import app
from app.pipeline.chat_pipeline import ChatPipeline


@pytest.fixture
def client():

    def pipeline_falso():
        return ChatPipeline(
            query_client=QueryClientFalso(),
            retrieval_client=RetrievalClientFalso(
                [documento("c1", "Protocolo de chocolate", 0.82)]
            ),
            reranker=RerankerFalso,
            llm_client=LLMClientFalso(),
        )

    app.dependency_overrides[get_chat_pipeline] = pipeline_falso

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_resposta_mantem_o_formato_que_o_frontend_usa(client):

    resposta = client.post("/chat/", json={"question": "meu cão vomitou"})

    assert resposta.status_code == 200

    corpo = resposta.json()

    assert isinstance(corpo["answer"], str)
    assert corpo["answer"]

    fonte = corpo["sources"][0]
    assert fonte["title"] == "Protocolo de chocolate"
    assert "score" in fonte and "source" in fonte


def test_resposta_traz_os_campos_que_a_avaliacao_precisa(client):

    resposta = client.post("/chat/", json={"question": "meu cão vomitou"})

    corpo = resposta.json()

    assert corpo["config"]["retrieval_enabled"] is True
    assert corpo["config"]["model"]
    assert corpo["retrieval"]["returned_count"] == 1
    assert corpo["timings"]["total_s"] >= 0
    assert corpo["debug"] is None


def test_configuracao_ecoada_reflete_o_que_foi_pedido(client):
    """
    O manifesto de cada rodada de avaliação é montado a partir daqui, então
    a resposta precisa dizer o que rodou, e não o que foi solicitado.
    """

    resposta = client.post(
        "/chat/",
        json={
            "question": "meu cão vomitou",
            "options": {"retrieval_enabled": False, "context_top_k": 5},
        },
    )

    corpo = resposta.json()

    assert corpo["config"]["retrieval_enabled"] is False
    assert corpo["config"]["query_rewriting_enabled"] is False
    assert corpo["config"]["context_top_k"] == 5
    assert corpo["sources"] == []


def test_debug_pode_ser_pedido_por_requisicao(client):

    resposta = client.post(
        "/chat/",
        json={
            "question": "meu cão vomitou",
            "options": {"include_debug": True},
        },
    )

    debug = resposta.json()["debug"]

    assert debug["rewritten_question"] == "consulta reescrita"
    assert debug["queries"]


def test_etapa_nao_implementada_responde_400(client):

    resposta = client.post(
        "/chat/",
        json={
            "question": "meu cão vomitou",
            "options": {"self_refine_enabled": True},
        },
    )

    assert resposta.status_code == 400
    assert "Self-Refine" in resposta.json()["message"]


def test_opcao_desconhecida_responde_422(client):

    resposta = client.post(
        "/chat/",
        json={
            "question": "meu cão vomitou",
            "options": {"retrieval_enable": False},
        },
    )

    assert resposta.status_code == 422


def test_relato_vazio_e_recusado(client):

    assert client.post("/chat/", json={"question": "   "}).status_code == 422
    assert client.post("/chat/", json={"question": ""}).status_code == 422
