"""Testes do processamento determinístico anterior ao ChromaDB."""

import json
import re
import sys
from pathlib import Path

import pytest

from app.database import ingest_documents
from app.database.document_processing import (
    DocumentChunk,
    PageText,
    SectionText,
    TextUnit,
    chunk_metadata,
    chunk_section,
    clean_structured_text,
    count_tokens,
    dehyphenate_line_breaks,
    detect_sections,
    filter_sections,
    load_metadata,
    process_document,
    process_pages,
    remove_repeated_margin_lines,
)


class FakeTokenizer:
    """Tokenizer offline com fronteiras observáveis nos testes."""

    model_max_length = 128

    def encode(
        self,
        text,
        add_special_tokens=True,
        truncation=False,
    ):
        del truncation
        tokens = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
        special_tokens = 2 if add_special_tokens else 0
        return list(range(len(tokens) + special_tokens))


@pytest.fixture
def tokenizer():
    return FakeTokenizer()


def base_metadata(**overrides):
    metadata = {
        "title": "Canine emergency source",
        "source": "Journal",
        "document_type": "peer_reviewed_review",
        "validation_status": "published_not_locally_validated",
        "species": "dog",
        "topic": "test",
        "indexing": {},
    }
    metadata.update(overrides)
    return metadata


def test_dehyphenation_recompoe_quebra_de_linha():
    assert dehyphenate_line_breaks("severe hyper-\nthermia") == (
        "severe hyperthermia"
    )


def test_hifen_legitimo_na_mesma_linha_e_preservado():
    assert clean_structured_text("peer-reviewed evidence") == (
        "peer-reviewed evidence"
    )


def test_references_e_detectada_e_excluida_por_padrao():
    pages = [
        PageText(
            1,
            "Abstract\nUseful clinical evidence.\nReferences\n[1] Noise.",
        )
    ]

    sections, used_fallback = detect_sections(pages)
    included, excluded = filter_sections(sections, {})

    assert not used_fallback
    assert "References" in [section.title for section in sections]
    assert "References" in excluded
    assert [section.title for section in included] == ["Abstract"]


def test_references_e_terminal_mesmo_com_siglas_em_maiusculas():
    pages = [
        PageText(
            1,
            "Abstract\nUseful clinical evidence.\nReferences\n"
            "PMID:26238698\nDOI\nMore citation text.",
        )
    ]

    sections, _ = detect_sections(pages)
    included, excluded = filter_sections(sections, {})

    assert [section.title for section in sections] == ["Abstract", "References"]
    assert [section.title for section in included] == ["Abstract"]
    assert excluded == ["References"]


def test_exclusao_configurada_via_sidecar():
    pages = [PageText(1, "Abstract\nKeep this.\nAppendix\nRemove this.")]
    indexing = {"exclude_sections": ["Appendix"]}
    sections, _ = detect_sections(pages, ["Appendix"])
    included, excluded = filter_sections(sections, indexing)

    assert [section.title for section in included] == ["Abstract"]
    assert excluded == ["Appendix"]


def test_include_sections_funciona_com_heading_configurado():
    pages = [
        PageText(
            1,
            "Abstract\nGeneral text.\nCustom Findings\nTriage evidence.",
        )
    ]
    indexing = {"include_sections": ["Custom Findings"]}
    sections, _ = detect_sections(pages, ["Custom Findings"])
    included, excluded = filter_sections(sections, indexing)

    assert [section.title for section in included] == ["Custom Findings"]
    assert "Abstract" in excluded


def test_fallback_quando_nao_ha_heading(tokenizer):
    report = process_pages(
        "legacy.txt",
        [PageText(0, "Texto antigo sem estrutura, ainda ingerível.")],
        base_metadata(),
        tokenizer,
    )

    assert report.used_section_fallback
    assert report.included_sections == ("Document",)
    assert report.chunks


def test_palavras_maiusculas_isoladas_nao_viram_headings():
    pages = [PageText(0, "PROTOCOLO\nSINTÉTICO\nTexto clínico completo.")]

    sections, used_fallback = detect_sections(pages)

    assert used_fallback
    assert [section.title for section in sections] == ["Document"]


