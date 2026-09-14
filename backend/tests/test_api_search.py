"""
Contrato HTTP do /search.

A rota é do trilho A e não tinha teste. Ela é a matéria-prima da régua de
recuperação: quem mede se a busca trouxe o protocolo certo precisa saber
**de qual documento** cada trecho veio, e precisa ver a lista inteira,
inclusive o que ficou abaixo do corte de relevância.
"""

import sys
import types

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.retrieved_document import RetrievedDocument


def trecho(
    chunk_id: str,
    titulo: str,
    topic: str,
    score: float,
    source_file: str = "protocolo.pdf",
) -> RetrievedDocument:

    return RetrievedDocument(
        id=chunk_id,
        chunk_id=chunk_id,
        title=titulo,
        content="conteúdo do protocolo",
        source="Conteúdo sintético para teste técnico",
        score=score,
        topic=topic,
        source_file=source_file,
    )


@pytest.fixture
def cliente(monkeypatch):
    """
    Dublê no cliente de busca, não no banco: a rota é fina e o que importa
    é o que ela faz com o que a busca devolve.
    """

    from app.clients import retrieval_client

    devolvidos = [
        trecho("c1", "Suspeita de intoxicação por chocolate",
               "chocolate_toxicosis", 0.82, "intoxicacao_chocolate.pdf"),
        trecho("c2", "Trauma, quedas e hemorragias",
               "trauma_and_bleeding", 0.41, "trauma_hemorragia.pdf"),
    ]

    monkeypatch.setattr(
        retrieval_client.RetrievalClient,
        "retrieve",
        staticmethod(lambda queries: list(devolvidos)),
    )

    with TestClient(app) as test_client:
        yield test_client


def test_a_busca_devolve_a_procedencia_de_cada_trecho(cliente):
    """
    `topic` é o identificador estável do assunto; o título é texto livre e
    muda quando o documento é reescrito. A régua julga pelo primeiro.
    """

    corpo = cliente.post(
        "/search/", json={"question": "meu cachorro comeu chocolate"}
    ).json()

    primeiro = corpo["documents"][0]

    assert primeiro["topic"] == "chocolate_toxicosis"
    assert primeiro["source_file"] == "intoxicacao_chocolate.pdf"


def test_a_ordem_e_as_notas_sao_preservadas(cliente):
    """
    A régua mede **posição**: em que lugar da lista o protocolo certo
    apareceu. Reordenar ou omitir aqui inutilizaria a medição.
    """

    documentos = cliente.post(
        "/search/", json={"question": "chocolate"}
    ).json()["documents"]

    assert [d["topic"] for d in documentos] == [
        "chocolate_toxicosis",
        "trauma_and_bleeding",
    ]
    assert [d["score"] for d in documentos] == [0.82, 0.41]


def test_o_trecho_irrelevante_continua_na_resposta(cliente):
    """
    Ao contrário do `/chat/`, esta rota **não** aplica o corte de
    relevância: um trecho com nota 0,41 aparece. É de propósito — a régua
    precisa enxergar o que ficou abaixo do corte para dizer se o protocolo
    certo estava lá embaixo (evidencias/backlog.md#b-11).
    """

    documentos = cliente.post(
        "/search/", json={"question": "chocolate"}
    ).json()["documents"]

    assert len(documentos) == 2
    assert min(d["score"] for d in documentos) < 0.70


def test_o_formato_antigo_continua_valendo(cliente):
    """
    Os campos novos são acréscimo. Quem já consumia a rota não pode
    quebrar.
    """

    primeiro = cliente.post(
        "/search/", json={"question": "chocolate"}
    ).json()["documents"][0]

    for campo in ("id", "title", "content", "source", "score"):
        assert campo in primeiro


def test_trecho_sem_metadado_de_procedencia_nao_quebra(cliente, monkeypatch):
    """
    A base pode ter trechos ingeridos antes de os metadados existirem. Eles
    devem aparecer com procedência vazia, não derrubar a rota.
    """

    from app.clients import retrieval_client

    monkeypatch.setattr(
        retrieval_client.RetrievalClient,
        "retrieve",
        staticmethod(
            lambda queries: [
                RetrievedDocument(
                    id="antigo",
                    chunk_id="antigo",
                    title="Documento sem título",
                    content="texto",
                    source="Fonte não informada",
                    score=0.5,
                )
            ]
        ),
    )

    documento = cliente.post(
        "/search/", json={"question": "qualquer"}
    ).json()["documents"][0]

    assert documento["topic"] == ""
    assert documento["source_file"] == ""


@pytest.mark.parametrize(
    "metadata,stored,expected",
    [
        ({"body": "corpo limpo"}, "Document title: X\nSection: Y\n\ncorpo limpo", "corpo limpo"),
        ({}, "texto legado", "texto legado"),
    ],
)
def test_cliente_separa_corpo_do_embedding_e_preserva_legado(
    monkeypatch, metadata, stored, expected
):
    from app.clients.retrieval_client import RetrievalClient
    from app.database.chroma_client import ChromaDBClient

    class Collection:
        def count(self):
            return 1

        def query(self, **kwargs):
            return {
                "ids": [["c1"]],
                "documents": [[stored]],
                "metadatas": [[metadata]],
                "distances": [[0.1]],
            }

    monkeypatch.setattr(
        ChromaDBClient,
        "get_collection",
        staticmethod(lambda: Collection()),
    )

    assert RetrievalClient.retrieve(["consulta"])[0].content == expected
