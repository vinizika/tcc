"""
Reprodutibilidade das chamadas ao modelo na etapa de consulta.

Sem temperatura e seed fixas nas três etapas (rewrite, multi-query, HyDE),
execuções idênticas produzem consultas diferentes e o estudo de ablação
deixa de ser comparável entre rodadas (evidencias/backlog.md#b-04).
"""

from app.clients.query_client import QueryClient
from app.core.ollama import default_options


class _OllamaClientFalso:

    def __init__(self, content: str = "resposta"):
        self.content = content
        self.chamadas: list[dict] = []

    def chat(self, **kwargs):
        self.chamadas.append(kwargs)
        return {"message": {"content": self.content}}


def test_rewrite_usa_opcoes_padrao(monkeypatch):

    cliente_falso = _OllamaClientFalso("cão com taquipneia e cianose")
    monkeypatch.setattr(QueryClient, "_client", cliente_falso)

    QueryClient.rewrite("meu cachorro esta ofegante e com a lingua azul")

    assert cliente_falso.chamadas[0]["options"] == default_options()


def test_generate_queries_usa_opcoes_padrao(monkeypatch):

    cliente_falso = _OllamaClientFalso("consulta 1\nconsulta 2\nconsulta 3")
    monkeypatch.setattr(QueryClient, "_client", cliente_falso)

    QueryClient.generate_queries("relato do tutor")

    assert cliente_falso.chamadas[0]["options"] == default_options()


def test_generate_hypothetical_document_usa_opcoes_padrao(monkeypatch):

    cliente_falso = _OllamaClientFalso("trecho de protocolo clínico")
    monkeypatch.setattr(QueryClient, "_client", cliente_falso)

    QueryClient.generate_hypothetical_document("relato do tutor")

    assert cliente_falso.chamadas[0]["options"] == default_options()
