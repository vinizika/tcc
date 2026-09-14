import copy

import pytest

from verify_vector_consensus import (
    ConsensusError,
    verify_artifact_consensus,
    verify_fingerprint_consensus,
)


IDENTITY = {
    "collection": "documents__run",
    "document_count": 2,
    "chunk_count": 3,
    "chunk_ids_sha256": "ids",
    "content_sha256": "content",
    "embedding_model": "model",
    "embedding_revision": "revision",
    "recipe_sha256": "recipe",
    "source_set_sha256": "sources",
    "profile": "experimental",
}


def fingerprint(**overrides):
    identity = {**IDENTITY, **overrides}
    return {"vector_store": identity}


def artifacts():
    manifest = {
        "collection_name": IDENTITY["collection"],
        "profile": IDENTITY["profile"],
        "embedding": {
            "model": IDENTITY["embedding_model"],
            "revision": IDENTITY["embedding_revision"],
        },
        "chunking": {"recipe_sha256": IDENTITY["recipe_sha256"]},
        "sources": {
            "document_count": IDENTITY["document_count"],
            "source_set_sha256": IDENTITY["source_set_sha256"],
        },
        "chunks": {
            "count": IDENTITY["chunk_count"],
            "ids_sha256": IDENTITY["chunk_ids_sha256"],
            "content_sha256": IDENTITY["content_sha256"],
        },
    }
    import hashlib
    import json

    digest = hashlib.sha256(
        json.dumps(
            manifest,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    receipt = {
        "collection_name": IDENTITY["collection"],
        "profile": IDENTITY["profile"],
        "chunk_count": IDENTITY["chunk_count"],
        "manifest_sha256": digest,
    }
    return manifest, fingerprint(), receipt


def test_fingerprints_iguais_entram_em_consenso():
    result = verify_fingerprint_consensus([fingerprint(), fingerprint()])
    assert result["status"] == "consensus"


@pytest.mark.parametrize(
    "field,value",
    [
        ("chunk_count", 4),
        ("chunk_ids_sha256", "other"),
        ("content_sha256", "other"),
        ("embedding_model", "other"),
        ("embedding_revision", "other"),
        ("collection", "other"),
        ("profile", "curated"),
    ],
)
def test_fingerprint_divergente_falha(field, value):
    with pytest.raises(ConsensusError, match="divergentes"):
        verify_fingerprint_consensus(
            [fingerprint(), fingerprint(**{field: value})]
        )


def test_fingerprint_sem_campo_obrigatorio_falha():
    with pytest.raises(ConsensusError, match="obrigatório"):
        verify_fingerprint_consensus(
            [fingerprint(), fingerprint(content_sha256=None)]
        )


def test_manifesto_fingerprint_e_recibo_concordam():
    manifest, stored_fingerprint, receipt = artifacts()
    result = verify_artifact_consensus(
        manifest=manifest,
        fingerprint=stored_fingerprint,
        receipt=receipt,
    )
    assert result["chunk_count"] == 3


def test_recibo_divergente_falha():
    manifest, stored_fingerprint, receipt = artifacts()
    receipt["profile"] = "curated"
    with pytest.raises(ConsensusError, match="receipt.profile"):
        verify_artifact_consensus(
            manifest=manifest,
            fingerprint=stored_fingerprint,
            receipt=receipt,
        )


def test_contagem_real_divergente_falha():
    manifest, stored_fingerprint, receipt = artifacts()
    with pytest.raises(ConsensusError, match="actual.chunk_count"):
        verify_artifact_consensus(
            manifest=manifest,
            fingerprint=stored_fingerprint,
            receipt=receipt,
            actual={
                "chunk_count": 2,
                "chunk_ids_sha256": "ids",
                "content_sha256": "content",
            },
        )


def test_manifesto_ausente_de_campo_falha():
    manifest, stored_fingerprint, receipt = artifacts()
    broken = copy.deepcopy(manifest)
    del broken["embedding"]["revision"]
    with pytest.raises(ConsensusError, match="manifesto"):
        verify_artifact_consensus(
            manifest=broken,
            fingerprint=stored_fingerprint,
            receipt=receipt,
        )
