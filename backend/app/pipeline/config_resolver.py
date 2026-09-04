"""
Resolve a configuração efetiva de uma requisição.

Função pura, sem dependência de rede ou banco: recebe as settings e as opções
da requisição e devolve o que de fato vai rodar. Fica separada do pipeline
para poder ser testada sozinha, já que é ela que define a semântica de cada
braço do estudo de ablação.
"""

from app.core.config import Settings
from app.exceptions.pipeline_exception import UnsupportedOptionException
from app.schemas.triage import EffectiveConfig, PipelineOptions


# Etapas previstas na arquitetura que ainda não foram implementadas.
# Pedir uma delas é erro, não silêncio: uma etapa "ligada" que não roda
# produziria uma linha de ablação sem significado.
NOT_IMPLEMENTED_OPTIONS = {
    "cot_enabled": "Chain-of-Thought ainda não foi implementado.",
    "self_refine_enabled": "Self-Refine ainda não foi implementado.",
}


def _pick(override, default):
    """
    O valor da requisição vence; None significa "use o padrão".
    """

    return default if override is None else override


def resolve(
    settings: Settings,
    options: PipelineOptions | None = None,
) -> EffectiveConfig:

    options = options or PipelineOptions()

    for field, message in NOT_IMPLEMENTED_OPTIONS.items():
        if getattr(options, field, None):
            raise UnsupportedOptionException(message)

    prompt_version = _pick(
        options.prompt_version,
        settings.TRIAGE_PROMPT_VERSION,
    )

    structured_output_mode = _pick(
        options.structured_output_mode,
        settings.STRUCTURED_OUTPUT_MODE,
    )

    retrieval_enabled = _pick(
        options.retrieval_enabled,
        settings.RETRIEVAL_ENABLED,
    )

    num_predict = _pick(
        options.num_predict,
        settings.LLM_NUM_PREDICT,
    )

    # O modo legado existe para reproduzir a medição de 04/05, feita antes do
    # RAG: prompt antigo, sem documentos, saída apenas em JSON e sem teto de
    # tokens. Forçar aqui (em vez de confiar em quem chama) garante que a
    # configuração ecoada na resposta descreva o que realmente rodou.
    if prompt_version == "v0_legacy":
        retrieval_enabled = False
        structured_output_mode = "json"
        num_predict = -1

    query_rewriting_enabled = _pick(
        options.query_rewriting_enabled,
        settings.QUERY_REWRITING_ENABLED,
    )

    multi_query_enabled = _pick(
        options.multi_query_enabled,
        settings.MULTI_QUERY_ENABLED,
    )

    hyde_enabled = _pick(
        options.hyde_enabled,
        settings.HYDE_ENABLED,
    )

    # Sem busca não há consulta a otimizar. Zerar as três evita gastar
    # chamadas ao modelo e deixa o braço "LLM puro" honesto na configuração.
    if not retrieval_enabled:
        query_rewriting_enabled = False
        multi_query_enabled = False
        hyde_enabled = False

    return EffectiveConfig(
        query_rewriting_enabled=query_rewriting_enabled,
        multi_query_enabled=multi_query_enabled,
        hyde_enabled=hyde_enabled,
        retrieval_enabled=retrieval_enabled,
        context_top_k=_pick(
            options.context_top_k,
            settings.CONTEXT_TOP_K,
        ),
        context_min_score=_pick(
            options.context_min_score,
            settings.CONTEXT_MIN_SCORE,
        ),
        rewritten_hint_enabled=_pick(
            options.rewritten_hint_enabled,
            settings.REWRITTEN_HINT_ENABLED,
        ),
        cot_enabled=False,
        self_refine_enabled=False,
        prompt_version=prompt_version,
        structured_output_mode=structured_output_mode,
        model=settings.LLM_MODEL,
        temperature=_pick(
            options.temperature,
            settings.LLM_TEMPERATURE,
        ),
        seed=_pick(options.seed, settings.LLM_SEED),
        num_ctx=settings.LLM_NUM_CTX,
        num_predict=num_predict,
    )
