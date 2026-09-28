from fastapi import APIRouter, BackgroundTasks, Depends, Query
from app.schemas.workspace import AnimalInput, ConversationInput, TurnInput
from app.services.auth_service import require_tutor
from app.services.workspace_service import WorkspaceService as Workspace

router = APIRouter(prefix="/workspace", tags=["Workspace"])


@router.get("/pets")
def pets(principal=Depends(require_tutor), offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100)):
    return Workspace.pets(principal, offset, limit)


@router.post("/pets", status_code=201)
def create_pet(data: AnimalInput, principal=Depends(require_tutor)):
    return Workspace.save_pet(principal, data)


@router.put("/pets/{pet_id}")
def update_pet(pet_id: str, data: AnimalInput, principal=Depends(require_tutor)):
    return Workspace.save_pet(principal, data, pet_id)


@router.get("/conversations")
def conversations(principal=Depends(require_tutor), offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100)):
    return Workspace.list(principal, offset, limit)


@router.post("/conversations", status_code=201)
def create_conversation(data: ConversationInput, principal=Depends(require_tutor)):
    return Workspace.create(principal, data.pet_id)


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, principal=Depends(require_tutor)):
    return Workspace.get(principal, conversation_id)


@router.patch("/conversations/{conversation_id}")
def associate(conversation_id: str, data: ConversationInput, principal=Depends(require_tutor)):
    return Workspace.associate(principal, conversation_id, data.pet_id)


@router.post("/conversations/{conversation_id}/messages", status_code=202)
def turn(conversation_id: str, data: TurnInput, background: BackgroundTasks, principal=Depends(require_tutor)):
    doc, created = Workspace.submit(principal, conversation_id, data)
    if created:
        background.add_task(Workspace.process, principal, conversation_id, data.request_id)
    return doc
