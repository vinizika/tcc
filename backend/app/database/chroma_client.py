"""Acesso seguro e versionado ao ChromaDB.

Uma ingestão escreve em uma coleção candidata. Somente ``activate_collection``
troca o ponteiro ativo, depois de conferir manifesto, contagem e hashes. A
coleção-base antiga é a única exceção que pode existir sem manifesto.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from app.core.config import settings
from app.core.logger import setup_logger
from app.database.embedding_config import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_MODEL_REVISION,
    embedding_recipe_sha256,
)


logger = setup_logger("ChromaDB")


class ActiveCollectionUnavailableError(RuntimeError):
    pass


class MissingManifestError(RuntimeError):
    pass


class CollectionIntegrityError(RuntimeError):
    pass


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def chunk_ids_sha256(identifiers: list[str]) -> str:
    return hashlib.sha256(
        "\n".join(sorted(str(value) for value in identifiers)).encode("utf-8")
    ).hexdigest()


def chunk_content_sha256(
    identifiers: list[str],
    documents: list[str],
    metadatas: list[dict | None],
) -> str:
    """Hash estável de id, texto vetorizado e metadados de cada chunk."""

    rows: list[str] = []
    for index, identifier in enumerate(identifiers):
        document = documents[index] if index < len(documents) else ""
        metadata = metadatas[index] if index < len(metadatas) else None
        rows.append(
            "\x1f".join(
                (
                    str(identifier),
                    str(document or ""),
                    _canonical_json(metadata or {}),
                )
            )
        )
    return hashlib.sha256("\x1e".join(sorted(rows)).encode("utf-8")).hexdigest()


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_path, path)


class ChromaDBClient:
    """Cliente lazy com ponteiro persistente para a coleção ativa."""

    _backend_directory = Path(__file__).resolve().parents[2]
    _client = None
    _embedding_function = None
    _path_override: Path | None = None
    _collection_override: str | None = None
    _embedding_override = None

    @classmethod
    def configure(
        cls,
        *,
        path: str | Path | None = None,
        collection_name: str | None = None,
        embedding_function=None,
    ) -> None:
        """Configura um cliente isolado; usado por testes e ferramentas."""

        cls._path_override = Path(path) if path is not None else None
        cls._collection_override = collection_name
        cls._embedding_override = embedding_function
        cls._client = None
        cls._embedding_function = None

    @classmethod
    def reset_configuration(cls) -> None:
        cls.configure()

    @classmethod
    def chroma_path(cls) -> Path:
        if cls._path_override is not None:
            return cls._path_override.resolve()
        configured = Path(settings.CHROMA_PATH)
        if configured.is_absolute():
            return configured
        return (cls._backend_directory / configured).resolve()

    @classmethod
    def base_collection_name(cls) -> str:
        return cls._collection_override or settings.CHROMA_COLLECTION

    @classmethod
    def pointer_path(cls) -> Path:
        return cls.chroma_path() / "active_collection.json"

    @classmethod
    def manifest_path(cls, collection_name: str) -> Path:
        return cls.chroma_path() / "manifests" / f"{collection_name}.json"

    @classmethod
    def _get_embedding_function(cls):
        if cls._embedding_override is not None:
            return cls._embedding_override
        if cls._embedding_function is None:
            cls._embedding_function = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=EMBEDDING_MODEL_NAME,
                    revision=EMBEDDING_MODEL_REVISION,
                )
            )
        return cls._embedding_function

    @classmethod
    def get_client(cls):
        if cls._client is None:
            path = cls.chroma_path()
            path.mkdir(parents=True, exist_ok=True)
            cls._client = chromadb.PersistentClient(path=str(path))
        return cls._client

    @classmethod
    def is_versioned_collection(cls, collection_name: str) -> bool:
        return collection_name.startswith(f"{cls.base_collection_name()}__")

    @classmethod
    def load_active_pointer(cls) -> dict | None:
        path = cls.pointer_path()
        if not path.exists():
            return None
        try:
            pointer = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ActiveCollectionUnavailableError(
                f"Ponteiro ativo inválido em {path}: {error}"
            ) from error
        if not isinstance(pointer, dict) or not pointer.get("collection_name"):
            raise ActiveCollectionUnavailableError(
                f"Ponteiro ativo sem collection_name: {path}"
            )
        return pointer

    @classmethod
    def _get_strict_collection(
        cls,
        collection_name: str,
        *,
        with_embedding_function: bool = True,
    ):
        try:
            return cls.get_client().get_collection(
                name=collection_name,
                embedding_function=(
                    cls._get_embedding_function()
                    if with_embedding_function
                    else None
                ),
            )
        except Exception as error:
            raise ActiveCollectionUnavailableError(
                f"A coleção {collection_name!r} não existe ou não pode ser aberta"
            ) from error

    @classmethod
    def get_collection_for_inspection(cls):
        """Abre a coleção ativa sem modelo de embedding e sem criar estado.

        Fingerprints e verificações que só usam ``count``/``get`` não precisam
        transformar texto em vetor. Carregar o SentenceTransformer nesse caminho
        fazia uma rota de saúde consultar o Hugging Face e aguardar todos os
        backoffs de rede quando o modelo não estava inteiramente no cache.

        A inspeção continua validando a identidade do manifesto apontado. A
        integridade dos chunks é conferida sobre a única leitura feita pelo
        próprio fingerprint, evitando duas varreduras integrais consecutivas.
        """

        pointer = cls.load_active_pointer()
        if pointer:
            collection_name = str(pointer["collection_name"])
            collection = cls._get_strict_collection(
                collection_name,
                with_embedding_function=False,
            )
            manifest = cls.load_manifest(collection_name, required=True)
            chunks = manifest.get("chunks")
            required_chunk_fields = ("count", "ids_sha256", "content_sha256")
            if not isinstance(chunks, dict) or any(
                field not in chunks for field in required_chunk_fields
            ):
                raise CollectionIntegrityError(
                    "Manifesto ativo sem metadados obrigatórios de chunks."
                )
            if pointer.get("manifest_sha256") != sha256_json(manifest):
                raise CollectionIntegrityError(
                    "Hash do manifesto ativo não coincide com o ponteiro."
                )
            return collection

        # Inspeção nunca cria a coleção legada. Uma rota de saúde não deve
        # modificar o banco apenas para dizer que ele ainda não foi preparado.
        existing_names = {
            collection.name for collection in cls.get_client().list_collections()
        }
        collection_name = cls.base_collection_name()
        if collection_name not in existing_names:
            raise ActiveCollectionUnavailableError(
                f"A coleção legada {collection_name!r} não existe."
            )
        return cls._get_strict_collection(
            collection_name,
            with_embedding_function=False,
        )

    @classmethod
    def get_collection(cls):
        """Resolve a ativa sem jamais criar o nome contido no ponteiro."""

        pointer = cls.load_active_pointer()
        if pointer:
            collection_name = str(pointer["collection_name"])
            collection = cls._get_strict_collection(collection_name)
            manifest = cls.load_manifest(collection_name, required=True)
            actual_manifest_hash = sha256_json(manifest)
            expected_manifest_hash = pointer.get("manifest_sha256")
            if expected_manifest_hash != actual_manifest_hash:
                raise CollectionIntegrityError(
                    "Hash do manifesto ativo não coincide com o ponteiro."
                )
            cls.validate_collection_integrity(collection_name, manifest=manifest)
            return collection

        # Compatibilidade restrita: sem ponteiro, a instalação antiga usava
        # exatamente esta coleção e não possuía manifesto.
        return cls.get_client().get_or_create_collection(
            name=cls.base_collection_name(),
            embedding_function=cls._get_embedding_function(),
            metadata={"description": "Documentos usados pelo sistema RAG veterinário"},
            configuration={"hnsw": {"space": "cosine"}},
        )

    @classmethod
    def create_staging_collection(cls, collection_name: str, *, profile: str):
        if not cls.is_versioned_collection(collection_name):
            raise ValueError("Coleção staged deve usar um nome versionado.")
        return cls.get_client().create_collection(
            name=collection_name,
            embedding_function=cls._get_embedding_function(),
            metadata={
                "description": "Coleção candidata de documentos veterinários",
                "profile": profile,
                "recipe_sha256": embedding_recipe_sha256(),
            },
            configuration={"hnsw": {"space": "cosine"}},
        )

    @classmethod
    def write_manifest(cls, collection_name: str, manifest: dict) -> str:
        if manifest.get("collection_name") != collection_name:
            raise ValueError("O manifesto não corresponde à coleção.")
        atomic_write_json(cls.manifest_path(collection_name), manifest)
        return sha256_json(manifest)

    @classmethod
    def load_manifest(
        cls,
        collection_name: str,
        *,
        required: bool | None = None,
    ) -> dict | None:
        path = cls.manifest_path(collection_name)
        must_exist = (
            cls.is_versioned_collection(collection_name)
            if required is None
            else required
        )
        if not path.exists():
            if must_exist:
                raise MissingManifestError(
                    f"Coleção versionada sem manifesto: {collection_name}"
                )
            return None
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise MissingManifestError(
                f"Manifesto inválido de {collection_name}: {error}"
            ) from error
        if not isinstance(manifest, dict):
            raise MissingManifestError(
                f"Manifesto de {collection_name} deve ser um objeto JSON."
            )
        return manifest

    @classmethod
    def validate_collection_integrity(
        cls,
        collection_name: str,
        *,
        manifest: dict | None = None,
    ) -> dict:
        collection = cls._get_strict_collection(collection_name)

        # A única leitura sem manifesto admitida é a coleção-base legada.
        if manifest is None:
            manifest = cls.load_manifest(collection_name)
        if manifest is None and collection_name == cls.base_collection_name():
            return {"legacy": True, "chunk_count": collection.count()}
        if manifest is None:
            raise MissingManifestError(collection_name)

        required_paths = (
            ("collection_name",),
            ("profile",),
            ("embedding", "model"),
            ("embedding", "revision"),
            ("embedding", "dimensions"),
            ("chunking", "recipe_sha256"),
            ("sources", "document_count"),
            ("sources", "source_set_sha256"),
            ("chunks", "count"),
            ("chunks", "ids_sha256"),
            ("chunks", "content_sha256"),
        )
        for path in required_paths:
            value: Any = manifest
            for part in path:
                value = value.get(part) if isinstance(value, dict) else None
            if value in (None, ""):
                raise CollectionIntegrityError(
                    f"Manifesto sem campo obrigatório: {'.'.join(path)}"
                )

        if manifest["collection_name"] != collection_name:
            raise CollectionIntegrityError("Nome da coleção diverge do manifesto.")
        if manifest["embedding"]["model"] != EMBEDDING_MODEL_NAME:
            raise CollectionIntegrityError("Modelo do manifesto é incompatível.")
        if manifest["embedding"]["revision"] != EMBEDDING_MODEL_REVISION:
            raise CollectionIntegrityError("Revisão do embedding é incompatível.")
        if manifest["chunking"]["recipe_sha256"] != embedding_recipe_sha256():
            raise CollectionIntegrityError("Receita de chunks é incompatível.")

        records = collection.get(include=["documents", "metadatas"])
        identifiers = list(records.get("ids") or [])
        documents = list(records.get("documents") or [])
        metadatas = list(records.get("metadatas") or [])
        actual = {
            "count": len(identifiers),
            "ids_sha256": chunk_ids_sha256(identifiers),
            "content_sha256": chunk_content_sha256(
                identifiers, documents, metadatas
            ),
        }
        expected = manifest["chunks"]
        for field_name, actual_value in actual.items():
            if expected.get(field_name) != actual_value:
                raise CollectionIntegrityError(
                    f"Integridade divergente em chunks.{field_name}: "
                    f"esperado={expected.get(field_name)!r}, real={actual_value!r}"
                )
        return actual

    @classmethod
    def activate_collection(cls, collection_name: str) -> dict:
        manifest = cls.load_manifest(collection_name)
        cls.validate_collection_integrity(collection_name, manifest=manifest)
        previous_pointer = cls.load_active_pointer()
        if previous_pointer:
            previous_collection = previous_pointer.get("collection_name")
        else:
            existing_names = {
                collection.name for collection in cls.get_client().list_collections()
            }
            previous_collection = (
                cls.base_collection_name()
                if cls.base_collection_name() in existing_names
                else None
            )
        pointer = {
            "schema_version": 1,
            "collection_name": collection_name,
            "previous_collection": previous_collection,
            "activated_at": datetime.now(timezone.utc).isoformat(),
            "manifest_sha256": sha256_json(manifest),
            "profile": manifest["profile"],
        }
        atomic_write_json(cls.pointer_path(), pointer)
        return pointer

    @classmethod
    def rollback(cls, collection_name: str | None = None) -> dict:
        pointer = cls.load_active_pointer()
        if pointer is None:
            raise ActiveCollectionUnavailableError("Não existe ponteiro para rollback.")
        target = collection_name or pointer.get("previous_collection")
        if not target:
            raise ActiveCollectionUnavailableError("Ponteiro sem coleção anterior.")

        if target == cls.base_collection_name():
            cls._get_strict_collection(target)
            previous = pointer["collection_name"]
            legacy_pointer = {
                "schema_version": 1,
                "collection_name": target,
                "previous_collection": previous,
                "activated_at": datetime.now(timezone.utc).isoformat(),
                "manifest_sha256": None,
                "profile": "legacy",
            }
            # Sem ponteiro, o fallback legado abre somente o nome-base.
            cls.pointer_path().unlink(missing_ok=True)
            return legacy_pointer
        return cls.activate_collection(str(target))

    @classmethod
    def delete_collection(cls, collection_name: str) -> None:
        pointer = cls.load_active_pointer()
        active_name = (
            pointer.get("collection_name") if pointer else cls.base_collection_name()
        )
        if collection_name == active_name:
            raise ValueError("A coleção ativa não pode ser excluída.")
        cls.get_client().delete_collection(collection_name)
        cls.manifest_path(collection_name).unlink(missing_ok=True)

    @classmethod
    def list_versioned_collections(cls) -> list[dict]:
        results: list[dict] = []
        for collection in cls.get_client().list_collections():
            name = collection.name
            if cls.is_versioned_collection(name):
                results.append(
                    {"name": name, "manifest": cls.load_manifest(name)}
                )
        return sorted(results, key=lambda item: item["name"])
