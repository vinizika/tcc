from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.conversation import ConversationResponse
from app.services.conversation_service import ConversationService
from app.schemas.auth import Principal
from app.services.auth_service import optional_legacy_tutor

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    principal: Annotated[Principal | None, Depends(optional_legacy_tutor)],
):

    return ConversationService.get_owned(conversation_id, principal.user_id) if principal else ConversationService.get(conversation_id)
