from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings
from app.exceptions.persistence_exception import MongoNotConfiguredException


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    """
    Cliente compartilhado do MongoDB, para o histórico de conversa.

    `serverSelectionTimeoutMS` curto: sem ele, um Mongo fora do ar prende a
    requisição por até 30s (padrão da biblioteca) antes de falhar — tempo
    demais para uma etapa que é acessória à triagem.
    """

    if not settings.MONGODB_URI:
        raise MongoNotConfiguredException()

    return MongoClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5000,
    )


def get_mongo_database() -> Database:

    return get_mongo_client()[settings.MONGODB_DB_NAME]