def test_cabecalho_repetido_nas_margens_e_removido():
    pages = [
        PageText(number, f"Journal Header\nClinical content {number}.")
        for number in range(1, 4)
    ]

    cleaned = remove_repeated_margin_lines(pages)

    assert all("Journal Header" not in page.text for page in cleaned)
    assert all("Clinical content" in page.text for page in cleaned)


def test_chunks_respeitam_limite_e_overlap_comeca_em_palavra(tokenizer):
    text = " ".join(f"palavra{index}" for index in range(80))
    section = SectionText("Clinical signs", [TextUnit(text, 2, 2)])

    chunks, fallback_splits = chunk_section(
        section,
        "Heatstroke",
        tokenizer,
        target_tokens=28,
        overlap_tokens=5,
        safe_limit=32,
    )

    assert fallback_splits == 1
    assert len(chunks) > 2
    assert all(chunk.token_count <= 32 for chunk in chunks)

    contents = [chunk.text.split("\n\n", 1)[1] for chunk in chunks]
    assert all(re.match(r"^palavra\d+\b", content) for content in contents)
    assert set(contents[0].split()) & set(contents[1].split())


def test_prefixo_esta_dentro_da_contagem_de_tokens(tokenizer):
    section = SectionText(
        "Diagnosis",
        [TextUnit("Evidence for initial triage.", 3, 3)],
    )
    chunks, _ = chunk_section(section, "Heatstroke", tokenizer)

    assert chunks[0].text.startswith(
        "Document title: Heatstroke\nSection: Diagnosis\n\n"
    )
    assert chunks[0].token_count == count_tokens(tokenizer, chunks[0].text)


def test_section_e_intervalo_de_paginas_sao_preservados(tokenizer):
    report = process_pages(
        "paper.pdf",
        [
            PageText(1, "Diagnosis\nFirst clinical sentence."),
            PageText(2, "Second clinical sentence."),
        ],
        base_metadata(),
        tokenizer,
    )

    assert report.chunks[0].section == "Diagnosis"
    assert report.chunks[0].page_start == 1
    assert report.chunks[0].page_end == 2


def test_metadados_adicionais_e_de_chunk_sao_preservados():
    metadata = base_metadata(
        authors="A; B",
        year=2017,
        doi="10.1/example",
        journal="Temperature",
        language="en",
        source_url="https://doi.org/10.1/example",
    )
    chunk = DocumentChunk("text", "Prognosis", 4, 5, 20)

    result = chunk_metadata(metadata, chunk, "paper.pdf", ".pdf", 7)

    assert result["authors"] == "A; B"
    assert result["year"] == 2017
    assert result["section"] == "Prognosis"
    assert result["page"] == 4
    assert result["page_start"] == 4
    assert result["page_end"] == 5
    assert result["token_count"] == 20


def test_documento_sem_json_usa_defaults_neutros(tmp_path, caplog):
    document_path = tmp_path / "real_source.txt"
    document_path.write_text("evidence", encoding="utf-8")

    metadata = load_metadata(document_path)

    assert metadata["document_type"] == "unknown"
    assert metadata["validation_status"] == "not_informed"
    assert "Metadados não encontrados" in caplog.text


def test_warning_para_secao_configurada_ausente(caplog):
    sections = [SectionText("Abstract", [TextUnit("text", 1, 1)])]

    filter_sections(
        sections,
        {"exclude_sections": ["Nonexistent appendix"]},
    )

    assert "Seção configurada e não encontrada" in caplog.text


def test_apenas_secoes_excluidas_nao_produzem_chunks(tokenizer):
    report = process_pages(
        "references-only.pdf",
        [PageText(1, "References\n[1] Citation only.")],
        base_metadata(),
        tokenizer,
    )

    assert report.chunks == ()
    assert report.included_sections == ()
    assert report.excluded_sections == ("References",)


def test_exclude_pages_remove_pagina_antes_do_processamento(tokenizer):
    report = process_pages(
        "paper.pdf",
        [
            PageText(1, "Editorial cover without heading."),
            PageText(2, "Abstract\nUseful evidence."),
        ],
        base_metadata(indexing={"exclude_pages": [1]}),
        tokenizer,
    )

    assert all(chunk.page_start >= 2 for chunk in report.chunks)
    assert not any("Editorial cover" in chunk.text for chunk in report.chunks)


