"""
O pipeline decide quais etapas rodam. Estes testes usam dublês para
verificar essas decisões sem depender de Ollama nem do banco vetorial.
"""

from conftest import (
    LLMClientFalso,
    QueryClientFalso,
    RerankerFalso,
    RetrievalClientFalso,
    documento,
)

from app.pipeline.chat_pipeline import ChatPipeline
from app.schemas.triage import PipelineOptions


def montar(documentos=None, **falsos):

    query_client = falsos.get("query_client") or QueryClientFalso()
    retrieval_client = falsos.get("retrieval_client") or (
        RetrievalClientFalso(documentos or [])
    )
    llm_client = falsos.get("llm_client") or LLMClientFalso()

    pipeline = ChatPipeline(
        query_client=query_client,
        retrieval_client=retrieval_client,
        reranker=RerankerFalso,
        llm_client=llm_client,
    )

    return pipeline, query_client, retrieval_client, llm_client


def test_sem_busca_nenhuma_etapa_de_consulta_roda():
    """
    O braço "LLM puro" é a linha de base do estudo de ablação: ele não pode
    gastar chamadas ao modelo com reescrita nem tocar o banco vetorial.
    """

    pipeline, query_client, retrieval_client, _ = montar()

    resultado = pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(retrieval_enabled=False),
    )

    assert query_client.rewrite_calls == 0
    assert query_client.generate_queries_calls == 0
    assert query_client.hyde_calls == 0
    assert retrieval_client.chamadas == []
    assert resultado.sources == []
    assert resultado.retrieval.returned_count == 0


def test_reescrita_desligada_manda_o_relato_original_para_a_busca():

    pipeline, query_client, retrieval_client, _ = montar()

    pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(
            query_rewriting_enabled=False,
            multi_query_enabled=False,
            hyde_enabled=False,
        ),
    )

    assert query_client.rewrite_calls == 0
    assert retrieval_client.chamadas == [["meu cachorro comeu chocolate"]]


def test_multi_query_desligado_busca_apenas_a_consulta_reescrita():

    pipeline, query_client, retrieval_client, _ = montar()

    pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(multi_query_enabled=False, hyde_enabled=False),
    )

    assert query_client.generate_queries_calls == 0
    assert retrieval_client.chamadas == [["consulta reescrita"]]


def test_multi_query_vazio_nao_deixa_a_busca_sem_consulta():
    """
    O modelo pode devolver nada. Buscar com lista vazia devolveria zero
    documentos e pareceria falha da recuperação.
    """

    query_client = QueryClientFalso(queries=[])

    pipeline, _, retrieval_client, _ = montar(query_client=query_client)

    pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(hyde_enabled=False),
    )

    assert retrieval_client.chamadas == [["consulta reescrita"]]


def test_hyde_entra_como_consulta_adicional():

    pipeline, query_client, retrieval_client, _ = montar()

    pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(hyde_enabled=True),
    )

    assert query_client.hyde_calls == 1
    assert "documento hipotético" in retrieval_client.chamadas[0]


def test_apenas_os_melhores_trechos_vao_ao_prompt():

    documentos = [
        documento("c1", score=0.9),
        documento("c2", score=0.8),
        documento("c3", score=0.7),
        documento("c4", score=0.6),
    ]

    pipeline, _, _, llm_client = montar(documentos)

    resultado = pipeline.execute(
        "relato",
        PipelineOptions(context_top_k=2),
    )

    assert [item.document.chunk_id for item in resultado.sources] == [
        "c1",
        "c2",
    ]

    _, documentos_no_prompt = llm_client.chamadas[0]
    assert len(documentos_no_prompt) == 2


def test_corte_por_score_minimo_descarta_trecho_fraco():

    documentos = [
        documento("forte", score=0.75),
        documento("fraco", score=0.20),
    ]

    pipeline, _, _, _ = montar(documentos)

    resultado = pipeline.execute(
        "relato",
        PipelineOptions(context_min_score=0.5),
    )

    assert [item.document.chunk_id for item in resultado.sources] == [
        "forte"
    ]


def test_estatisticas_da_busca_descrevem_tudo_que_foi_recuperado():
    """
    O runner precisa distinguir "a geração errou" de "a busca não trouxe
    nada útil", então estes números cobrem o resultado inteiro da busca, e
    não apenas o recorte que foi ao prompt.
    """

    documentos = [
        documento("c1", score=0.85),
        documento("c2", score=0.40),
        documento("c3", score=0.30),
    ]

    pipeline, _, _, _ = montar(documentos)

    resultado = pipeline.execute(
        "relato",
        PipelineOptions(context_top_k=1),
    )

    info = resultado.retrieval

    assert info.returned_count == 3
    assert info.used_count == 1
    assert info.above_threshold_count == 1
    assert info.max_score == 0.85
    assert info.threshold == 0.70


def test_sem_documentos_o_pipeline_ainda_responde():

    pipeline, _, _, _ = montar([])

    resultado = pipeline.execute("relato")

    assert resultado.answer
    assert resultado.sources == []
    assert resultado.retrieval.max_score is None


def test_debug_so_aparece_quando_pedido():

    pipeline, _, _, _ = montar([documento()])

    sem_debug = pipeline.execute("relato")
    assert sem_debug.debug is None

    com_debug = pipeline.execute(
        "relato",
        PipelineOptions(include_debug=True),
    )

    assert com_debug.debug is not None
    assert com_debug.debug.rewritten_question == "consulta reescrita"
    assert com_debug.debug.queries
    assert len(com_debug.debug.all_sources) == 1


def test_tempos_e_configuracao_efetiva_sao_reportados():

    pipeline, _, _, _ = montar([documento()])

    resultado = pipeline.execute("relato")

    assert resultado.timings.total_s >= 0.0
    assert resultado.config.model == "llama3.2:3b"
    assert resultado.config.retrieval_enabled is True
