"""Persistent conversation workspace. The research pipeline remains independent."""
from datetime import datetime, timedelta, timezone
from functools import lru_cache
import logging
from uuid import uuid4

from fastapi import HTTPException
from app.clients.mongo_client import get_mongo_database
from app.core.config import settings
from app.services.followup_service import WorkspaceAttendant, advance, transcript, clinical_query
from app.schemas.auth import Principal
from app.schemas.workspace import AnimalInput, TurnInput
from app.exceptions.attendant_exception import AttendantUnavailableException, QuotaExhaustedException


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
            result = db.poc_conversations.update_one(scope(principal) | {"id": conversation_id, "status": "processing", "request_id": doc["request_id"], "updated_at": doc["updated_at"]},
                {"$set": {"status": "failed", "error": "A análise foi interrompida. Tente novamente."}})
            if result.modified_count:
                doc.update(status="failed", error="A análise foi interrompida. Tente novamente.")
            else:
                doc = public(db.poc_conversations.find_one(scope(principal) | {"id": conversation_id}))
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
        seen = data.request_id in doc.get("accepted_requests", []) or any(m["id"] == data.request_id for m in doc["messages"])
        if (doc.get("request_id") == data.request_id or seen) and not (doc["status"] == "failed" and doc.get("request_id") == data.request_id):
            return doc, False
        if doc["status"] == "processing":
            raise HTTPException(409, "Uma análise já está em andamento nesta conversa.")
        if len(doc["messages"]) >= 100:
            raise HTTPException(409, "Esta conversa atingiu 50 respostas. Inicie uma nova conversa.")
        if seen and doc["messages"][-1]["content"] != data.content:
            raise HTTPException(409, "Use o conteúdo original para repetir este envio.")
        followup = doc.get("followup") or {}
        if data.origin == "form" and (followup.get("state") != "form" or data.question_id != followup.get("question_id") or data.selected_option not in followup.get("options", [])):
            raise HTTPException(409, "Este formulário não está mais disponível. Atualize a conversa.")
        if data.origin == "form" and not data.content.startswith(data.selected_option):
            raise HTTPException(422, "A resposta deve incluir a opção selecionada.")
        message = {"id": data.request_id, "role": "tutor", "content": data.content, "created_at": now(),
                   "origin": data.origin, "selected_option": data.selected_option,
                   "question_id": followup.get("question_id"),
                   "answer_to": followup.get("question") if followup.get("state") in {"asking", "form"} else None}
        retry = (doc["status"] == "failed" and doc["messages"]
                 and doc["messages"][-1]["role"] == "tutor"
                 and doc["messages"][-1]["content"] == data.content)
        update = {"$set": {"status": "processing", "processing_id": str(uuid4()), "request_id": data.request_id, "error": None, "error_code": None,
                          "attendant_provider": data.attendant_provider or settings.ATTENDANT_PROVIDER, "updated_at": now(),
                          "title": data.content[:64] if not doc["messages"] else doc["title"]}}
        update["$addToSet"] = {"accepted_requests": data.request_id}
        if not retry:
            update["$push"] = {"messages": message}
        result = WorkspaceService.db().poc_conversations.update_one(
            scope(principal) | {"id": conversation_id, "status": doc["status"], "updated_at": doc["updated_at"]},
            update)
        if not result.modified_count:
            raise HTTPException(409, "Este envio já foi recebido. Atualize a conversa.")
        return WorkspaceService.get(principal, conversation_id), True

    @staticmethod
    def process(principal, conversation_id, request_id, pipeline=None, planner=None):
        db = WorkspaceService.db()
        selector = {"id": conversation_id, "owner_id": principal.user_id, "request_id": request_id, "status": "processing"}
        try:
            doc = WorkspaceService.get(principal, conversation_id)
            if doc["request_id"] != request_id or doc["status"] != "processing":
                return
            selector["processing_id"] = doc.get("processing_id")
            question = transcript(doc)
            pet = doc.get("pet")
            context = None
            if pet:
                context = "; ".join(f"{key}: {value}" for key, value in pet.items()
                                    if key in {"name", "species", "age", "weight_kg", "breed", "relevant_history"} and value is not None)
            from app.schemas.triage import PipelineOptions
            result = (pipeline or poc_pipeline()).execute(question, PipelineOptions(
                num_ctx=settings.WORKSPACE_NUM_CTX, retrieval_enabled=True, prompt_version="v1_grounded", cot_enabled=False, query_rewriting_enabled=False, multi_query_enabled=False, hyde_enabled=False,
                attendant_provider=doc.get("attendant_provider", settings.ATTENDANT_PROVIDER)), animal_context=context,
                retrieval_question=clinical_query(doc))
            checkpoint = db.poc_conversations.update_one(selector, {"$set": {
                "latest_triage": result.triage.model_dump(mode="json", exclude={"raciocinio"})}})
            if not checkpoint.matched_count:
                return
            followup = advance(doc, result, planner)
            content = "\n".join(filter(None, [result.triage.justificativa, result.triage.recomendacao,
                                               followup.get("question"), followup.get("guidance")]))
            message = {"id": str(uuid4()), "role": "assistant", "content": content, "created_at": now(),
                       "triage": result.triage.model_dump(mode="json", exclude={"raciocinio"}),
                       "followup": followup,
                       "retrieval": result.retrieval.model_dump(mode="json"),
                       "sources": [{"title": s.document.title, "display_title": s.document.display_title,
                                    "topic": s.document.topic, "references": list(s.document.references),
                                    "source": s.document.source, "cited": s.cited} for s in result.sources],
                       "provenance": result.provenance.model_dump(mode="json") if result.provenance else None,
                       "config": result.config.model_dump(mode="json"), "timings": result.timings.model_dump(mode="json"),
                       "rag_collection": active_collection_name()}
            db.poc_conversations.update_one(selector, {"$push": {"messages": message},
                "$set": {"status": "idle", "error": None, "followup": followup, "updated_at": now()}})
        except AttendantUnavailableException as error:
            message = ("A cota do serviço de análise foi esgotada. Seu relato está salvo. Procure atendimento se houver piora."
                       if isinstance(error, QuotaExhaustedException) else
                       "O serviço de análise está indisponível. Seu relato está salvo. Tente novamente ou procure atendimento.")
            if error.details.get("reason") == "context_limit":
                message = "O histórico excede a capacidade configurada do modelo local. Seu relato está salvo. Selecione Gemini para tentar novamente ou procure uma clínica."
            db.poc_conversations.update_one(selector, {"$set": {"status": "failed", "updated_at": now(),
                "error": message, "error_code": error.code}})
        except Exception as error:
            logging.getLogger(__name__).error("Workspace analysis failed (%s)", type(error).__name__)
            # Never put upstream credentials or raw exception text in a patient response.
            db.poc_conversations.update_one(selector, {"$set": {"status": "failed", "updated_at": now(),
                "error": "Não conseguimos concluir a análise. Seu relato está salvo. Tente novamente ou procure atendimento."}})


def active_collection_name():
    from app.database.chroma_client import ChromaDBClient
    if settings.POC_RAG_COLLECTION:
        return settings.POC_RAG_COLLECTION
    pointer = ChromaDBClient.load_active_pointer()
    return pointer["collection_name"] if pointer else settings.CHROMA_COLLECTION


@lru_cache(maxsize=1)
def poc_pipeline():
    from app.pipeline.chat_pipeline import ChatPipeline
    from app.clients.retrieval_client import RetrievalClient
    from app.database.chroma_client import ChromaDBClient
    class WorkspacePipeline(ChatPipeline):
        def _attendant(self, provider):
            return WorkspaceAttendant(super()._attendant(provider))

    if not settings.POC_RAG_COLLECTION:
        return WorkspacePipeline()

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

    return WorkspacePipeline(retrieval_client=PocRetrieval)
