from pydantic import BaseModel


class SearchRequest(BaseModel):
    question: str


class SearchDocument(BaseModel):
    id: str
    title: str
    content: str
    source: str
    score: float

    # Procedência do trecho. O título é texto livre e muda quando o
    # documento é reescrito; `topic` é o identificador estável do assunto e
    # `source_file` diz de qual arquivo o trecho saiu. A régua de
    # recuperação julga por eles, em vez de casar títulos por string.
    topic: str = ""
    source_file: str = ""


class SearchResponse(BaseModel):
    documents: list[SearchDocument]