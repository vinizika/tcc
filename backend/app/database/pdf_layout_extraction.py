"""Extração determinística de PDFs científicos baseada em layout.

O módulo trata cada página de forma independente. Ele usa blocos e
coordenadas fornecidos pelo PyMuPDF para reconstruir a ordem de leitura e
remover apenas ruídos reconhecidos com alta confiança. Não usa OCR, modelos
de linguagem ou regras ligadas a um artigo específico.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import median


_CAPTION_START = re.compile(
    r"^\s*(?:figure|fig\.?|table)\s+\d+[a-z]?\s*[.:\-]",
    re.IGNORECASE,
)
_CONTACT_START = re.compile(
    r"^\s*(?:contact\b|corresponding\s+author\b|orcid\b|"
    r"author\s+correspondence\b)",
    re.IGNORECASE,
)
_EMAIL = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
_AFFILIATION_CUE = re.compile(
    r"\b(?:affiliation|department|faculty|institute|university|"
    r"school\s+of|correspondence|postal|p\.?\s*o\.?\s*box)\b",
    re.IGNORECASE,
)
_EDITORIAL_SECTION_START = re.compile(
    r"^\s*(?:article\s+history|keywords)\s*(?:\n|$)",
    re.IGNORECASE,
)
_TOP_EDITORIAL = re.compile(
    r"(?:https?://doi\.org/|\bvol\.?\s*\d+\b)",
    re.IGNORECASE,
)
_REPRODUCTION_NOTICE = re.compile(
    r"^\s*(?:©|copyright\b|reproduced\s+by\s+permission\b|"
    r"permission\s+to\s+reuse\b)",
    re.IGNORECASE,
)
_ISOLATED_PAGE_NUMBER = re.compile(r"^\s*\d{1,5}\s*$")
_STANDALONE_NUMBER = re.compile(r"(?<!\w)\d{1,5}(?!\w)")


@dataclass(frozen=True)
class LayoutBlock:
    """Bloco textual com geometria normalizada para uma página."""

    page_number: int
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    page_width: float
    page_height: float
    sequence: int = 0
    font_size: float | None = None

    @property
    def width(self) -> float:
        return max(0.0, self.x1 - self.x0)

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2


@dataclass(frozen=True)
class ExtractedPage:
    number: int
    text: str


@dataclass(frozen=True)
class PageOrder:
    blocks: tuple[LayoutBlock, ...]
    column_count: int
    used_coordinate_fallback: bool = False


@dataclass(frozen=True)
class ExtractionStatistics:
    extractor: str
    blocks_extracted: int = 0
    blocks_removed: int = 0
    headers_removed: int = 0
    footers_removed: int = 0
    page_numbers_removed: int = 0
    captions_removed: int = 0
    editorial_blocks_removed: int = 0
    multi_column_pages: int = 0
    coordinate_fallback_pages: int = 0
    degree_symbols_recovered: int = 0
    unmapped_glyphs: int = 0
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class PdfExtractionResult:
    pages: tuple[ExtractedPage, ...]
    statistics: ExtractionStatistics


@dataclass(frozen=True)
class LayoutCleaningResult:
    pages: tuple[tuple[LayoutBlock, ...], ...]
    blocks_removed: int
    headers_removed: int
    footers_removed: int
    page_numbers_removed: int
    captions_removed: int
    editorial_blocks_removed: int


def normalize_pdf_unicode(text: str) -> tuple[str, int, int]:
    """Normaliza Unicode e recupera somente símbolos contextualmente seguros.

    Alguns PDFs sem ``ToUnicode`` entregam um caractere de controle no lugar
    do símbolo de grau. A conversão só é feita quando esse glifo está entre um
    número e a unidade C/F. Outros controles viram U+FFFD para tornar a perda
    explícita, em vez de inventar o caractere original.
    """

    normalized = unicodedata.normalize("NFKC", text)
    output: list[str] = []
    recovered_degrees = 0
    unmapped_glyphs = 0

    for index, character in enumerate(normalized):
        if character in {"\n", "\t"} or unicodedata.category(character) != "Cc":
            output.append(character)
            continue

        previous = normalized[index - 1] if index else ""
        following = normalized[index + 1] if index + 1 < len(normalized) else ""

        if previous.isdigit() and following.upper() in {"C", "F"}:
            output.append("°")
            recovered_degrees += 1
        else:
            output.append("\N{REPLACEMENT CHARACTER}")
            unmapped_glyphs += 1

    return "".join(output), recovered_degrees, unmapped_glyphs


def is_caption_block(text: str) -> bool:
    """Reconhece somente legendas com marcador e numeração no início."""

    return bool(_CAPTION_START.match(" ".join(text.split())))


def is_editorial_block(block: LayoutBlock) -> bool:
    """Reconhece contato, autoria e avisos editoriais com alta confiança."""

    raw_text = block.text.strip()
    text = " ".join(raw_text.split())

    if (
        _CONTACT_START.match(text)
        or _EDITORIAL_SECTION_START.match(raw_text)
        or _REPRODUCTION_NOTICE.match(text)
    ):
        return True

    top_margin = block.y0 <= block.page_height * 0.13
    bottom_margin = block.y1 >= block.page_height * 0.87

    if top_margin and _TOP_EDITORIAL.search(text):
        return True

    return bool(
        (top_margin or bottom_margin)
        and _EMAIL.search(text)
        and _AFFILIATION_CUE.search(text)
    )


def _margin_region(block: LayoutBlock) -> str | None:
    if block.y0 <= block.page_height * 0.12:
        return "header"
    if block.y1 >= block.page_height * 0.88:
        return "footer"
    return None


def _margin_signature(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", " ".join(text.split())).casefold()
    return _STANDALONE_NUMBER.sub("#", normalized)


def _repeated_margin_signatures(
    pages: list[list[LayoutBlock]],
) -> tuple[set[str], set[str]]:
    """Obtém assinaturas recorrentes, contando no máximo uma vez por página."""

    page_count = len(pages)
    if page_count < 3:
        return set(), set()

    required_occurrences = max(3, math.ceil(page_count * 0.20))
    header_counts: Counter[str] = Counter()
    footer_counts: Counter[str] = Counter()

    for blocks in pages:
        header_keys: set[str] = set()
        footer_keys: set[str] = set()

        for block in blocks:
            region = _margin_region(block)
            signature = _margin_signature(block.text)

            if not signature or len(signature) > 220:
                continue
            if region == "header":
                header_keys.add(signature)
            elif region == "footer":
                footer_keys.add(signature)

        header_counts.update(header_keys)
        footer_counts.update(footer_keys)

    headers = {
        signature
        for signature, count in header_counts.items()
        if count >= required_occurrences
    }
    footers = {
        signature
        for signature, count in footer_counts.items()
        if count >= required_occurrences
    }
    return headers, footers


def clean_layout_blocks(
    pages: list[list[LayoutBlock]],
) -> LayoutCleaningResult:
    """Remove ruído estrutural antes de reconstruir a ordem de leitura."""

    repeated_headers, repeated_footers = _repeated_margin_signatures(pages)
    cleaned_pages: list[tuple[LayoutBlock, ...]] = []
    headers_removed = 0
    footers_removed = 0
    page_numbers_removed = 0
    captions_removed = 0
    editorial_blocks_removed = 0

    for blocks in pages:
        kept: list[LayoutBlock] = []

        for block in blocks:
            region = _margin_region(block)
            signature = _margin_signature(block.text)
            compact_text = " ".join(block.text.split())

            if region == "header" and signature in repeated_headers:
                headers_removed += 1
            elif region == "footer" and signature in repeated_footers:
                footers_removed += 1
            elif region and _ISOLATED_PAGE_NUMBER.fullmatch(compact_text):
                page_numbers_removed += 1
            elif is_caption_block(compact_text):
                captions_removed += 1
            elif is_editorial_block(block):
                if region == "header" and _TOP_EDITORIAL.search(compact_text):
                    headers_removed += 1
                else:
                    editorial_blocks_removed += 1
            else:
                kept.append(block)

        cleaned_pages.append(tuple(kept))

    blocks_removed = (
        headers_removed
        + footers_removed
        + page_numbers_removed
        + captions_removed
        + editorial_blocks_removed
    )
    return LayoutCleaningResult(
        pages=tuple(cleaned_pages),
        blocks_removed=blocks_removed,
        headers_removed=headers_removed,
        footers_removed=footers_removed,
        page_numbers_removed=page_numbers_removed,
        captions_removed=captions_removed,
        editorial_blocks_removed=editorial_blocks_removed,
    )


def _has_valid_geometry(blocks: list[LayoutBlock]) -> bool:
    if not blocks:
        return True

    for block in blocks:
        coordinates = (
            block.x0,
            block.y0,
            block.x1,
            block.y1,
            block.page_width,
            block.page_height,
        )
        if not all(math.isfinite(value) for value in coordinates):
            return False
        if block.page_width <= 0 or block.page_height <= 0:
            return False
        if block.x1 < block.x0 or block.y1 < block.y0:
            return False

    return True


def _is_spanning(block: LayoutBlock, page_width: float) -> bool:
    return block.x0 < page_width * 0.46 and block.x1 > page_width * 0.54


def _column_groups(
    blocks: list[LayoutBlock],
    page_width: float,
) -> tuple[list[LayoutBlock], list[LayoutBlock]]:
    left: list[LayoutBlock] = []
    right: list[LayoutBlock] = []

    for block in blocks:
        if _is_spanning(block, page_width):
            continue

        if block.center_x < page_width * 0.47 and block.x1 <= page_width * 0.56:
            left.append(block)
        elif (
            block.center_x > page_width * 0.53
            and block.x0 >= page_width * 0.44
        ):
            right.append(block)

    return left, right


def detect_column_count(blocks: list[LayoutBlock]) -> int:
    """Detecta duas regiões horizontais dominantes sem perfil por documento."""

    if len(blocks) < 2 or not _has_valid_geometry(blocks):
        return 1

    page_width = median(block.page_width for block in blocks)
    left, right = _column_groups(blocks, page_width)

    if not left or not right:
        return 1

    left_text = sum(len(block.text.strip()) for block in left)
    right_text = sum(len(block.text.strip()) for block in right)
    left_center = median(block.center_x for block in left)
    right_center = median(block.center_x for block in right)

    if left_text < 20 or right_text < 20:
        return 1
    if left_center > page_width * 0.43:
        return 1
    if right_center < page_width * 0.57:
        return 1
    if right_center - left_center < page_width * 0.24:
        return 1

    return 2


def _order_column_band(
    blocks: list[LayoutBlock],
    page_width: float,
) -> list[LayoutBlock]:
    left = [block for block in blocks if block.center_x < page_width / 2]
    right = [block for block in blocks if block.center_x >= page_width / 2]
    position_key = lambda block: (block.y0, block.x0, block.sequence)
    return [*sorted(left, key=position_key), *sorted(right, key=position_key)]


def order_blocks_for_reading(blocks: list[LayoutBlock]) -> PageOrder:
    """Ordena uma página sem alternar linhas entre colunas.

    Blocos que cruzam a faixa central funcionam como separadores entre bandas.
    Assim, um título em largura total aparece antes das duas colunas e uma
    página pode voltar a uma coluna abaixo de uma figura ou heading.
    """

    if not blocks:
        return PageOrder((), 1)

    if not _has_valid_geometry(blocks):
        return PageOrder(
            tuple(sorted(blocks, key=lambda block: block.sequence)),
            1,
            used_coordinate_fallback=True,
        )

    position_key = lambda block: (block.y0, block.x0, block.sequence)
    column_count = detect_column_count(blocks)

    if column_count == 1:
        return PageOrder(tuple(sorted(blocks, key=position_key)), 1)

    page_width = median(block.page_width for block in blocks)
    spanning = sorted(
        (block for block in blocks if _is_spanning(block, page_width)),
        key=position_key,
    )
    remaining = [block for block in blocks if block not in spanning]
    ordered: list[LayoutBlock] = []

    for separator in spanning:
        before = [
            block
            for block in remaining
            if block.y1 <= separator.y0 + 1.0
        ]
        ordered.extend(_order_column_band(before, page_width))
        before_ids = {id(block) for block in before}
        remaining = [block for block in remaining if id(block) not in before_ids]
        ordered.append(separator)

    ordered.extend(_order_column_band(remaining, page_width))
    return PageOrder(tuple(ordered), 2)


def _block_font_size(block: dict) -> float | None:
    weighted_sizes: list[float] = []

    for line in block.get("lines", []):
        for span in line.get("spans", []):
            span_text = span.get("text", "").strip()
            size = span.get("size")
            if span_text and isinstance(size, (int, float)):
                weighted_sizes.extend([float(size)] * min(len(span_text), 40))

    return median(weighted_sizes) if weighted_sizes else None


def _block_text(block: dict) -> str:
    fragments: list[tuple[tuple[float, float, float, float], str]] = []

    for line in block.get("lines", []):
        text = "".join(span.get("text", "") for span in line.get("spans", []))
        if text.strip():
            bbox = tuple(float(value) for value in line["bbox"])
            fragments.append((bbox, text.rstrip()))

    # Alguns PDFs justificados codificam palavras da mesma linha como linhas
    # separadas, com caixas verticalmente sobrepostas. Reagrupá-las pela
    # geometria corrige espaços sem dicionário e sem inferência semântica.
    visual_lines: list[list[tuple[tuple[float, float, float, float], str]]] = []

    for fragment in sorted(
        fragments,
        key=lambda item: (((item[0][1] + item[0][3]) / 2), item[0][0]),
    ):
        bbox, _ = fragment
        center_y = (bbox[1] + bbox[3]) / 2
        matching_line = None

        for visual_line in reversed(visual_lines[-2:]):
            reference_bbox = visual_line[0][0]
            reference_center = (reference_bbox[1] + reference_bbox[3]) / 2
            shortest_height = min(
                bbox[3] - bbox[1],
                reference_bbox[3] - reference_bbox[1],
            )

            same_visual_line = abs(center_y - reference_center) <= max(
                2.0,
                shortest_height * 0.35,
            )
            if same_visual_line:
                matching_line = visual_line
                break

        if matching_line is None:
            visual_lines.append([fragment])
        else:
            matching_line.append(fragment)

    lines: list[str] = []

    for visual_line in visual_lines:
        ordered_fragments = sorted(visual_line, key=lambda item: item[0][0])
        lines.append(" ".join(text.strip() for _, text in ordered_fragments))

    return "\n".join(lines).strip()


def extract_pdf_with_layout(document_path: Path) -> PdfExtractionResult:
    """Extrai um PDF com PyMuPDF; exceções são tratadas pelo chamador."""

    import pymupdf

    document = pymupdf.open(document_path)

    try:
        if document.needs_pass and not document.authenticate(""):
            raise ValueError(
                f"O PDF {document_path.name} está protegido por senha."
            )

        pages: list[list[LayoutBlock]] = []
        recovered_degrees = 0
        unmapped_glyphs = 0

        for page_number, page in enumerate(document, start=1):
            page_blocks: list[LayoutBlock] = []
            # Imagens não são usadas (não há OCR nesta etapa). Excluí-las dos
            # flags evita decodificar bitmaps grandes só para descartá-los.
            text_flags = (
                pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES
            )
            raw_page = page.get_text("dict", sort=False, flags=text_flags)

            for sequence, raw_block in enumerate(raw_page.get("blocks", [])):
                if raw_block.get("type") != 0:
                    continue

                raw_text = _block_text(raw_block)
                text, recovered, unmapped = normalize_pdf_unicode(raw_text)
                recovered_degrees += recovered
                unmapped_glyphs += unmapped

                if not text.strip():
                    continue

                x0, y0, x1, y1 = raw_block["bbox"]
                page_blocks.append(
                    LayoutBlock(
                        page_number=page_number,
                        text=text,
                        x0=float(x0),
                        y0=float(y0),
                        x1=float(x1),
                        y1=float(y1),
                        page_width=float(page.rect.width),
                        page_height=float(page.rect.height),
                        sequence=sequence,
                        font_size=_block_font_size(raw_block),
                    )
                )

            pages.append(page_blocks)
    finally:
        document.close()

    blocks_extracted = sum(len(page) for page in pages)
    cleaned = clean_layout_blocks(pages)
    extracted_pages: list[ExtractedPage] = []
    multi_column_pages = 0
    coordinate_fallback_pages = 0
    empty_pages = 0

    for page_number, blocks in enumerate(cleaned.pages, start=1):
        ordered = order_blocks_for_reading(list(blocks))
        multi_column_pages += int(ordered.column_count == 2)
        coordinate_fallback_pages += int(ordered.used_coordinate_fallback)
        page_text = "\n".join(block.text for block in ordered.blocks).strip()

        if page_text:
            extracted_pages.append(ExtractedPage(page_number, page_text))
        else:
            empty_pages += 1

    warnings: list[str] = []
    if coordinate_fallback_pages:
        warnings.append(
            f"{coordinate_fallback_pages} página(s) sem geometria confiável"
        )
    if empty_pages:
        warnings.append(
            f"{empty_pages} página(s) sem texto após a extração/limpeza"
        )
    if unmapped_glyphs:
        warnings.append(
            f"{unmapped_glyphs} glifo(s) sem mapeamento Unicode inequívoco"
        )

    statistics = ExtractionStatistics(
        extractor="PyMuPDF/layout-aware",
        blocks_extracted=blocks_extracted,
        blocks_removed=cleaned.blocks_removed,
        headers_removed=cleaned.headers_removed,
        footers_removed=cleaned.footers_removed,
        page_numbers_removed=cleaned.page_numbers_removed,
        captions_removed=cleaned.captions_removed,
        editorial_blocks_removed=cleaned.editorial_blocks_removed,
        multi_column_pages=multi_column_pages,
        coordinate_fallback_pages=coordinate_fallback_pages,
        degree_symbols_recovered=recovered_degrees,
        unmapped_glyphs=unmapped_glyphs,
        warnings=tuple(warnings),
    )
    return PdfExtractionResult(tuple(extracted_pages), statistics)
