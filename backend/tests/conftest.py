"""
Preparação dos testes.

O módulo app.database.chroma_client abre o banco vetorial e carrega o modelo
de embeddings no momento do import, e app.main o importa em cadeia. Para os
testes rodarem rápido e sem estado externo, ele é substituído por um dublê
antes de qualquer import de app.*.

Isto precisa acontecer nas primeiras linhas do arquivo: o conftest é
carregado antes dos módulos de teste.
"""

import sys
import types

_chroma_stub = types.ModuleType("app.database.chroma_client")


class _ColecaoFalsa:

    def count(self):
        return 0

    def query(self, *args, **kwargs):
        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }


class ChromaDBClient:

    @staticmethod
    def get_collection():
        return _ColecaoFalsa()


_chroma_stub.ChromaDBClient = ChromaDBClient

sys.modules.setdefault("app.database.chroma_client", _chroma_stub)


import pytest  # noqa: E402

from app.core.config import Settings  # noqa: E402
from app.clients.llm_client import LLMCallResult  # noqa: E402
from app.models.retrieved_document import RetrievedDocument  # noqa: E402


@pytest.fixture
def settings() -> Settings:
    """
    Settings explícitas, sem depender do ambiente da máquina: os testes
    verificam a lógica de resolução, não a configuração de quem roda.
    """

    return Settings(
        LLM_MODEL="modelo-de-teste",
        LLM_TEMPERATURE=0.0,
        LLM_SEED=42,
        LLM_NUM_CTX=4096,
        LLM_NUM_PREDICT=600,
        STRUCTURED_OUTPUT_MODE="schema",
        QUERY_REWRITING_ENABLED=True,
        MULTI_QUERY_ENABLED=True,
        HYDE_ENABLED=True,
        RETRIEVAL_ENABLED=True,
        CONTEXT_TOP_K=3,
        CONTEXT_MIN_SCORE=0.0,
        COT_ENABLED=False,
        SELF_REFINE_ENABLED=False,
        REWRITTEN_HINT_ENABLED=False,
        TRIAGE_PROMPT_VERSION="v1_grounded",
    )


def documento(
    chunk_id: str = "c1",
    titulo: str = "Protocolo",
    score: float = 0.5,
    conteudo: str = "conteúdo do protocolo",
) -> RetrievedDocument:

    return RetrievedDocument(
        id=chunk_id,
        chunk_id=chunk_id,
        title=titulo,
        content=conteudo,
        source="fonte.pdf",
        score=score,
    )


class QueryClientFalso:
    """
    Dublê do trilho B1. Registra o que foi chamado para os testes poderem
    verificar que uma etapa desligada realmente não roda.
    """

    def __init__(
        self,
        rewritten: str = "consulta reescrita",
        queries: list[str] | None = None,
        hypothetical: str = "documento hipotético",
    ):
        self.rewritten = rewritten
        self.queries = (
            queries
            if queries is not None
            else ["consulta 1", "consulta 2"]
        )
        self.hypothetical = hypothetical

        self.rewrite_calls = 0
        self.generate_queries_calls = 0
        self.hyde_calls = 0

    def rewrite(self, question: str) -> str:
        self.rewrite_calls += 1
        return self.rewritten

    def generate_queries(self, question: str) -> list[str]:
        self.generate_queries_calls += 1
        return list(self.queries)

    def generate_hypothetical_document(self, question: str) -> str:
        self.hyde_calls += 1
        return self.hypothetical


class RetrievalClientFalso:

    def __init__(self, documentos: list[RetrievedDocument] | None = None):
        self.documentos = documentos or []
        self.chamadas: list[list[str]] = []

    def retrieve(self, queries: list[str]) -> list[RetrievedDocument]:
        self.chamadas.append(list(queries))
        return list(self.documentos)


class RerankerFalso:

    @staticmethod
    def rerank(documentos):
        return sorted(
            documentos,
            key=lambda documento: documento.score,
            reverse=True,
        )


class LLMClientFalso:
    """
    Dublê do modelo. Guarda as mensagens recebidas para os testes poderem
    verificar o que foi ao prompt (por exemplo, que o relato original foi
    enviado, e não a versão reescrita).
    """

    def __init__(self, output=None, falhar: bool = False):
        self.output = output
        self.falhar = falhar
        self.chamadas: list[dict] = []

    def classify(self, messages, output_model, **kwargs):
        self.chamadas.append(
            {
                "messages": messages,
                "output_model": output_model,
                **kwargs,
            }
        )

        if self.falhar:
            return LLMCallResult(
                output=None,
                raw="isto nao e json",
                json_parsed=False,
                schema_valid=False,
                attempts=2,
                done_reason="stop",
            )

        saida = self.output

        if saida is None:
            campos = {
                "classificacao": "EMERGENCIA",
                "justificativa": "sinais compatíveis com risco",
                "sinais_de_alerta": ["tremores"],
                "recomendacao": "procure atendimento",
            }

            if "fontes" in output_model.model_fields:
                campos["fontes"] = [1]

            saida = output_model(**campos)

        return LLMCallResult(
            output=saida,
            raw=saida.model_dump_json(),
            json_parsed=True,
            schema_valid=True,
            attempts=1,
            done_reason="stop",
            prompt_tokens=100,
            completion_tokens=50,
            eval_duration_s=1.0,
        )
