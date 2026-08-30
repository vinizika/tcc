from pydantic import BaseModel


class SearchRequest(BaseModel):
    question: str


class SearchDocument(BaseModel):
    id: str
    title: str
    content: str
    source: str
    score: float


class SearchResponse(BaseModel):
    documents: list[SearchDocument]