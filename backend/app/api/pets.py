from fastapi import APIRouter

from app.schemas.pet import PetCreate, PetResponse, PetUpdate
from app.services.pet_service import PetService

router = APIRouter(
    prefix="/pets",
    tags=["Pets"]
)


@router.post("/", response_model=PetResponse)
def create_pet(request: PetCreate):

    return PetService.create(request)


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(pet_id: str):

    return PetService.get(pet_id)


@router.patch("/{pet_id}", response_model=PetResponse)
def update_pet(pet_id: str, request: PetUpdate):

    return PetService.update(pet_id, request)
