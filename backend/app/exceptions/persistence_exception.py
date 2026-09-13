from app.exceptions.base_exception import BaseAppException


class SupabaseNotConfiguredException(BaseAppException):
    """
    SUPABASE_URL/SUPABASE_KEY vazios.

    Em desenvolvimento, sem um projeto criado ainda, cadastro de tutor e pet
    não tem onde ser gravado. Falhar com uma mensagem clara é melhor que
    tentar conectar em uma URL vazia e devolver um erro de rede genérico.
    """

    def __init__(self, message: str = (
        "Supabase não configurado. Defina SUPABASE_URL e SUPABASE_KEY."
    )):

        super().__init__(message, status_code=503)


class MongoNotConfiguredException(BaseAppException):
    """MONGODB_URI vazio — sem onde gravar o histórico de conversa."""

    def __init__(self, message: str = (
        "MongoDB não configurado. Defina MONGODB_URI."
    )):

        super().__init__(message, status_code=503)
