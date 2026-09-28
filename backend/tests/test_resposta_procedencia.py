"""
A resposta: a ficha citada com a fonte real, só o que o modelo viu, e quem
respondeu (rodada 25 do João).
"""

from pydantic import BaseModel

from conftest import LLMClientFalso, QueryClientFalso, RerankerFalso, RetrievalClientFalso, documento

from app.clients.llm_client import LLMClient
from app.core.config import settings
from app.pipeline.answer_renderer import render
from app.pipeline.chat_pipeline import ChatPipeline
from app.prompts.triage import montar_bloco_de_contexto
from app.schemas.triage import PipelineOptions
from app.schemas.triage_output import CitedSource, SourceReference, TriageResult


def montar(documentos, llm_client=None):
    llm_client = llm_client or LLMClientFalso()
    pipeline = ChatPipeline(
        query_client=QueryClientFalso(),
        retrieval_client=RetrievalClientFalso(documentos),
        reranker=RerankerFalso,
        llm_client=llm_client,
    )
    return pipeline, llm_client


def test_ficha_citada_mostra_o_documento_aprovado_com_titulo_real():
    """
    O tutor via "Feline abscess case" como fonte. Agora vê a ficha usada e o
    documento por trás dela, com título real, periódico, ano e DOI.
    """

    triagem = TriageResult(
        classificacao="EMERGENCIA",
        justificativa="Sinais de intoxicação.",
        recomendacao="Procure atendimento agora.",
        fontes=[
            CitedSource(
                index=1,
                chunk_id="ficha__chocolate_toxicosis",
                title="Ficha de triagem: Intoxicacao por chocolate",
                source="Ficha de triagem do time (mapa de assuntos)",
                display_title="Intoxicação por chocolate",
                references=[
                    SourceReference(
                        title="Household Food Items Toxic to Dogs and Cats",
                        journal="Frontiers in Veterinary Science",
                        year=2016,
                        doi="10.3389/fvets.2016.00026",
                        url="https://doi.org/10.3389/fvets.2016.00026",
                    )
                ],
            )
        ],
    )

    texto = render(triagem)

    assert (
        "- Intoxicação por chocolate — fonte: Household Food Items Toxic to "
        "Dogs and Cats (Frontiers in Veterinary Science, 2016). "
        "<https://doi.org/10.3389/fvets.2016.00026>"
    ) in texto
    assert "Ficha de triagem do time" not in texto


def test_endereco_que_nao_e_http_continua_escapado():
    """
    Só vira link o que tem cara de endereço http. A rodada 26 achou o DOI
    escapado ("https\\://"), o que quebrava o link na tela.
    """

    triagem = TriageResult(
        classificacao="EMERGENCIA",
        justificativa="x",
        recomendacao="y",
        fontes=[
            CitedSource(
                index=1,
                chunk_id="ficha__x",
                title="Ficha de triagem: X",
                source="Ficha de triagem do time (mapa de assuntos)",
                display_title="X",
                references=[SourceReference(title="Doc", url="javascript:alert(1)")],
            )
        ],
    )

    texto = render(triagem)

    assert "javascript\\:alert(1)" in texto
    assert "<javascript" not in texto


def test_trecho_da_base_academica_continua_citado_como_antes():
    triagem = TriageResult(
        classificacao="EMERGENCIA",
        justificativa="x",
        recomendacao="y",
        fontes=[CitedSource(index=1, chunk_id="c1", title="Protocolo", source="fonte.pdf")],
    )

    assert "- Protocolo (fonte.pdf)" in render(triagem)


