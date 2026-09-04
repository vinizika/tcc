"""
Resultado interno do pipeline.

O pipeline devolve esta estrutura, e a camada de serviço a traduz para o
schema da API. Assim o pipeline não precisa conhecer o formato da resposta
HTTP, e os testes podem verificar a lógica sem passar por FastAPI.
"""

from dataclasses import dataclass, field
from typing import Optional

from app.models.retrieved_document import RetrievedDocument
from app.schemas.triage import (
    DebugInfo,
    EffectiveConfig,
    RetrievalInfo,
    Timings,
)


@dataclass
class ContextDocument:
    """
    Um trecho que foi efetivamente ao prompt, e se o modelo o citou.
    """

    document: RetrievedDocument
    cited: bool = False


@dataclass
class QueryPlan:
    """
    Saída da etapa de consulta (trilho B1), isolada em um só lugar para que
    mudanças na interface daquele trilho não se espalhem pelo pipeline.
    """

    rewritten: str
    queries: list[str] = field(default_factory=list)
    hypothetical_document: Optional[str] = None


@dataclass
class PipelineResult:

    answer: str
    sources: list[ContextDocument]
    config: EffectiveConfig
    timings: Timings
    retrieval: RetrievalInfo
    triage: Optional[object] = None
    debug: Optional[DebugInfo] = None
