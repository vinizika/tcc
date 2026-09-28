from typing import Literal

from pydantic import BaseModel


class SearchRequest(BaseModel):
    question: str
    # Sem modo, vale o RETRIEVAL_MODE das settings (padrão "vector").
    mode: Literal["vector", "routed_rerank"] | None = None


class SearchDocument(BaseModel):
    id: str
    title: str
    content: str
    source: str
    score: float
    ranking_score: float | None = None

    # Procedência do trecho. O título é texto livre e muda quando o
    # documento é reescrito; `topic` é o identificador estável do assunto e
    # `source_file` diz de qual arquivo o trecho saiu. A régua de
    # recuperação julga por eles, em vez de casar títulos por string.
    topic: str = ""
    source_file: str = ""


class SearchResponse(BaseModel):
    documents: list[SearchDocument]
