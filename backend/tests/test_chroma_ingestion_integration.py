"""Integrações reais em ChromaDB persistente e temporário."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest


class DeterministicEmbedding:
    """Embedding pequeno e offline, suficiente para exercitar o Chroma real."""

    @staticmethod
    def name():
        return "deterministic-test"

    def get_config(self):
        return {}

    @staticmethod
    def build_from_config(config):
        del config
        return DeterministicEmbedding()

    def __call__(self, input):
        return self.embed_documents(input)

    def embed_documents(self, input):
        return [
            [float((sum(map(ord, text)) + index) % 31) / 31 for index in range(8)]
            for text in input
        ]

    def embed_query(self, input):
        return self.embed_documents(input)


@pytest.fixture
def real_chroma_module():
    """O conftest global usa dublê; estes testes carregam o módulo verdadeiro."""

    module_name = "app.database.chroma_client"
    previous = sys.modules.get(module_name)
    module_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "database"
        / "chroma_client.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    try:
        yield module
    finally:
        module.ChromaDBClient.reset_configuration()
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous


def manifest_for(module, collection_name, ids, documents, metadatas):
    from app.database.embedding_config import (
        EMBEDDING_MODEL_NAME,
        EMBEDDING_MODEL_REVISION,
        embedding_recipe_sha256,
    )

    return {
        "schema_version": 1,
        "collection_name": collection_name,
        "profile": "experimental",
        "embedding": {
            "model": EMBEDDING_MODEL_NAME,
            "revision": EMBEDDING_MODEL_REVISION,
            "dimensions": 8,
        },
        "chunking": {"recipe_sha256": embedding_recipe_sha256()},
        "sources": {
            "document_count": 2,
            "source_set_sha256": "test-source-set",
        },
        "chunks": {
            "count": len(ids),
            "ids_sha256": module.chunk_ids_sha256(ids),
            "content_sha256": module.chunk_content_sha256(
                ids, documents, metadatas
            ),
        },
    }


def create_candidate(module, tmp_path, suffix="candidate"):
    client = module.ChromaDBClient
    client.configure(
        path=tmp_path,
        collection_name="documents",
        embedding_function=DeterministicEmbedding(),
    )
    name = f"documents__20260913T120000Z__{suffix}"
    collection = client.create_staging_collection(name, profile="experimental")
    ids = ["chunk-1", "chunk-2"]
    documents = ["title section clean body", "other clean body"]
    metadatas = [
        {"body": "clean body", "topic": "heatstroke", "species": "dog"},
        {"body": "other clean body", "topic": "seizures", "species": "dog_and_cat"},
    ]
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    manifest = manifest_for(module, name, ids, documents, metadatas)
    client.write_manifest(name, manifest)
    return name, manifest


def test_stage_nao_substitui_a_colecao_ativa(real_chroma_module, tmp_path):
    client = real_chroma_module.ChromaDBClient
    name, _ = create_candidate(real_chroma_module, tmp_path)

    assert client.pointer_path().exists() is False
    assert client.get_collection().name == "documents"
    assert name in [item["name"] for item in client.list_versioned_collections()]


def test_ativacao_persiste_e_rollback_reabre_legada(real_chroma_module, tmp_path):
    client = real_chroma_module.ChromaDBClient
    name, _ = create_candidate(real_chroma_module, tmp_path)
    # Materializa explicitamente a exceção legada antes da primeira ativação.
    assert client.get_collection().name == "documents"

    pointer = client.activate_collection(name)
    assert pointer["collection_name"] == name
    assert client.get_collection().count() == 2

    client.configure(
        path=tmp_path,
        collection_name="documents",
        embedding_function=DeterministicEmbedding(),
    )
    assert client.get_collection().name == name
    rollback = client.rollback()
    assert rollback["collection_name"] == "documents"
    assert client.get_collection().name == "documents"


def test_ponteiro_obsoleto_falha_sem_criar_colecao(
    real_chroma_module, tmp_path
):
    client = real_chroma_module.ChromaDBClient
    client.configure(
        path=tmp_path,
        collection_name="documents",
        embedding_function=DeterministicEmbedding(),
    )
    client.get_client()
    pointer = {
        "collection_name": "documents__missing",
        "manifest_sha256": "0" * 64,
    }
    client.pointer_path().write_text(json.dumps(pointer), encoding="utf-8")
    before = [item.name for item in client.get_client().list_collections()]

    with pytest.raises(real_chroma_module.ActiveCollectionUnavailableError):
        client.get_collection()

    after = [item.name for item in client.get_client().list_collections()]
    assert after == before
    assert "documents__missing" not in after


def test_ativacao_valida_hash_e_preserva_estado_atual(
    real_chroma_module, tmp_path
):
    client = real_chroma_module.ChromaDBClient
    name, manifest = create_candidate(real_chroma_module, tmp_path)
    manifest["chunks"]["count"] = 999
    client.write_manifest(name, manifest)

    with pytest.raises(real_chroma_module.CollectionIntegrityError):
        client.activate_collection(name)

    assert client.pointer_path().exists() is False


def test_versionada_sem_manifesto_e_rejeitada(real_chroma_module, tmp_path):
    client = real_chroma_module.ChromaDBClient
    client.configure(
        path=tmp_path,
        collection_name="documents",
        embedding_function=DeterministicEmbedding(),
    )
    name = "documents__20260913T120000Z__orphan"
    client.create_staging_collection(name, profile="experimental")

    with pytest.raises(real_chroma_module.MissingManifestError):
        client.validate_collection_integrity(name)


def test_colecao_ativa_nao_pode_ser_excluida(real_chroma_module, tmp_path):
    client = real_chroma_module.ChromaDBClient
    name, _ = create_candidate(real_chroma_module, tmp_path)
    client.activate_collection(name)

    with pytest.raises(ValueError, match="ativa"):
        client.delete_collection(name)


def test_manifesto_sem_identidade_das_fontes_e_rejeitado(
    real_chroma_module, tmp_path
):
    client = real_chroma_module.ChromaDBClient
    name, manifest = create_candidate(real_chroma_module, tmp_path)
    manifest.pop("sources")
    client.write_manifest(name, manifest)

    with pytest.raises(
        real_chroma_module.CollectionIntegrityError,
        match="sources.document_count",
    ):
        client.activate_collection(name)


def test_primeira_ativacao_sem_legada_nao_inventa_rollback(
    real_chroma_module, tmp_path
):
    client = real_chroma_module.ChromaDBClient
    name, _ = create_candidate(real_chroma_module, tmp_path)

    pointer = client.activate_collection(name)

    assert pointer["previous_collection"] is None
    with pytest.raises(
        real_chroma_module.ActiveCollectionUnavailableError,
        match="sem coleção anterior",
    ):
        client.rollback()


def test_rollback_invalido_preserva_ponteiro_atual(real_chroma_module, tmp_path):
    client = real_chroma_module.ChromaDBClient
    name, _ = create_candidate(real_chroma_module, tmp_path)
    client.activate_collection(name)
    before = client.load_active_pointer()

    with pytest.raises(real_chroma_module.MissingManifestError):
        client.rollback("documents__missing")

    assert client.load_active_pointer() == before
    assert client.get_collection().name == name


def test_inspecao_nao_carrega_embedding_nem_cria_colecao(
    real_chroma_module, tmp_path, monkeypatch
):
    client = real_chroma_module.ChromaDBClient
    client.configure(
        path=tmp_path,
        collection_name="documents",
        embedding_function=DeterministicEmbedding(),
    )
    client.get_collection()

    monkeypatch.setattr(
        client,
        "_get_embedding_function",
        classmethod(
            lambda cls: (_ for _ in ()).throw(
                AssertionError("modelo de embedding carregado durante inspeção")
            )
        ),
    )

    collection = client.get_collection_for_inspection()

    assert collection.name == "documents"
    assert collection.count() == 0
    assert [item.name for item in client.get_client().list_collections()] == [
        "documents"
    ]
