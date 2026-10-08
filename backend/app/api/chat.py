from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException

from app.api.deps import get_chat_pipeline
from app.pipeline.chat_pipeline import ChatPipeline
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.core.config import settings
from app.services.auth_service import get_current_principal

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    pipeline: Annotated[ChatPipeline, Depends(get_chat_pipeline)],
    authorization: Annotated[str | None, Header()] = None,
):
    principal_user_id = None
    has_personal_reference = bool(request.conversation_id or request.save_history)
    if settings.WORKFLOW_MODE != "demo" and has_personal_reference:
        principal = get_current_principal(authorization)
        if principal.role != "tutor":
            raise HTTPException(403, "Esta ação é exclusiva do tutor.")
        principal_user_id = principal.user_id

    return ChatService.process(request, pipeline, principal_user_id=principal_user_id)
