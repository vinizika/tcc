from fastapi import APIRouter

from app.schemas.conversation import ConversationResponse
from app.services.conversation_service import ConversationService

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str):

    return ConversationService.get(conversation_id)
