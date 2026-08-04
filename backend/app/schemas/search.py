from pydantic import BaseModel


class SearchRequest(BaseModel):
    question: str


class SearchResponse(BaseModel):
    documents: list[str]