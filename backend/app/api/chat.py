from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):

    return ChatService.process(request.question)