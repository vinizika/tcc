from app.exceptions.base_exception import BaseAppException


class ConversationNotFoundException(BaseAppException):

    def __init__(self, conversation_id: str):

        super().__init__(
            f"Conversa {conversation_id} não encontrada.",
            status_code=404,
        )
