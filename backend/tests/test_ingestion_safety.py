"""Travas de política executadas antes de qualquer mutação no Chroma."""

import hashlib
import json
import re

import pytest

from app.database import ingest_documents


class FakeTokenizer:
    model_max_length = 128

    def encode(self, text, add_special_tokens=True, truncation=False):
        del truncation
        tokens = re.findall(r"\w+|[^\w\s]", text)
        return list(range(len(tokens) + (2 if add_special_tokens else 0)))


def write_document(directory, name="source.txt", **metadata_overrides):
    path = directory / name
    path.write_text(
        "Clinical signs\nEvidence for initial veterinary triage.",
        encoding="utf-8",
    )
    metadata = {
        "title": "Veterinary source",
        "source": "Example institution",
        "source_url": "https://example.test/source",
        "document_type": "owner_guidance",
        "validation_status": "pending_specialist",
        "species": "dog",
        "topic": "known_topic",
        "ingestion_scope": "experimental_only",
        "indexing": {},
    }
    metadata.update(metadata_overrides)
    path.with_suffix(".json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )
    return path


def write_map(path):
    path.write_text("id,quadro\nknown_topic,Known topic\n", encoding="utf-8")


def test_curated_sem_elegiveis_falha_antes_de_tokenizer_e_chroma(
    tmp_path, monkeypatch
):
    write_document(tmp_path)
    monkeypatch.setattr(ingest_documents, "DOCUMENTS_DIRECTORY", tmp_path)
    monkeypatch.setattr(
        ingest_documents,
        "load_embedding_tokenizer",
        lambda: (_ for _ in ()).throw(AssertionError("tokenizer carregado")),
    )

    with pytest.raises(
        ingest_documents.IngestionValidationError,
        match="Nenhum documento elegível",
    ):
        ingest_documents.prepare_ingestion(profile="curated")


@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({"validation_status": "pending_specialist"}, "validation_status"),
        ({"ingestion_scope": "experimental_only"}, "ingestion_scope"),
        ({"species": "dogs_and_cats"}, "species"),
        ({"topic": "unknown"}, "topic"),
    ],
)
def test_curated_recusa_campos_nao_aprovados(
    tmp_path, monkeypatch, overrides, expected
):
    map_path = tmp_path / "map.csv"
    write_map(map_path)
    metadata = {
        "ingestion_scope": "curated",
        "validation_status": "approved_by_specialist",
        "species": "dog",
        "specialist": {
            "verdict": "approved",
            "name": "Reviewer",
            "date": "2026-09-13",
        },
        "rights": {
            "status": "allowed",
            "basis": "permission",
            "checked_by": "Reviewer",
            "date": "2026-09-13",
        },
    }
    metadata.update(overrides)
    document = write_document(tmp_path, **metadata)
    sidecar = json.loads(document.with_suffix(".json").read_text())
    sidecar["captured_sha256"] = hashlib.sha256(document.read_bytes()).hexdigest()
    document.with_suffix(".json").write_text(json.dumps(sidecar), encoding="utf-8")
    monkeypatch.setattr(ingest_documents, "DOCUMENTS_DIRECTORY", tmp_path)
    monkeypatch.setattr(ingest_documents, "TOPIC_MAP_PATH", map_path)

    with pytest.raises(ingest_documents.IngestionValidationError, match=expected):
        ingest_documents.prepare_ingestion(
            profile="curated", tokenizer=FakeTokenizer()
        )


def test_experimental_aceita_pendente_mas_registra_warning(tmp_path, monkeypatch):
    write_document(tmp_path)
    monkeypatch.setattr(ingest_documents, "DOCUMENTS_DIRECTORY", tmp_path)

    prepared = ingest_documents.prepare_ingestion(
        profile="experimental", tokenizer=FakeTokenizer()
    )

    assert len(prepared.documents) == 1
    assert prepared.warning_count >= 1
    assert "aprovação clínica" in " ".join(prepared.documents[0].warnings)


def test_legacy_rechunk_seleciona_apenas_protocolos_sinteticos(
    tmp_path, monkeypatch
):
    write_document(tmp_path, "synthetic.txt", document_type="synthetic_protocol")
    write_document(tmp_path, "paper.txt", document_type="peer_reviewed_article")
    monkeypatch.setattr(ingest_documents, "DOCUMENTS_DIRECTORY", tmp_path)

    prepared = ingest_documents.prepare_ingestion(
        profile="legacy_rechunk", tokenizer=FakeTokenizer()
    )

    assert [item.path.name for item in prepared.documents] == ["synthetic.txt"]


def test_body_limpo_e_texto_de_embedding_ficam_separados(tmp_path, monkeypatch):
    write_document(tmp_path)
    monkeypatch.setattr(ingest_documents, "DOCUMENTS_DIRECTORY", tmp_path)
    prepared = ingest_documents.prepare_ingestion(
        profile="experimental", tokenizer=FakeTokenizer()
    )
    chunk = prepared.documents[0].processed.report.chunks[0]

    assert chunk.text.startswith("Document title:")
    assert not chunk.body.startswith("Document title:")
    assert chunk.body in chunk.text
