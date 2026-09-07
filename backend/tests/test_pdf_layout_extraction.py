"""Regressões da extração científica orientada a blocos e coordenadas."""

import re
from pathlib import Path

import pytest

from app.database import document_processing, ingest_documents
from app.database.document_processing import (
    clean_structured_text,
    dehyphenate_line_breaks,
    extract_pdf_pages_with_statistics,
    process_document,
)
from app.database.pdf_layout_extraction import (
    LayoutBlock,
    clean_layout_blocks,
    is_caption_block,
    normalize_pdf_unicode,
    order_blocks_for_reading,
)


class FakeTokenizer:
    model_max_length = 128

    def encode(self, text, add_special_tokens=True, truncation=False):
        del truncation
        tokens = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
        return list(range(len(tokens) + (2 if add_special_tokens else 0)))


def block(
    text,
    x0,
    y0,
    x1,
    y1,
    *,
    page=1,
    sequence=0,
    width=600,
    height=800,
):
    return LayoutBlock(
        page_number=page,
        text=text,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        page_width=width,
        page_height=height,
        sequence=sequence,
    )


def test_pagina_de_uma_coluna_mantem_ordem_vertical():
    blocks = [
        block("Segundo parágrafo científico.", 50, 180, 550, 230, sequence=1),
        block("Primeiro parágrafo científico.", 50, 80, 550, 130),
    ]

    ordered = order_blocks_for_reading(blocks)

    assert ordered.column_count == 1
    assert [item.text for item in ordered.blocks] == [
        "Primeiro parágrafo científico.",
        "Segundo parágrafo científico.",
    ]


def test_pagina_de_duas_colunas_le_coluna_inteira_primeiro():
    blocks = [
        block("Direita superior com conteúdo suficiente.", 330, 80, 550, 130),
        block("Esquerda inferior com conteúdo suficiente.", 50, 180, 270, 230),
        block("Direita inferior com conteúdo suficiente.", 330, 180, 550, 230),
        block("Esquerda superior com conteúdo suficiente.", 50, 80, 270, 130),
    ]

    ordered = order_blocks_for_reading(blocks)

    assert ordered.column_count == 2
    assert [item.text.split()[0] for item in ordered.blocks] == [
        "Esquerda",
        "Esquerda",
        "Direita",
        "Direita",
    ]


def test_heading_em_largura_total_aparece_antes_das_colunas():
    blocks = [
        block("Corpo direito com evidência clínica.", 330, 100, 550, 180),
        block("Heading científico", 40, 40, 560, 70),
        block("Corpo esquerdo com evidência clínica.", 50, 100, 270, 180),
    ]

    ordered = order_blocks_for_reading(blocks)

    assert ordered.column_count == 2
    assert ordered.blocks[0].text == "Heading científico"
    assert ordered.blocks[1].text.startswith("Corpo esquerdo")
    assert ordered.blocks[2].text.startswith("Corpo direito")


def test_header_repetido_e_removido_por_posicao_e_recorrencia():
    pages = [
        [
            block(f"Journal name {100 + page}", 450, 10, 560, 30, page=page),
            block(f"Conteúdo clínico da página {page}.", 50, 100, 550, 180, page=page),
        ]
        for page in range(1, 4)
    ]

    cleaned = clean_layout_blocks(pages)

    assert cleaned.headers_removed == 3
    assert all(len(page_blocks) == 1 for page_blocks in cleaned.pages)


def test_footer_repetido_e_removido_por_posicao_e_recorrencia():
    pages = [
        [
            block("Rodapé institucional", 50, 760, 300, 790, page=page),
            block(f"Achado científico {page}.", 50, 100, 550, 180, page=page),
        ]
        for page in range(1, 4)
    ]

    cleaned = clean_layout_blocks(pages)

    assert cleaned.footers_removed == 3
    assert all(len(page_blocks) == 1 for page_blocks in cleaned.pages)


def test_numero_de_pagina_isolado_e_removido_na_margem():
    pages = [[block("42", 520, 770, 550, 790)]]

    cleaned = clean_layout_blocks(pages)

    assert cleaned.page_numbers_removed == 1
    assert cleaned.pages == ((),)


def test_bloco_contact_e_identificado_como_editorial():
    pages = [[block("CONTACT Author author@example.org", 50, 400, 550, 440)]]

    cleaned = clean_layout_blocks(pages)

    assert cleaned.editorial_blocks_removed == 1
    assert cleaned.pages == ((),)


def test_legenda_figure_no_inicio_e_excluida():
    pages = [[block("Figure 1. Survival curve and confidence interval.", 50, 300, 550, 350)]]

    cleaned = clean_layout_blocks(pages)

    assert cleaned.captions_removed == 1
    assert cleaned.pages == ((),)


def test_referencia_figura_no_corpo_e_preservada():
    text = "The biomarker increased during follow-up (Fig. 1)."
    pages = [[block(text, 50, 300, 550, 350)]]

    cleaned = clean_layout_blocks(pages)

    assert not is_caption_block(text)
    assert cleaned.pages[0][0].text == text