def test_inspect_nao_consulta_nem_altera_colecao(
    tmp_path,
    monkeypatch,
    tokenizer,
):
    document_path = tmp_path / "legacy.txt"
    document_path.write_text("Legacy clinical evidence.", encoding="utf-8")
    document_path.with_suffix(".json").write_text(
        json.dumps(base_metadata()),
        encoding="utf-8",
    )

    chroma_module = sys.modules["app.database.chroma_client"]

    def forbidden():
        raise AssertionError("O modo inspect tentou abrir o ChromaDB")

    monkeypatch.setattr(
        chroma_module.ChromaDBClient,
        "get_collection",
        staticmethod(forbidden),
    )

    reports = ingest_documents.inspect_documents(
        document_path=document_path,
        tokenizer=tokenizer,
    )

    assert len(reports) == 1
    assert reports[0].chunks


def test_pdf_real_exclui_ruido_e_preserva_secoes_clinicas(tokenizer):
    document_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "documents"
        / "pathophysiology_heatstroke_dogs_2017.pdf"
    )

    processed = process_document(document_path, tokenizer=tokenizer)
    report = processed.report

    assert report.pages_extracted == 16
    assert "Clinical signs upon presentation" in report.included_sections
    assert "Diagnosis" in report.included_sections
    assert "Prognosis" in report.included_sections
    assert "Conclusions" in report.included_sections
    assert "References" in report.excluded_sections
    assert "About the authors" in report.excluded_sections
    assert all(chunk.section != "References" for chunk in report.chunks)
    assert all(chunk.page_end <= 11 for chunk in report.chunks)
    assert all(chunk.page_start >= 2 for chunk in report.chunks)
    assert all(
        chunk.token_count <= tokenizer.model_max_length
        for chunk in report.chunks
    )
    assert any("devastating" in chunk.text for chunk in report.chunks)
    assert not any("devas- tating" in chunk.text for chunk in report.chunks)
    assert not any("Permission to reuse" in chunk.text for chunk in report.chunks)


def test_ingestao_vazia_nao_apaga_nem_insere(
    tmp_path,
    monkeypatch,
    tokenizer,
):
    document_path = tmp_path / "excluded.txt"
    document_path.write_text("References\n[1] Citation only.", encoding="utf-8")
    document_path.with_suffix(".json").write_text(
        json.dumps(base_metadata()),
        encoding="utf-8",
    )
    monkeypatch.setattr(ingest_documents, "DOCUMENTS_DIRECTORY", tmp_path)

    class Collection:
        def delete(self, **kwargs):
            raise AssertionError(f"delete indevido: {kwargs}")

        def upsert(self, **kwargs):
            raise AssertionError(f"upsert indevido: {kwargs}")

    with pytest.raises(ValueError, match="Nenhum texto utilizável"):
        ingest_documents.ingest_document(
            Collection(),
            document_path,
            tokenizer=tokenizer,
        )


def test_ingestao_entrega_ids_documentos_e_metadados_ao_chroma(
    tmp_path,
    monkeypatch,
    tokenizer,
):
    document_path = tmp_path / "source.txt"
    document_path.write_text(
        "Diagnosis\nClinical evidence for safe initial triage.",
        encoding="utf-8",
    )
    document_path.with_suffix(".json").write_text(
        json.dumps(base_metadata(authors="A; B", year=2026)),
        encoding="utf-8",
    )
    monkeypatch.setattr(ingest_documents, "DOCUMENTS_DIRECTORY", tmp_path)

    class Collection:
        def __init__(self):
            self.deleted_where = None
            self.upserts = []

        def delete(self, *, where):
            self.deleted_where = where

        def upsert(self, **kwargs):
            self.upserts.append(kwargs)

    collection = Collection()
    chunk_count = ingest_documents.ingest_document(
        collection,
        document_path,
        tokenizer=tokenizer,
    )

    assert chunk_count == 1
    assert collection.deleted_where == {"source_file": "source.txt"}
    assert len(collection.upserts) == 1
    assert len(collection.upserts[0]["ids"][0]) == 64
    assert collection.upserts[0]["documents"][0].startswith("Document title:")
    assert collection.upserts[0]["metadatas"][0]["section"] == "Diagnosis"
    assert collection.upserts[0]["metadatas"][0]["authors"] == "A; B"
