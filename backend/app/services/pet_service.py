from app.clients.supabase_client import get_supabase_client
from app.exceptions.pet_exception import PetNotFoundException
from app.schemas.pet import PetCreate, PetResponse, PetUpdate


class PetService:

    TABLE = "pets"

    @staticmethod
    def create(data: PetCreate) -> PetResponse:

        client = get_supabase_client()

        payload = data.model_dump(mode="json", exclude_none=True)

        resultado = (
            client.table(PetService.TABLE).insert(payload).execute()
        )

        return PetResponse(**resultado.data[0])

    @staticmethod
    def get(pet_id: str) -> PetResponse:

        client = get_supabase_client()

        resultado = (
            client.table(PetService.TABLE)
            .select("*")
            .eq("id", pet_id)
            .execute()
        )

        if not resultado.data:
            raise PetNotFoundException(pet_id)

        return PetResponse(**resultado.data[0])

    @staticmethod
    def list_by_tutor(tutor_id: str) -> list[PetResponse]:

        client = get_supabase_client()

        resultado = (
            client.table(PetService.TABLE)
            .select("*")
            .eq("tutor_id", tutor_id)
            .execute()
        )

        return [PetResponse(**linha) for linha in resultado.data]

    @staticmethod
    def update(pet_id: str, data: PetUpdate) -> PetResponse:

        client = get_supabase_client()

        payload = data.model_dump(mode="json", exclude_none=True)

        if not payload:
            # Nada para atualizar: confere que o pet existe e devolve como
            # está, em vez de mandar um UPDATE vazio ao Supabase.
            return PetService.get(pet_id)

        resultado = (
            client.table(PetService.TABLE)
            .update(payload)
            .eq("id", pet_id)
            .execute()
        )

        if not resultado.data:
            raise PetNotFoundException(pet_id)

        return PetResponse(**resultado.data[0])
