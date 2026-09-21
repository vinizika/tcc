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

from app.constants.pipeline import DEFAULT_CONTEXT_MIN_SCORE
from app.pipeline.chat_pipeline import ChatPipeline
from app.prompts.triage import montar_bloco_de_contexto
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


def test_multi_query_ligado_funde_reescrita_e_variacoes(monkeypatch):
    """
    B-10: "ligado" é superconjunto de "desligado" — a reescrita não some da
    lista quando o multi-query traz variações. Validado contra coleções
    reais em evidencias/ryu/2026-09-17-06-medindo-consulta-nas-candidatas.md.
    """

    pipeline, _, retrieval_client, _ = montar()

    pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(hyde_enabled=False),
    )

    assert retrieval_client.chamadas == [
        ["consulta reescrita", "consulta 1", "consulta 2"]
    ]


def test_multi_query_ligado_nao_duplica_variacao_igual_a_reescrita():

    query_client = QueryClientFalso(
        rewritten="consulta reescrita",
        queries=["consulta reescrita", "consulta 2"],
    )

    pipeline, _, retrieval_client, _ = montar(query_client=query_client)

    pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(hyde_enabled=False),
    )

    assert retrieval_client.chamadas == [["consulta reescrita", "consulta 2"]]


def test_hyde_entra_como_consulta_adicional():

    pipeline, query_client, retrieval_client, _ = montar()

    pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(hyde_enabled=True),
    )

    assert query_client.hyde_calls == 1
    assert "documento hipotético" in retrieval_client.chamadas[0]


def test_multi_query_e_hyde_juntos_preservam_a_ordem_apesar_do_paralelismo():
    """
    B-07: Multi-Query e HyDE rodam em paralelo (as duas só dependem da
    reescrita, nunca uma da outra) — mas a ordem final da lista de
    consultas não pode depender de qual chamada termina primeiro.
    """

    pipeline, _, retrieval_client, _ = montar()

    pipeline.execute(
        "meu cachorro comeu chocolate",
        PipelineOptions(multi_query_enabled=True, hyde_enabled=True),
    )

    assert retrieval_client.chamadas == [
        [
            "consulta reescrita",
            "consulta 1",
            "consulta 2",
            "documento hipotético",
        ]
    ]


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


# ----------------------------------------------------------------------
# Chain-of-Thought
# ----------------------------------------------------------------------


def test_cot_usa_o_formato_com_raciocinio_primeiro():
    """
    A ordem dos campos no formato é o experimento: a gramática do Ollama
    emite na ordem declarada, então o raciocínio precisa vir antes da
    classificação para o modelo escrevê-lo antes de decidir.
    """

    pipeline, _, _, llm_client = montar([documento()])

    pipeline.execute("relato", PipelineOptions(cot_enabled=True))

    modelo = llm_client.chamadas[0]["output_model"]
    campos = list(modelo.model_json_schema()["properties"])

    assert campos[0] == "raciocinio"
    assert campos.index("raciocinio") < campos.index("classificacao")


def test_controle_post_hoc_usa_o_raciocinio_por_ultimo():

    pipeline, _, _, llm_client = montar([documento()])

    pipeline.execute(
        "relato",
        PipelineOptions(cot_enabled=True, cot_position="last"),
    )

    campos = list(
        llm_client.chamadas[0]["output_model"].model_json_schema()[
            "properties"
        ]
    )

    assert campos[-1] == "raciocinio"
    assert campos.index("classificacao") < campos.index("raciocinio")


def test_cot_sem_documentos_nao_tem_campo_de_fontes():
    """
    Mesma razão do braço sem raciocínio: não havendo o que citar, a
    restrição de formato impede o modelo de inventar um índice.
    """

    pipeline, _, _, llm_client = montar([])

    pipeline.execute(
        "relato",
        PipelineOptions(retrieval_enabled=False, cot_enabled=True),
    )

    modelo = llm_client.chamadas[0]["output_model"]

    assert "raciocinio" in modelo.model_fields
    assert "fontes" not in modelo.model_fields


def test_raciocinio_chega_ao_resultado():
    """
    É o que o runner grava e o que permite ler, depois, se o modelo marcou
    o sinal grave e mesmo assim concluiu errado.
    """

    pipeline, _, _, _ = montar([documento()])

    resultado = pipeline.execute("relato", PipelineOptions(cot_enabled=True))

    assert resultado.triage.raciocinio
    assert "Conclusão" in resultado.triage.raciocinio


def test_sem_cot_o_raciocinio_fica_nulo():
    """
    Nulo e não vazio: distingue "não usou raciocínio" de "raciocinou e não
    escreveu nada".
    """

    pipeline, _, _, _ = montar([documento()])

    resultado = pipeline.execute("relato")

    assert resultado.triage.raciocinio is None


def test_prompt_do_cot_so_aparece_quando_ligado():

    pipeline, _, _, llm_client = montar([documento()])

    pipeline.execute("relato")
    sem_cot = llm_client.chamadas[0]["messages"][0]["content"]

    pipeline.execute("relato", PipelineOptions(cot_enabled=True))
    com_cot = llm_client.chamadas[1]["messages"][0]["content"]

    assert "risco à vida?" not in sem_cot
    assert "risco à vida?" in com_cot
    assert "Conclusão:" in com_cot


