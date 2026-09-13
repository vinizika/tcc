from app.exceptions.base_exception import BaseAppException


class PetNotFoundException(BaseAppException):

    def __init__(self, pet_id: str):

        super().__init__(
            f"Pet {pet_id} não encontrado.",
            status_code=404,
        )
