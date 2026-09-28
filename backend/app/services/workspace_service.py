"""Persistent conversation workspace. The research pipeline remains independent."""
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from uuid import uuid4

from fastapi import HTTPException
from app.clients.mongo_client import get_mongo_database
from app.core.config import settings
from app.schemas.auth import Principal
from app.schemas.workspace import AnimalInput, TurnInput


def now():
    return datetime.now(timezone.utc).isoformat()


def public(document):
    if document is None:
        raise HTTPException(404, "Registro não encontrado.")
    return {k: v for k, v in document.items() if k != "_id"}


def scope(principal: Principal):
    return {"owner_id": principal.user_id}


class WorkspaceService:
    @staticmethod
    def db():
        db = get_mongo_database()
        db.poc_pets.create_index([("owner_id", 1), ("id", 1)], unique=True)
        db.poc_conversations.create_index([("owner_id", 1), ("id", 1)], unique=True)
        db.poc_conversations.create_index([("owner_id", 1), ("updated_at", -1)])
        return db

    @staticmethod
    def pets(principal, offset=0, limit=30):
        return [public(d) for d in WorkspaceService.db().poc_pets.find(scope(principal)).sort("created_at", -1).skip(offset).limit(limit)]

    @staticmethod
    def pet(principal, pet_id):
        return public(WorkspaceService.db().poc_pets.find_one(scope(principal) | {"id": pet_id}))

    @staticmethod
    def save_pet(principal, data: AnimalInput, pet_id=None):
        db = WorkspaceService.db()
        if pet_id:
            old = WorkspaceService.pet(principal, pet_id)
        else:
            old = {"id": str(uuid4()), "owner_id": principal.user_id, "created_at": now()}
        doc = old | data.model_dump() | {"updated_at": now()}
        db.poc_pets.replace_one(scope(principal) | {"id": doc["id"]}, doc, upsert=True)
        return doc

    @staticmethod
    def create(principal, pet_id=None):
        pet = WorkspaceService.pet(principal, pet_id) if pet_id else None
        doc = {"id": str(uuid4()), "owner_id": principal.user_id, "title": "Nova conversa",
               "pet_id": pet_id, "pet": pet, "messages": [], "status": "idle", "error": None,
               "created_at": now(), "updated_at": now(), "request_id": None}
        WorkspaceService.db().poc_conversations.insert_one(dict(doc))
        return doc

    @staticmethod
    def get(principal, conversation_id):
        db = WorkspaceService.db()
        doc = public(db.poc_conversations.find_one(scope(principal) | {"id": conversation_id}))
        # A interrupted worker has a bounded lease, so a restart cannot strand a chat.
        if doc["status"] == "processing" and datetime.fromisoformat(doc["updated_at"]) < datetime.now(timezone.utc) - timedelta(minutes=20):
            db.poc_conversations.update_one({"id": conversation_id, "status": "processing", "request_id": doc["request_id"]},
                {"$set": {"status": "failed", "error": "A análise foi interrompida. Tente novamente."}})
            doc.update(status="failed", error="A análise foi interrompida. Tente novamente.")
        return doc

    @staticmethod
    def list(principal, offset=0, limit=30):
        cursor = WorkspaceService.db().poc_conversations.find(scope(principal), {"messages": 0}).sort("updated_at", -1).skip(offset).limit(limit)
        return [public(d) for d in cursor]

    @staticmethod
    def associate(principal, conversation_id, pet_id):
        doc = WorkspaceService.get(principal, conversation_id)
        if doc["status"] == "processing":
            raise HTTPException(409, "Aguarde a análise antes de trocar o animal.")
        pet = WorkspaceService.pet(principal, pet_id) if pet_id else None
        result = WorkspaceService.db().poc_conversations.update_one(scope(principal) | {"id": conversation_id, "status": {"$ne": "processing"}},
            {"$set": {"pet_id": pet_id, "pet": pet, "updated_at": now()}})
        if not result.matched_count:
            raise HTTPException(409, "Uma análise começou. Aguarde antes de trocar o animal.")
        return WorkspaceService.get(principal, conversation_id)

    @staticmethod
    def submit(principal, conversation_id, data: TurnInput):
        doc = WorkspaceService.get(principal, conversation_id)
        if doc.get("request_id") == data.request_id:
            return doc, False
        if doc["status"] == "processing":
            raise HTTPException(409, "Uma análise já está em andamento nesta conversa.")
        if len(doc["messages"]) >= 100:
            raise HTTPException(409, "Esta conversa atingiu 50 respostas. Inicie uma nova conversa.")
        message = {"id": data.request_id, "role": "tutor", "content": data.content, "created_at": now()}
        result = WorkspaceService.db().poc_conversations.update_one(
            scope(principal) | {"id": conversation_id, "status": {"$ne": "processing"}, "messages.id": {"$ne": data.request_id}},
            {"$set": {"status": "processing", "request_id": data.request_id, "error": None, "updated_at": now(),
                      "title": data.content[:64] if not doc["messages"] else doc["title"]}, "$push": {"messages": message}})
        if not result.modified_count:
            raise HTTPException(409, "Este envio já foi recebido. Atualize a conversa.")
        return WorkspaceService.get(principal, conversation_id), True

    @staticmethod
    def process(principal, conversation_id, request_id, pipeline=None):
        db = WorkspaceService.db()
        selector = {"id": conversation_id, "owner_id": principal.user_id, "request_id": request_id, "status": "processing"}
        try:
            doc = WorkspaceService.get(principal, conversation_id)
            if doc["request_id"] != request_id or doc["status"] != "processing":
                return
            # Only the tutor's statements enter the next clinical judgment; never
            # feed earlier generated conclusions back as facts.
            reports = [m["content"] for m in doc["messages"] if m["role"] == "tutor"]
            # Never truncate the current report: a warning sign may be at its end.
            # Earlier context is explicitly bounded; stored history stays complete.
            current = reports[-1]
            previous = reports[:-1]
            history = "\n".join(([previous[0]] + previous[-4:]) if len(previous) > 4 else previous)
            question = (("Relatos anteriores (trecho):\n" + history[:1800] + "\nRelato atual do tutor:\n") if previous else "") + current
            pet = doc.get("pet")
            context = None
            if pet:
                context = "; ".join(f"{key}: {value}" for key, value in pet.items()
                                    if key in {"name", "species", "age", "weight_kg", "breed", "relevant_history"} and value is not None)
            from app.schemas.triage import PipelineOptions
            result = (pipeline or poc_pipeline()).execute(question, PipelineOptions(
                retrieval_enabled=True, query_rewriting_enabled=False, multi_query_enabled=False, hyde_enabled=False), animal_context=context)
            message = {"id": str(uuid4()), "role": "assistant", "content": result.answer, "created_at": now(),
                       "triage": result.triage.model_dump(mode="json"),
                       "retrieval": result.retrieval.model_dump(mode="json"),
                       "sources": [{"title": s.document.title, "source": s.document.source, "cited": s.cited} for s in result.sources],
                       "config": result.config.model_dump(mode="json"), "timings": result.timings.model_dump(mode="json"),
                       "rag_collection": settings.POC_RAG_COLLECTION or settings.CHROMA_COLLECTION}
            db.poc_conversations.update_one(selector, {"$push": {"messages": message},
                "$set": {"status": "idle", "error": None, "updated_at": now()}})
        except Exception:
            # Never put upstream credentials or raw exception text in a patient response.
            db.poc_conversations.update_one(selector, {"$set": {"status": "failed", "updated_at": now(),
                "error": "Não conseguimos concluir a análise. Seu relato está salvo. Tente novamente ou procure atendimento."}})


@lru_cache(maxsize=1)
def poc_pipeline():
    from app.pipeline.chat_pipeline import ChatPipeline
    from app.clients.retrieval_client import RetrievalClient
    from app.database.chroma_client import ChromaDBClient
    if not settings.POC_RAG_COLLECTION:
        return ChatPipeline()

    # Separate client and collection: the research pointer and legacy API are unchanged.
    class PocChroma(ChromaDBClient):
        _client = None
        _embedding_function = None

    PocChroma.configure(path=settings.POC_RAG_PATH or None)
    PocChroma.validate_collection_integrity(settings.POC_RAG_COLLECTION)
    collection = PocChroma._get_strict_collection(settings.POC_RAG_COLLECTION)

    class PocRetrieval:
        @staticmethod
        def retrieve(queries, *, routing_query=None):
            return RetrievalClient.retrieve(queries, routing_query=routing_query, collection=collection)

    return ChatPipeline(retrieval_client=PocRetrieval)
