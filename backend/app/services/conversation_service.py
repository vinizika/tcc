"""
Histórico de conversa, em MongoDB.

Diferente de tutor/pet (Supabase, dado estruturado), o histórico é
acessório à triagem: se o Mongo não estiver configurado ou fora do ar,
`/chat/` precisa continuar respondendo — só sem gravar o turno. É por isso
que `append_turn` engole a falha e loga, em vez de propagar como as outras
exceções de persistência do módulo.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pymongo.errors import PyMongoError

from app.clients.mongo_client import get_mongo_database
from app.core.logger import setup_logger
from app.exceptions.conversation_exception import ConversationNotFoundException
from app.exceptions.persistence_exception import MongoNotConfiguredException
from app.schemas.conversation import ConversationMessage, ConversationResponse
from app.schemas.triage_output import TriageResult

logger = setup_logger("ConversationService")

COLLECTION = "conversations"


class ConversationService:

    @staticmethod
    def append_turn(
        tutor_message: str,
        assistant_message: str,
        triage: Optional[TriageResult] = None,
        conversation_id: Optional[str] = None,
        tutor_id: Optional[str] = None,
        pet_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Grava o par pergunta/resposta e devolve o id da conversa.

        Devolve `None` quando o Mongo não está disponível — quem chama usa
        isso para saber que não há id de conversa para o tutor reaproveitar
        no próximo turno, sem que a triagem em si tenha falhado.
        """

        agora = datetime.now(timezone.utc).isoformat()

        try:

            database = get_mongo_database()

            if not conversation_id:

                conversation_id = str(uuid4())

                database[COLLECTION].insert_one(
                    {
                        "_id": conversation_id,
                        "tutor_id": tutor_id,
                        "pet_id": pet_id,
                        "created_at": agora,
                        "updated_at": agora,
                        "messages": [],
                    }
                )

            turno_tutor = {
                "role": "tutor",
                "content": tutor_message,
                "timestamp": agora,
                "triage": None,
            }

            turno_assistente = {
                "role": "assistente",
                "content": assistant_message,
                "timestamp": agora,
                "triage": triage.model_dump() if triage else None,
            }

            database[COLLECTION].update_one(
                {"_id": conversation_id},
                {
                    "$push": {
                        "messages": {"$each": [turno_tutor, turno_assistente]}
                    },
                    "$set": {"updated_at": agora},
                },
            )

            return conversation_id

        except (MongoNotConfiguredException, PyMongoError) as erro:

            logger.warning(
                f"Histórico de conversa não gravado (Mongo indisponível): "
                f"{erro}"
            )

            return None

    @staticmethod
    def get(conversation_id: str) -> ConversationResponse:

        database = get_mongo_database()

        documento = database[COLLECTION].find_one({"_id": conversation_id})

        if not documento:
            raise ConversationNotFoundException(conversation_id)

        return ConversationResponse(
            id=documento["_id"],
            tutor_id=documento.get("tutor_id"),
            pet_id=documento.get("pet_id"),
            created_at=documento["created_at"],
            updated_at=documento["updated_at"],
            messages=[
                ConversationMessage(**mensagem)
                for mensagem in documento["messages"]
            ],
        )
