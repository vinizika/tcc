import pytest

from app.clients.mongo_client import get_mongo_client
from app.core.config import settings
from app.exceptions.persistence_exception import MongoNotConfiguredException


def test_sem_uri_levanta_excecao_clara(monkeypatch):

    monkeypatch.setattr(settings, "MONGODB_URI", "")

    get_mongo_client.cache_clear()

    with pytest.raises(MongoNotConfiguredException):
        get_mongo_client()

    get_mongo_client.cache_clear()
