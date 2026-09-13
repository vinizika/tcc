from app.exceptions.base_exception import BaseAppException


class TutorNotFoundException(BaseAppException):

    def __init__(self, tutor_id: str):

        super().__init__(
            f"Tutor {tutor_id} não encontrado.",
            status_code=404,
        )
