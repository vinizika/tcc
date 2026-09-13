import pytest

from app.clients.supabase_client import get_supabase_client
from app.core.config import settings
from app.exceptions.persistence_exception import SupabaseNotConfiguredException


def test_sem_credenciais_levanta_excecao_clara(monkeypatch):

    monkeypatch.setattr(settings, "SUPABASE_URL", "")
    monkeypatch.setattr(settings, "SUPABASE_KEY", "")

    get_supabase_client.cache_clear()

    with pytest.raises(SupabaseNotConfiguredException):
        get_supabase_client()

    get_supabase_client.cache_clear()
