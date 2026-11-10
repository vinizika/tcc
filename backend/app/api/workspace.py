from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile
from app.core.config import settings
from app.schemas.workspace import AnimalInput, ConversationInput, DocumentInput, TurnInput
from app.services import animal_records_service
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


# --- Histórico do animal: documentos e conversas anteriores (rodada 34 do João) ---

@router.post("/documents/read")
def read_document(file: UploadFile = File(...), attendant_provider: Literal["gemini", "ollama"] = Form("gemini"),
                  principal=Depends(require_tutor)):
    """Lê um PDF ou foto e devolve a proposta de resumo. Nada é guardado aqui."""
    limit = settings.MAX_DOCUMENT_UPLOAD_MB * 1024 * 1024
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"Arquivo acima do limite de {settings.MAX_DOCUMENT_UPLOAD_MB} MB.")
    return animal_records_service.read_document(data, file.filename or "documento", attendant_provider)


@router.get("/context")
def context(pet_id: str | None = None, conversation_id: str | None = None, principal=Depends(require_tutor)):
    return Workspace.context(principal, pet_id, conversation_id)


@router.post("/pets/{pet_id}/documents", status_code=201)
def add_pet_document(pet_id: str, data: DocumentInput, principal=Depends(require_tutor)):
    return Workspace.add_document(principal, data, pet_id=pet_id)


@router.delete("/pets/{pet_id}/documents/{document_id}")
def remove_pet_document(pet_id: str, document_id: str, principal=Depends(require_tutor)):
    return Workspace.remove_document(principal, document_id, pet_id=pet_id)


@router.post("/conversations/{conversation_id}/documents", status_code=201)
def add_conversation_document(conversation_id: str, data: DocumentInput, principal=Depends(require_tutor)):
    """Guarda no animal da conversa; sem animal associado, na própria conversa."""
    return Workspace.add_document(principal, data, conversation_id=conversation_id)


@router.delete("/conversations/{conversation_id}/documents/{document_id}")
def remove_conversation_document(conversation_id: str, document_id: str, principal=Depends(require_tutor)):
    return Workspace.remove_document(principal, document_id, conversation_id=conversation_id)


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
