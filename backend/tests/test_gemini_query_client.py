"""
GeminiQueryClient espelha QueryClient (mesmos prompts, mesma interface).
Estes testes usam um cliente Gemini falso — não precisam do pacote
`google-genai` instalado nem de rede.
"""

from app.clients.gemini_query_client import GeminiQueryClient
from app.exceptions.llm_exception import LLMException

import pytest


class _RespostaFalsa:

    def __init__(self, texto: str):
        self.text = texto


class _ModelsFalso:

    def __init__(self, texto: str = "resposta", erro: Exception | None = None):
        self.texto = texto
        self.erro = erro
        self.chamadas: list[dict] = []

    def generate_content(self, **kwargs):
        self.chamadas.append(kwargs)
        if self.erro:
            raise self.erro
        return _RespostaFalsa(self.texto)


class _ClienteGeminiFalso:

    def __init__(self, texto: str = "resposta", erro: Exception | None = None):
        self.models = _ModelsFalso(texto, erro)


class _ErroLimiteExcedido(Exception):
    code = 429


def test_rewrite_usa_o_mesmo_prompt_do_query_client(monkeypatch):

    from app.clients.query_client import REWRITE_SYSTEM_PROMPT

    cliente_falso = _ClienteGeminiFalso("cão com taquipneia e cianose")
    monkeypatch.setattr(GeminiQueryClient, "_client", cliente_falso)

    GeminiQueryClient.rewrite("meu cachorro esta ofegante")

    config = cliente_falso.models.chamadas[0]["config"]
    assert config["system_instruction"] == REWRITE_SYSTEM_PROMPT


def test_rewrite_descarta_termo_de_urgencia_nao_presente_no_relato(monkeypatch):

    cliente_falso = _ClienteGeminiFalso(
        "gato apresentando espirro, sintoma que requer avaliação "
        "veterinária imediata"
    )
    monkeypatch.setattr(GeminiQueryClient, "_client", cliente_falso)

    resultado = GeminiQueryClient.rewrite("meu gato está espirrando")

    assert resultado == "meu gato está espirrando"


def test_generate_queries_parseia_ate_tres_linhas(monkeypatch):

    cliente_falso = _ClienteGeminiFalso("consulta 1\nconsulta 2\nconsulta 3\nconsulta 4")
    monkeypatch.setattr(GeminiQueryClient, "_client", cliente_falso)

    queries = GeminiQueryClient.generate_queries("relato do tutor")

    assert queries == ["consulta 1", "consulta 2", "consulta 3"]


def test_generate_hypothetical_document(monkeypatch):

    cliente_falso = _ClienteGeminiFalso("trecho de protocolo clínico")
    monkeypatch.setattr(GeminiQueryClient, "_client", cliente_falso)

    resultado = GeminiQueryClient.generate_hypothetical_document("relato do tutor")

    assert resultado == "trecho de protocolo clínico"


def test_limite_excedido_vira_llmexception_clara(monkeypatch):

    cliente_falso = _ClienteGeminiFalso(erro=_ErroLimiteExcedido("RESOURCE_EXHAUSTED"))
    monkeypatch.setattr(GeminiQueryClient, "_client", cliente_falso)

    with pytest.raises(LLMException, match="Limite gratuito do Gemini atingido"):
        GeminiQueryClient.rewrite("meu cachorro comeu chocolate")


def test_sem_chave_configurada_recusa_com_mensagem_clara(monkeypatch):

    monkeypatch.setattr(GeminiQueryClient, "_client", None)
    monkeypatch.setattr("app.clients.gemini_query_client.settings.GEMINI_API_KEY", "")

    with pytest.raises(LLMException, match="GEMINI_API_KEY"):
        GeminiQueryClient.rewrite("meu cachorro comeu chocolate")
