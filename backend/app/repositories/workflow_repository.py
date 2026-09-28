from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from fastapi import HTTPException

from app.clients.mongo_client import get_mongo_database
from app.core.config import settings


DEMO_CLINICS: list[dict[str, Any]] = [
    {
        "id": "demo-clinic-a", "name": "Hospital Veterinário Aurora — fictício",
        "address": "Av. Demonstração, 120 — São Paulo/SP", "latitude": -23.5614,
        "longitude": -46.6559, "phone": "+55 11 0000-0101", "opening_hours": "24 horas (dado fictício)",
        "open_now": True, "rating": 4.7, "review_count": 128, "source": "demo",
        "participant": True, "verified": True, "enabled": True, "google_place_id": None,
    },
    {
        "id": "demo-clinic-b", "name": "Centro Vet Horizonte — fictício",
        "address": "Rua Cenário, 45 — São Paulo/SP", "latitude": -23.5687,
        "longitude": -46.6481, "phone": "+55 11 0000-0202", "opening_hours": "08:00–22:00 (dado fictício)",
        "open_now": True, "rating": 4.4, "review_count": 73, "source": "demo",
        "participant": True, "verified": True, "enabled": True, "google_place_id": None,
    },
    {
        "id": "demo-public-only", "name": "Clínica Pública Exemplo — fictícia",
        "address": "Alameda Mock, 900 — São Paulo/SP", "latitude": -23.5520,
        "longitude": -46.6650, "phone": "+55 11 0000-0303", "opening_hours": None,
        "open_now": None, "rating": 4.8, "review_count": 41, "source": "demo",
        "participant": False, "verified": False, "enabled": False, "google_place_id": None,
    },
]


class MemoryWorkflowRepository:
    """Repositório de teste; o Compose usa Mongo e persiste entre recargas."""

    def __init__(self):
        self.clinics = {item["id"]: deepcopy(item) for item in DEMO_CLINICS}
        self.referrals: dict[str, dict] = {}
        self.idempotency: dict[tuple[str, str], str] = {}
        self.lock = RLock()

    def list_clinics(self) -> list[dict]: return [deepcopy(v) for v in self.clinics.values()]
    def get_clinic(self, clinic_id: str) -> dict | None: return deepcopy(self.clinics.get(clinic_id))
    def save_clinic(self, document: dict) -> dict:
        self.clinics[document["id"]] = deepcopy(document); return deepcopy(document)
    def save_referral(self, document: dict, key: str) -> tuple[dict, bool]:
        with self.lock:
            existing_id = self.idempotency.get((document["tutor_id"], key))
            if existing_id:
                return deepcopy(self.referrals[existing_id]), False
            self.referrals[document["id"]] = deepcopy(document)
            self.idempotency[(document["tutor_id"], key)] = document["id"]
            return deepcopy(document), True
    def get_referral(self, referral_id: str) -> dict | None: return deepcopy(self.referrals.get(referral_id))
    def list_referrals(self, query: dict) -> list[dict]:
        return [deepcopy(v) for v in self.referrals.values() if all(v.get(k) == val for k, val in query.items())]
    def replace_referral(self, document: dict) -> dict:
        self.referrals[document["id"]] = deepcopy(document); return deepcopy(document)


class MongoWorkflowRepository:
    def __init__(self):
        database = get_mongo_database()
        self.clinics = database["workflow_clinics"]
        self.referrals = database["referrals"]
        self.clinics.create_index("id", unique=True)
        self.referrals.create_index("id", unique=True)
        self.referrals.create_index([("tutor_id", ASCENDING), ("idempotency_key", ASCENDING)], unique=True)
        self.referrals.create_index([("clinic_id", ASCENDING), ("created_at", DESCENDING)])
        if settings.WORKFLOW_MODE == "demo" or settings.POC_QUICK_LOGIN_ENABLED:
            for clinic in DEMO_CLINICS:
                self.clinics.update_one({"id": clinic["id"]}, {"$setOnInsert": clinic}, upsert=True)

    @staticmethod
    def _clean(document: dict | None) -> dict | None:
        if document:
            document.pop("_id", None)
        return document

    def list_clinics(self) -> list[dict]: return [self._clean(item) for item in self.clinics.find({})]
    def get_clinic(self, clinic_id: str) -> dict | None: return self._clean(self.clinics.find_one({"id": clinic_id}))
    def save_clinic(self, document: dict) -> dict:
        self.clinics.replace_one({"id": document["id"]}, deepcopy(document), upsert=True)
        return document
    def save_referral(self, document: dict, key: str) -> tuple[dict, bool]:
        existing = self.referrals.find_one({"tutor_id": document["tutor_id"], "idempotency_key": key})
        if existing: return self._clean(existing), False
        try:
            self.referrals.insert_one(deepcopy(document))
            return document, True
        except DuplicateKeyError:
            # Dois cliques concorrentes podem passar pelo primeiro find. O
            # índice único decide e a segunda requisição devolve o original.
            existing = self.referrals.find_one({"tutor_id": document["tutor_id"], "idempotency_key": key})
            if existing:
                return self._clean(existing), False
            raise
    def expire_locations(self):
        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=120)).isoformat()
        self.referrals.update_many({"location.updated_at": {"$lt": cutoff}},
            {"$set": {"location": None}, "$inc": {"_revision": 1}})

    def get_referral(self, referral_id: str) -> dict | None:
        self.expire_locations()
        return self._clean(self.referrals.find_one({"id": referral_id}))
    def list_referrals(self, query: dict) -> list[dict]:
        self.expire_locations()
        return [self._clean(item) for item in self.referrals.find(query).sort("created_at", DESCENDING)]
    def replace_referral(self, document: dict) -> dict:
        revision = document.get("_revision", 0)
        selector = {"id": document["id"], "$or": [{"_revision": revision}, {"_revision": {"$exists": False}}]} if revision == 0 else {"id": document["id"], "_revision": revision}
        document["_revision"] = revision + 1
        result = self.referrals.replace_one(selector, deepcopy(document), upsert=False)
        if not result.matched_count:
            raise HTTPException(409, "O caso foi atualizado em outra sessão. Atualize e tente novamente.")
        return document


_memory_repository = MemoryWorkflowRepository()
_mongo_repository: MongoWorkflowRepository | None = None


def get_workflow_repository():
    global _mongo_repository
    try:
        if _mongo_repository is None:
            _mongo_repository = MongoWorkflowRepository()
        return _mongo_repository
    except PyMongoError:
        # Apenas testes podem usar o adaptador volátil. Na aplicação, a falta
        # de Mongo deve ser visível e não transformar produção em demo.
        if settings.ENVIRONMENT == "test":
            return _memory_repository
        raise


def reset_memory_repository() -> None:
    global _memory_repository
    _memory_repository = MemoryWorkflowRepository()
