from fastapi import APIRouter

from app.schemas.pet import PetResponse
from app.schemas.tutor import TutorCreate, TutorResponse
from app.services.pet_service import PetService
from app.services.tutor_service import TutorService

router = APIRouter(
    prefix="/tutors",
    tags=["Tutors"]
)


@router.post("/", response_model=TutorResponse)
def create_tutor(request: TutorCreate):

    return TutorService.create(request)


@router.get("/{tutor_id}", response_model=TutorResponse)
def get_tutor(tutor_id: str):

    return TutorService.get(tutor_id)


@router.get("/{tutor_id}/pets", response_model=list[PetResponse])
def list_tutor_pets(tutor_id: str):

    # Confere que o tutor existe antes de listar — devolver lista vazia
    # para um tutor inexistente esconderia um id digitado errado.
    TutorService.get(tutor_id)

    return PetService.list_by_tutor(tutor_id)
