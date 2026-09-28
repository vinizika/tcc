"""
O Gemini como atendente e a regra "nunca trocar de modelo em silêncio"
(rodada 26 do João). Nada aqui chama a rede: o SDK é substituído por um
dublê que devolve respostas e erros no formato do `google-genai`.
"""

import pytest
from fastapi.testclient import TestClient
from google.genai import errors as genai_errors

from conftest import LLMClientFalso, QueryClientFalso, RerankerFalso, RetrievalClientFalso, documento

from app.api.deps import get_chat_pipeline
from app.clients import gemini_llm_client as modulo
from app.clients.gemini_llm_client import LEMBRETE_DE_FORMATO, GeminiLLMClient
from app.core.config import Settings, settings
from app.exceptions.attendant_exception import (
    AttendantUnavailableException,
    QuotaExhaustedException,
)
from app.exceptions.pipeline_exception import UnsupportedOptionException
from app.main import app
from app.pipeline.chat_pipeline import ChatPipeline
from app.pipeline.config_resolver import resolve
from app.schemas.triage import PipelineOptions
from app.schemas.triage_output import TriageLLMOutput

JSON_OK = (
    '{"classificacao": "EMERGENCIA", "justificativa": "risco", '
    '"sinais_de_alerta": [], "recomendacao": "vá agora", "fontes": [1]}'
)


class _Uso:
    prompt_token_count = 120
    candidates_token_count = 30


class _Resposta:
    def __init__(self, texto):
        self.text = texto
        self.model_version = "gemini-3.5-flash-lite-001"
        self.usage_metadata = _Uso()


class _Modelos:
    def __init__(self, roteiro):
        self.roteiro = list(roteiro)
        self.chamadas = []

    def generate_content(self, *, model, contents, config):
        self.chamadas.append({"model": model, "contents": contents, "config": config})
        proximo = self.roteiro.pop(0)
        if isinstance(proximo, Exception):
            raise proximo
        return _Resposta(proximo)


class GenaiClientFalso:
    def __init__(self, roteiro):
        self.models = _Modelos(roteiro)


