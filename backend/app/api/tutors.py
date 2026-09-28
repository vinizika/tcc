from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.pet import PetResponse
from app.schemas.tutor import TutorCreate, TutorResponse
from app.services.pet_service import PetService
from app.services.tutor_service import TutorService
from app.schemas.auth import Principal
from app.services.auth_service import optional_legacy_tutor

router = APIRouter(
    prefix="/tutors",
    tags=["Tutors"]
)


@router.post("/", response_model=TutorResponse)
def create_tutor(
    request: TutorCreate,
    principal: Annotated[Principal | None, Depends(optional_legacy_tutor)],
):

    return TutorService.create_for_user(request, principal.user_id) if principal else TutorService.create(request)


@router.get("/{tutor_id}", response_model=TutorResponse)
def get_tutor(
    tutor_id: str,
    principal: Annotated[Principal | None, Depends(optional_legacy_tutor)],
):

    return TutorService.get_owned(tutor_id, principal.user_id) if principal else TutorService.get(tutor_id)


@router.get("/{tutor_id}/pets", response_model=list[PetResponse])
def list_tutor_pets(
    tutor_id: str,
    principal: Annotated[Principal | None, Depends(optional_legacy_tutor)],
):

    # Confere que o tutor existe antes de listar — devolver lista vazia
    # para um tutor inexistente esconderia um id digitado errado.
    if principal:
        TutorService.get_owned(tutor_id, principal.user_id)
    else:
        TutorService.get(tutor_id)

    return PetService.list_by_tutor(tutor_id)
