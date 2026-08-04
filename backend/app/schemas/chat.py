from pydantic import BaseModel


class Source(BaseModel):
    title: str
    score: float


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []