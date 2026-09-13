from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings
from app.exceptions.persistence_exception import SupabaseNotConfiguredException


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Cliente compartilhado do Supabase, para tutores e pets.

    Falha explicitamente quando as credenciais estão vazias, em vez de
    deixar a biblioteca tentar conectar numa URL em branco: em
    desenvolvimento, sem projeto criado ainda, é o estado normal, e a
    mensagem precisa dizer o que fazer, não parecer um erro de rede.
    """

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise SupabaseNotConfiguredException()

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
