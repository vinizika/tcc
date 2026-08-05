from pydantic import BaseModel

class SourceResponse(BaseModel):

    title: str

    score: float


class ChatResponse(BaseModel):

    answer: str

    sources: list[SourceResponse]