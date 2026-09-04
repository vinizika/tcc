from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.triage import (
    DebugInfo,
    EffectiveConfig,
    PipelineOptions,
    RetrievalInfo,
    Timings,
)
from app.schemas.triage_output import TriageResult


class ChatRequest(BaseModel):

    question: str = Field(min_length=1, max_length=4000)

    # Sobrescreve as etapas do pipeline nesta requisição. Usado pelo runner
    # de avaliação para rodar cada braço do estudo de ablação sem reiniciar
    # o backend.
    options: Optional[PipelineOptions] = None

    @field_validator("question")
    @classmethod
    def question_nao_pode_ser_so_espaco(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError("O relato não pode estar vazio.")

        return value


class SourceResponse(BaseModel):

    title: str
    source: str
    score: float

    # Identifica o trecho exato, para o runner conferir se a resposta se
    # apoiou no protocolo certo.
    chunk_id: str = ""

    # Se o modelo citou este trecho na resposta.
    cited: bool = False


class ChatResponse(BaseModel):

    answer: str
    sources: list[SourceResponse]

    # A classificacao estruturada. O texto em "answer" e uma renderizacao
    # dela; quem consome a API por programa deve ler daqui.
    triage: Optional[TriageResult] = None

    # Campos aditivos: o frontend atual usa apenas "answer" e continua
    # funcionando. Servem à avaliação e ao frontend que virá.
    config: Optional[EffectiveConfig] = None
    retrieval: Optional[RetrievalInfo] = None
    timings: Optional[Timings] = None
    debug: Optional[DebugInfo] = None
