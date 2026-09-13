from app.clients.supabase_client import get_supabase_client
from app.exceptions.tutor_exception import TutorNotFoundException
from app.schemas.tutor import TutorCreate, TutorResponse


class TutorService:

    TABLE = "tutors"

    @staticmethod
    def create(data: TutorCreate) -> TutorResponse:

        client = get_supabase_client()

        resultado = (
            client.table(TutorService.TABLE)
            .insert(data.model_dump(exclude_none=True))
            .execute()
        )

        return TutorResponse(**resultado.data[0])

    @staticmethod
    def get(tutor_id: str) -> TutorResponse:

        client = get_supabase_client()

        resultado = (
            client.table(TutorService.TABLE)
            .select("*")
            .eq("id", tutor_id)
            .execute()
        )

        if not resultado.data:
            raise TutorNotFoundException(tutor_id)

        return TutorResponse(**resultado.data[0])
