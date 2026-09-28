from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.pet import PetCreate, PetResponse, PetUpdate
from app.services.pet_service import PetService
from app.schemas.auth import Principal
from app.services.auth_service import optional_legacy_tutor
from app.services.tutor_service import TutorService

router = APIRouter(
    prefix="/pets",
    tags=["Pets"]
)


@router.post("/", response_model=PetResponse)
def create_pet(
    request: PetCreate,
    principal: Annotated[Principal | None, Depends(optional_legacy_tutor)],
):

    if principal:
        TutorService.get_owned(request.tutor_id, principal.user_id)
    return PetService.create(request)


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(
    pet_id: str,
    principal: Annotated[Principal | None, Depends(optional_legacy_tutor)],
):

    return PetService.get_owned(pet_id, principal.user_id) if principal else PetService.get(pet_id)


@router.patch("/{pet_id}", response_model=PetResponse)
def update_pet(
    pet_id: str,
    request: PetUpdate,
    principal: Annotated[Principal | None, Depends(optional_legacy_tutor)],
):

    return PetService.update_owned(pet_id, request, principal.user_id) if principal else PetService.update(pet_id, request)