def test_trecho_que_nao_coube_no_bloco_nao_e_fonte_nem_conta_como_usado():
    """
    O bloco de contexto tem teto de 4.000 caracteres. Até 25/09, o trecho que
    ficava inteiro de fora continuava listado como fonte e contado como usado.
    """

    documentos = [
        documento("primeiro", score=0.9, conteudo="x" * 3990),
        documento("cortado", score=0.8, conteudo="começo que ainda cabe " * 5),
        documento("fora", score=0.7, conteudo="nunca entra no prompt"),
    ]
    pipeline, llm_client = montar(documentos)

    resultado = pipeline.execute("relato")
    prompt = llm_client.chamadas[0]["messages"][-1]["content"]

    assert [item.document.chunk_id for item in resultado.sources] == ["primeiro", "cortado"]
    assert resultado.retrieval.used_count == 2
    assert "nunca entra no prompt" not in prompt
    assert "[3]" not in prompt


def test_o_bloco_de_contexto_continua_o_mesmo_quando_tudo_cabe():
    documentos = [documento("a", conteudo="texto a"), documento("b", conteudo="texto b")]

    assert montar_bloco_de_contexto(documentos) == (
        "[1] Protocolo — texto a\n\n[2] Protocolo — texto b"
    )


def test_a_resposta_diz_quem_respondeu_e_o_think_chega_ao_cliente():

    class LLMComProcedencia(LLMClientFalso):
        def classify(self, messages, output_model, **kwargs):
            resultado = super().classify(messages, output_model, **kwargs)
            resultado.provider = "ollama"
            resultado.model = "qwen3:8b"
            resultado.model_version = "sha256:abc"
            resultado.thinking = False
            return resultado

    llm = LLMComProcedencia()
    pipeline, _ = montar([documento()], llm_client=llm)

    resultado = pipeline.execute("relato", PipelineOptions(think=False))

    atendente = resultado.provenance.attendant
    assert (atendente.provider, atendente.model, atendente.model_version) == (
        "ollama",
        "qwen3:8b",
        "sha256:abc",
    )
    assert atendente.thinking is False
    assert atendente.fallback_from is None
    assert llm.chamadas[0]["think"] is False
    assert resultado.provenance.query_stage.calls == []


def test_think_padrao_e_falso():
    pipeline, llm_client = montar([documento()])

    resultado = pipeline.execute("relato")

    assert resultado.config.think is False
    assert llm_client.chamadas[0]["think"] is False


class _Saida(BaseModel):
    ok: bool


class _Modelo:
    model = settings.LLM_MODEL
    digest = "sha256:123"


class _Lista:
    models = [_Modelo()]


class _OllamaQueGuarda:

    def __init__(self):
        self.kwargs = None

    def list(self):
        return _Lista()

    def chat(self, **kwargs):
        self.kwargs = kwargs
        return {"message": {"content": '{"ok": true}', "thinking": None}}


def test_llm_client_manda_think_ao_ollama_e_registra_a_procedencia():
    ollama = _OllamaQueGuarda()

    resultado = LLMClient(client=ollama).classify(
        [{"role": "user", "content": "x"}], _Saida, think=False
    )

    assert ollama.kwargs["think"] is False
    assert resultado.provider == "ollama"
    assert resultado.model == settings.LLM_MODEL
    assert resultado.model_version == "sha256:123"
    assert resultado.thinking is False


def test_llm_client_sem_think_nao_manda_o_parametro():
    ollama = _OllamaQueGuarda()

    LLMClient(client=ollama).classify([{"role": "user", "content": "x"}], _Saida)

    assert "think" not in ollama.kwargs


def test_rastro_da_consulta_registra_a_queda_do_gemini(monkeypatch):
    from app.clients import hybrid_query_client as hibrido
    from app.exceptions.llm_exception import LLMException

    def falha(question):
        raise LLMException("cota")

    monkeypatch.setattr(hibrido.GeminiQueryClient, "rewrite", staticmethod(falha))
    monkeypatch.setattr(hibrido.QueryClient, "rewrite", staticmethod(lambda q: "reescrita pelo ollama"))

    rastro: list = []
    token = hibrido.QUERY_TRACE.set(rastro)
    try:
        assert hibrido.HybridQueryClient.rewrite("relato") == "reescrita pelo ollama"
    finally:
        hibrido.QUERY_TRACE.reset(token)

    assert rastro == [{"step": "rewrite", "provider": "ollama", "fallback_from": "gemini"}]