def test_legenda_table_numerada_e_identificada():
    assert is_caption_block("Table 1. Baseline clinical measurements.")
    assert is_caption_block("TABLE 2: Laboratory findings.")


def test_texto_cientifico_na_margem_nao_e_removido_sem_evidencia():
    scientific_text = "Introduction to a validated longitudinal study."
    pages = [[block(scientific_text, 50, 5, 550, 45)]]

    cleaned = clean_layout_blocks(pages)

    assert cleaned.blocks_removed == 0
    assert cleaned.pages[0][0].text == scientific_text


def test_hifen_legitimo_continua_preservado():
    assert clean_structured_text("exercise-induced heatstroke") == (
        "exercise-induced heatstroke"
    )


def test_dehyphenation_de_quebra_de_linha_continua_funcionando():
    assert dehyphenate_line_breaks("hyper-\nthermia") == "hyperthermia"


def test_unicode_e_ligatura_sao_normalizados_sem_dicionario():
    normalized, recovered, unmapped = normalize_pdf_unicode("signiﬁcantly")

    assert normalized == "significantly"
    assert recovered == 0
    assert unmapped == 0


def test_glifo_de_grau_e_recuperado_apenas_entre_numero_e_unidade():
    normalized, recovered, unmapped = normalize_pdf_unicode("41\x01C / A\x01B")

    assert normalized == "41°C / A�B"
    assert recovered == 1
    assert unmapped == 1


def test_ordem_usa_fallback_se_geometria_for_insuficiente():
    blocks = [
        block("Terceiro", 0, 0, 0, 0, width=0, sequence=2),
        block("Primeiro", 0, 0, 0, 0, width=0, sequence=0),
        block("Segundo", 0, 0, 0, 0, width=0, sequence=1),
    ]

    ordered = order_blocks_for_reading(blocks)

    assert ordered.used_coordinate_fallback
    assert [item.text for item in ordered.blocks] == [
        "Primeiro",
        "Segundo",
        "Terceiro",
    ]


def test_parser_estruturado_faz_fallback_limpo_para_pypdf(monkeypatch):
    def fail(_):
        raise RuntimeError("layout inválido")

    expected_pages = [document_processing.PageText(1, "Texto preservado.")]
    monkeypatch.setattr(document_processing, "extract_pdf_with_layout", fail)
    monkeypatch.setattr(
        document_processing,
        "_extract_pdf_pages_with_pypdf",
        lambda _: expected_pages,
    )

    pages, statistics = extract_pdf_pages_with_statistics(Path("paper.pdf"))

    assert pages == expected_pages
    assert statistics.extractor == "pypdf/simple-fallback"
    assert "layout inválido" in statistics.warnings[0]


def test_falha_em_um_documento_nao_impede_tentativa_do_seguinte(monkeypatch):
    paths = [Path("broken.pdf"), Path("working.pdf")]
    attempted = []

    class Collection:
        def count(self):
            return 1

    def fake_ingest(collection, document_path, tokenizer=None):
        del collection, tokenizer
        attempted.append(document_path.name)
        if document_path.name == "broken.pdf":
            raise ValueError("PDF malformado")
        return 1

    monkeypatch.setattr(ingest_documents, "_document_paths", lambda: paths)
    monkeypatch.setattr(ingest_documents, "ingest_document", fake_ingest)
    monkeypatch.setattr(ingest_documents, "load_embedding_tokenizer", object)

    from app.database.chroma_client import ChromaDBClient

    monkeypatch.setattr(
        ChromaDBClient,
        "get_collection",
        staticmethod(lambda: Collection()),
    )

    with pytest.raises(RuntimeError, match="broken.pdf"):
        ingest_documents.ingest_documents()

    assert attempted == ["broken.pdf", "working.pdf"]


def test_regressao_do_paper_real_melhora_extracao_sem_tocar_no_indice():
    document_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "documents"
        / "pathophysiology_heatstroke_dogs_2017.pdf"
    )
    report = process_document(document_path, tokenizer=FakeTokenizer()).report
    statistics = report.extraction_statistics
    all_text = "\n".join(chunk.text for chunk in report.chunks)
    clinical = next(
        chunk
        for chunk in report.chunks
        if chunk.section == "Clinical signs upon presentation"
    )

    assert statistics is not None
    assert statistics.extractor == "PyMuPDF/layout-aware"
    assert statistics.multi_column_pages >= 9
    assert statistics.headers_removed >= 10
    assert statistics.captions_removed == 6
    assert report.corrupted_openers_removed == 1
    assert clinical.text.split("\n\n", 1)[1].startswith("The median systolic")
    assert "58delirium" not in clinical.text
    assert "Box 12" not in all_text
    assert "Figure 4." not in all_text
    assert "(Fig. 4)" in all_text
    assert "41°C" in all_text
    assert "/C14C" not in all_text
    assert "signi ficantly" not in all_text
    assert "significantly" in all_text
    assert "experimentally induced models" in all_text
    assert "References" in report.excluded_sections
    assert all(chunk.token_count <= 128 for chunk in report.chunks)
