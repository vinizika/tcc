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
    def create_for_user(data: TutorCreate, user_id: str) -> TutorResponse:
        client = get_supabase_client()
        payload = data.model_dump(exclude_none=True) | {"user_id": user_id}
        resultado = client.table(TutorService.TABLE).insert(payload).execute()
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

    @staticmethod
    def get_owned(tutor_id: str, user_id: str) -> TutorResponse:
        client = get_supabase_client()
        resultado = (
            client.table(TutorService.TABLE)
            .select("*")
            .eq("id", tutor_id)
            .eq("user_id", user_id)
            .execute()
        )
        if not resultado.data:
            raise TutorNotFoundException(tutor_id)
        return TutorResponse(**resultado.data[0])