def test_cot_com_contexto_pede_para_julgar_cada_trecho():
    """
    É o passo que mira o mecanismo do B-01: com a base atual o modelo
    rebaixa emergências por causa de trechos que tratam de outro problema.
    """

    pipeline, _, _, llm_client = montar([documento()])

    pipeline.execute("relato", PipelineOptions(cot_enabled=True))
    com_documentos = llm_client.chamadas[0]["messages"][0]["content"]

    pipeline.execute(
        "relato",
        PipelineOptions(retrieval_enabled=False, cot_enabled=True),
    )
    sem_documentos = llm_client.chamadas[1]["messages"][0]["content"]

    assert "descreve o caso deste relato?" in com_documentos
    assert "descreve o caso deste relato?" not in sem_documentos


def test_modo_legado_ignora_o_cot_no_formato():

    pipeline, _, _, llm_client = montar([documento()])

    pipeline.execute(
        "relato",
        PipelineOptions(prompt_version="v0_legacy", cot_enabled=True),
    )

    modelo = llm_client.chamadas[0]["output_model"]

    assert "raciocinio" not in modelo.model_fields


# ----------------------------------------------------------------------
# Corte de relevância (evidencias/backlog.md#b-11)
# ----------------------------------------------------------------------


def test_por_padrao_o_trecho_irrelevante_nao_entra_no_prompt():
    """
    Até 12/09 o corte era zero e qualquer trecho entrava, por mais distante
    que fosse do relato. A rodada 9 mediu o custo disso: nas 98 linhas do
    conjunto nenhum trecho passava de 0,70, e três entravam em todos os
    prompts — os braços com RAG mediram injeção de ruído.
    """

    documentos = [
        documento("relevante", score=0.75),
        documento("irrelevante", score=0.60),
    ]

    pipeline, _, _, _ = montar(documentos)

    resultado = pipeline.execute("relato")

    assert [item.document.chunk_id for item in resultado.sources] == [
        "relevante"
    ]


def test_nada_relevante_e_o_classificador_decide_sem_contexto():
    """
    O caso central desta correção, e o estado real do sistema hoje: a busca
    roda, devolve trechos, e nenhum é bom o bastante. O classificador
    precisa receber **nada** — e não os três mais próximos — respondendo
    como no braço sem RAG.
    """

    documentos = [
        documento("fraco1", score=0.57),
        documento("fraco2", score=0.55),
        documento("fraco3", score=0.51),
    ]

    pipeline, _, _, llm_client = montar(documentos)

    resultado = pipeline.execute("relato")

    info = resultado.retrieval

    # A busca rodou e trouxe coisa: o problema não é base vazia.
    assert info.returned_count == 3
    assert info.used_count == 0
    assert info.above_threshold_count == 0

    assert resultado.sources == []

    # Sem trechos, o formato de saída não tem campo de fontes — a restrição
    # de formato impede o modelo de inventar um índice.
    assert "fontes" not in llm_client.chamadas[0]["output_model"].model_fields

    # E o prompt não traz bloco de contexto nenhum.
    prompt = llm_client.chamadas[0]["messages"][-1]["content"]
    assert "Trechos de protocolos" not in prompt


def test_contexto_destaca_encaminhamento_emergencial_explicito():
    trecho = documento("urgente", score=0.9)
    trecho.content = (
        "Vomiting and lethargy were associated with emergency referral."
    )

    contexto = montar_bloco_de_contexto([trecho])

    assert "MENCIONA EXPLICITAMENTE ENCAMINHAMENTO EMERGENCIAL" in contexto
    assert trecho.content in contexto


def test_contexto_nao_rotula_trecho_sem_linguagem_emergencial():
    trecho = documento("neutro", score=0.9)
    trecho.content = "Vomiting was recorded in the study population."

    contexto = montar_bloco_de_contexto([trecho])

    assert "ENCAMINHAMENTO EMERGENCIAL" not in contexto


def test_o_corte_aplicado_vai_na_resposta_com_a_trava_de_auditoria():
    """
    `used_below_min_score` nunca pode ser verdadeiro. Se for, o filtro
    quebrou e um trecho irrelevante chegou ao classificador — e o runner
    pega isso na linha, não semanas depois na leitura da evidência.
    """

    documentos = [
        documento("forte", score=0.9),
        documento("fraco", score=0.3),
    ]

    pipeline, _, _, _ = montar(documentos)

    info = pipeline.execute("relato").retrieval

    assert info.context_min_score == DEFAULT_CONTEXT_MIN_SCORE
    assert info.used_below_min_score is False


def test_o_braco_antigo_continua_reproduzivel_com_corte_zero():
    """
    As rodadas citadas até 11/09 usaram corte zero. Elas precisam continuar
    reproduzíveis, ou a comparação com o histórico se perde.
    """

    documentos = [
        documento("fraco1", score=0.57),
        documento("fraco2", score=0.55),
    ]

    pipeline, _, _, _ = montar(documentos)

    resultado = pipeline.execute(
        "relato",
        PipelineOptions(context_min_score=0.0),
    )

    assert len(resultado.sources) == 2
    assert resultado.retrieval.context_min_score == 0.0
    assert resultado.retrieval.used_below_min_score is False
