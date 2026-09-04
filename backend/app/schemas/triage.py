"""
Modelos de configuração e de instrumentação do pipeline de triagem.

Aqui ficam as estruturas que descrevem *como* uma requisição foi processada
(quais etapas rodaram, com quais parâmetros, quanto tempo cada uma levou e o
que a busca encontrou). Os modelos da saída clínica do LLM ficam neste mesmo
arquivo a partir da etapa de geração real.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


PromptVersion = Literal["v0_legacy", "v1_grounded"]

StructuredOutputMode = Literal["schema", "json"]


class PipelineOptions(BaseModel):
    """
    Sobrescreve, por requisição, as configurações do pipeline.

    Todo campo é opcional: o que vier como None usa o padrão das settings.
    Isso existe para o estudo de ablação — cada combinação de etapas ligadas
    e desligadas é uma requisição diferente, sem reiniciar o backend.

    extra="forbid" faz um nome errado virar erro 422 em vez de ser ignorado
    em silêncio, o que na avaliação produziria uma linha sem significado.
    """

    model_config = ConfigDict(extra="forbid")

    # Etapas de consulta (trilho B1)
    query_rewriting_enabled: Optional[bool] = None
    multi_query_enabled: Optional[bool] = None
    hyde_enabled: Optional[bool] = None

    # Etapas de decisão (trilho B2)
    retrieval_enabled: Optional[bool] = None
    context_top_k: Optional[int] = Field(default=None, ge=1, le=10)
    context_min_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    rewritten_hint_enabled: Optional[bool] = None
    cot_enabled: Optional[bool] = None
    self_refine_enabled: Optional[bool] = None

    # Geração
    prompt_version: Optional[PromptVersion] = None
    structured_output_mode: Optional[StructuredOutputMode] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    seed: Optional[int] = None
    num_predict: Optional[int] = Field(default=None, ge=-1)

    include_debug: bool = False


class EffectiveConfig(BaseModel):
    """
    O que de fato rodou. Vai na resposta para que o runner de avaliação
    registre a configuração real de cada rodada, e não a que ele pediu.
    """

    query_rewriting_enabled: bool
    multi_query_enabled: bool
    hyde_enabled: bool

    retrieval_enabled: bool
    context_top_k: int
    context_min_score: float
    rewritten_hint_enabled: bool
    cot_enabled: bool
    self_refine_enabled: bool

    prompt_version: PromptVersion
    structured_output_mode: StructuredOutputMode

    model: str
    temperature: float
    seed: int
    num_ctx: int
    num_predict: int


class RetrievalInfo(BaseModel):
    """
    Informações da busca, fora do bloco de debug de propósito: o runner
    precisa delas em toda linha para separar "a geração errou" de "a
    recuperação não trouxe nada de útil".
    """

    returned_count: int = 0
    used_count: int = 0
    above_threshold_count: int = 0
    max_score: Optional[float] = None
    threshold: float = 0.0


class Timings(BaseModel):

    query_s: float = 0.0
    retrieval_s: float = 0.0
    generation_s: float = 0.0
    total_s: float = 0.0

    prompt_tokens: int = 0
    completion_tokens: int = 0
    tokens_per_s: Optional[float] = None
    load_duration_s: Optional[float] = None


class DebugSource(BaseModel):

    chunk_id: str
    title: str
    source: str
    score: float


class DebugInfo(BaseModel):
    """
    Preenchido apenas quando a requisição pede include_debug=true.
    """

    rewritten_question: Optional[str] = None
    queries: list[str] = []
    hypothetical_document: Optional[str] = None
    all_sources: list[DebugSource] = []
    raw_llm_output: Optional[str] = None
