from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_chat_pipeline
from app.pipeline.chat_pipeline import ChatPipeline
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    pipeline: Annotated[ChatPipeline, Depends(get_chat_pipeline)],
):

    return ChatService.process(request, pipeline)