def _cliente(roteiro, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_MIN_INTERVAL_S", 0.0)
    esperas = []
    cliente = GeminiLLMClient(client=GenaiClientFalso(roteiro), dormir=esperas.append)
    return cliente, esperas


MENSAGENS = [{"role": "system", "content": "sistema"}, {"role": "user", "content": "relato"}]


def _erro_429(por_dia: bool):
    quota = "GenerateRequestsPerDayPerProjectPerModel-FreeTier" if por_dia else "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
    return genai_errors.ClientError(
        429, {"error": {"code": 429, "message": f"quota exceeded, quotaId: '{quota}'", "status": "RESOURCE_EXHAUSTED"}}
    )


def test_resposta_valida_registra_provedor_modelo_e_versao(monkeypatch):
    cliente, _ = _cliente([JSON_OK], monkeypatch)

    resultado = cliente.classify(MENSAGENS, TriageLLMOutput, options={"temperature": 0.0, "seed": 42, "num_predict": 600})

    assert resultado.schema_valid and resultado.attempts == 1
    assert (resultado.provider, resultado.model) == ("gemini", settings.GEMINI_MODEL)
    assert resultado.model_version == "gemini-3.5-flash-lite-001"
    chamada = cliente._client.models.chamadas[0]
    assert chamada["config"].system_instruction == "sistema"
    assert chamada["config"].temperature == 0.0
    assert chamada["config"].seed == 42
    assert chamada["contents"] == "relato"


def test_saida_invalida_duas_vezes_vira_incerto_no_pipeline(monkeypatch):
    cliente, _ = _cliente(["", "isto não é json"], monkeypatch)

    resultado = cliente.classify(MENSAGENS, TriageLLMOutput)

    assert resultado.output is None and resultado.attempts == 2
    assert cliente._client.models.chamadas[1]["contents"].endswith(LEMBRETE_DE_FORMATO)


def test_limite_por_minuto_espera_e_tenta_de_novo(monkeypatch):
    cliente, esperas = _cliente([_erro_429(por_dia=False), JSON_OK], monkeypatch)

    resultado = cliente.classify(MENSAGENS, TriageLLMOutput)

    assert resultado.schema_valid
    assert esperas == [5.0]


def test_cota_do_dia_para_na_hora_sem_esperar(monkeypatch):
    cliente, esperas = _cliente([_erro_429(por_dia=True)], monkeypatch)

    with pytest.raises(QuotaExhaustedException):
        cliente.classify(MENSAGENS, TriageLLMOutput)
    assert esperas == []


def test_servidor_sem_capacidade_desiste_depois_do_teto(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_MAX_RETRIES_503", 2)
    erro = genai_errors.ServerError(503, {"error": {"code": 503, "message": "high demand"}})
    cliente, esperas = _cliente([erro, erro, erro], monkeypatch)

    with pytest.raises(AttendantUnavailableException) as falha:
        cliente.classify(MENSAGENS, TriageLLMOutput)
    assert falha.value.details["reason"] == "server_unavailable"
    assert esperas == [20.0, 40.0]


def test_sem_chave_falha_explicando_como_rodar_local(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    with pytest.raises(AttendantUnavailableException) as falha:
        GeminiLLMClient().classify(MENSAGENS, TriageLLMOutput)
    assert falha.value.details["reason"] == "missing_api_key"
    assert "ATTENDANT_PROVIDER=ollama" in falha.value.message


def test_a_chave_nunca_aparece_na_mensagem_de_erro():
    from app.clients.gemini_common import sem_chave

    assert "AIza" not in sem_chave("falhou com key=AIzaSyA1234567890abcdefghijklmnop")


# ----------------------------------------------------------------------
# Sem troca silenciosa
# ----------------------------------------------------------------------


class _AtendenteQueFalha:
    def classify(self, messages, output_model, **kwargs):
        raise AttendantUnavailableException("sem cota", provider="gemini", model="gemini-3.5-flash-lite", reason="daily_quota")


def _pipeline_com(atendentes):
    pipeline = ChatPipeline(
        query_client=QueryClientFalso(),
        retrieval_client=RetrievalClientFalso([documento()]),
        reranker=RerankerFalso,
    )
    pipeline._atendentes.update(atendentes)
    return pipeline


def test_gemini_falhou_sem_troca_permitida_a_requisicao_falha(monkeypatch):
    monkeypatch.setattr(settings, "ATTENDANT_FALLBACK", "none")
    ollama = LLMClientFalso()
    pipeline = _pipeline_com({"gemini": _AtendenteQueFalha(), "ollama": ollama})

    with pytest.raises(AttendantUnavailableException):
        pipeline.execute("relato", PipelineOptions(attendant_provider="gemini"))
    assert ollama.chamadas == []


def test_gemini_falhou_com_troca_permitida_responde_pelo_ollama_e_diz(monkeypatch):
    monkeypatch.setattr(settings, "ATTENDANT_FALLBACK", "ollama")
    ollama = LLMClientFalso()
    pipeline = _pipeline_com({"gemini": _AtendenteQueFalha(), "ollama": ollama})

    resultado = pipeline.execute("relato", PipelineOptions(attendant_provider="gemini"))

    assert len(ollama.chamadas) == 1
    assert resultado.provenance.attendant.fallback_from == "gemini:gemini-3.5-flash-lite"
    assert "Aviso: o atendente configurado" in resultado.answer


def test_api_responde_503_com_o_codigo_da_cota(monkeypatch):
    monkeypatch.setattr(settings, "ATTENDANT_FALLBACK", "none")
    app.dependency_overrides[get_chat_pipeline] = lambda: _pipeline_com({"gemini": _AtendenteQueFalha()})
    try:
        with TestClient(app) as cliente:
            resposta = cliente.post("/chat/", json={"question": "meu cão comeu chocolate", "options": {"attendant_provider": "gemini"}})
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 503
    corpo = resposta.json()
    assert corpo["code"] == "attendant_unavailable"
    assert corpo["details"] == {"provider": "gemini", "model": "gemini-3.5-flash-lite", "reason": "daily_quota"}


def test_padroes_escolhem_o_gemini_e_o_qwen_como_local():
    padroes = Settings(_env_file=None)
    config = resolve(padroes, None)

    assert (config.attendant_provider, config.model, config.attendant_fallback) == (
        "gemini",
        "gemini-3.5-flash-lite",
        "none",
    )
    assert padroes.LLM_MODEL == "qwen3:8b"
    local = resolve(padroes, PipelineOptions(attendant_provider="ollama", llm_model="llama3.2:3b"))
    assert (local.attendant_provider, local.model) == ("ollama", "llama3.2:3b")


def test_modelo_local_com_o_gemini_e_recusado():
    with pytest.raises(UnsupportedOptionException):
        resolve(Settings(_env_file=None), PipelineOptions(attendant_provider="gemini", llm_model="qwen3:8b"))


def test_o_modulo_do_gemini_nunca_importa_o_cliente_do_ollama():
    fonte = open(modulo.__file__, encoding="utf-8").read()

    assert "LLMClient(" not in fonte and "get_ollama_client" not in fonte
