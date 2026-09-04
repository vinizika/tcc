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

    # O prompt cita os trechos numerados; com corte em 2, so [1] e [2].
    prompt = llm_client.chamadas[0]["messages"][-1]["content"]
    assert "[1]" in prompt and "[2]" in prompt
    assert "[3]" not in prompt


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


# ----------------------------------------------------------------------
# Etapa de decisão
# ----------------------------------------------------------------------


def test_o_relato_original_vai_ao_classificador():
    """
    A reescrita acrescenta interpretação clínica ("requer avaliação
    imediata"). Usá-la na decisão misturaria a etapa de consulta dentro do
    resultado da classificação e confundiria o estudo de ablação.
    """

    pipeline, _, _, llm_client = montar([documento()])

    pipeline.execute("meu cachorro comeu chocolate")

    prompt = llm_client.chamadas[0]["messages"][-1]["content"]

    assert "meu cachorro comeu chocolate" in prompt
    assert "consulta reescrita" not in prompt


def test_a_dica_da_reescrita_entra_apenas_quando_ligada():

    pipeline, _, _, llm_client = montar([documento()])

    pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(rewritten_hint_enabled=True),
    )

    prompt = llm_client.chamadas[0]["messages"][-1]["content"]

    assert "consulta reescrita" in prompt


def test_sem_documentos_usa_o_formato_sem_campo_de_fontes():
    """
    Não havendo o que citar, a restrição de formato impede o modelo de
    inventar um número de fonte.
    """

    pipeline, _, _, llm_client = montar([])

    pipeline.execute("relato", PipelineOptions(retrieval_enabled=False))

    modelo = llm_client.chamadas[0]["output_model"]

    assert "fontes" not in modelo.model_fields


def test_fonte_citada_e_resolvida_para_o_documento():

    pipeline, _, _, _ = montar(
        [documento("chunk-chocolate", "Intoxicação por chocolate", 0.8)]
    )

    resultado = pipeline.execute("relato")

    assert resultado.triage.fontes[0].chunk_id == "chunk-chocolate"
    assert resultado.triage.fontes[0].index == 1
    assert resultado.sources[0].cited is True


def test_indice_de_fonte_inexistente_e_descartado_e_contado():
    """
    Citar um número que não existe é fonte inventada: não pode aparecer na
    tela, mas precisa virar métrica de ancoragem.
    """

    from app.schemas.triage_output import TriageLLMOutput
    from conftest import LLMClientFalso as Falso

    saida = TriageLLMOutput(
        classificacao="EMERGENCIA",
        justificativa="x",
        sinais_de_alerta=[],
        recomendacao="y",
        fontes=[1, 9],
    )

    pipeline, _, _, _ = montar(
        [documento("c1", score=0.8)],
        llm_client=Falso(output=saida),
    )

    resultado = pipeline.execute("relato")

    assert [f.index for f in resultado.triage.fontes] == [1]
    assert resultado.triage.invalid_source_indices == [9]


def test_falha_do_modelo_vira_incerto_conservador():
    """
    Duas tentativas sem resposta válida não podem virar uma classificação
    arriscada. O sistema assume que não sabe e orienta procurar atendimento.
    """

    from conftest import LLMClientFalso as Falso

    pipeline, _, _, _ = montar([], llm_client=Falso(falhar=True))

    resultado = pipeline.execute("relato")

    assert resultado.triage.classificacao == "INCERTO"
    assert resultado.triage.schema_valid is False
    assert "veterinário" in resultado.triage.recomendacao
    assert resultado.answer


def test_modo_legado_usa_o_prompt_antigo_sem_documentos():

    pipeline, _, _, llm_client = montar([documento()])

    pipeline.execute("relato", PipelineOptions(prompt_version="v0_legacy"))

    chamada = llm_client.chamadas[0]
    mensagens = chamada["messages"]

    assert len(mensagens) == 1
    assert mensagens[0]["role"] == "user"
    assert "não informado" in mensagens[0]["content"]
    assert chamada["mode"] == "json"


def test_tokens_da_geracao_sao_reportados():

    pipeline, _, _, _ = montar([documento()])

    resultado = pipeline.execute("relato")

    assert resultado.timings.prompt_tokens == 100
    assert resultado.timings.completion_tokens == 50
    assert resultado.timings.tokens_per_s == 50.0
