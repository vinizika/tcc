"""Gera as fichas de triagem que o backend lê, a partir do mapa e dos rascunhos.

A arquitetura da autópsia 2 (rodadas 19 e 21 do João) usa duas fichas por
quadro do mapa:

- a **ficha de busca**, escrita por IA a partir dos documentos aprovados
  (``data/curadoria/fichas/<topic>.json``), com as frases do jeito que o tutor
  conta. É o texto que a busca compara com o relato; o atendente não a lê;
- a **ficha de leitura**, montada das colunas validadas do mapa
  (``data/curadoria/mapa-de-assuntos.csv``), com a conduta fixa pela urgência.
  É o texto que o atendente lê.

O backend roda numa imagem que só tem ``backend/``, então este script compila
as duas num JSON versionado, ``backend/data/fichas.json``, junto com as
referências de cada quadro (os documentos aprovados, de
``backend/data/documents/*.json``). ``--check`` permite ao CI detectar quando
um dos arquivos de origem mudou e o gerado ficou desatualizado.

As duas regras de montagem são as da autópsia, sem mudança: o texto que sai
daqui é, byte a byte, o texto que foi medido. Mudar uma frase de ficha é uma
rodada medida, e começa num dos arquivos de origem, nunca aqui.

A conferência de que o trecho de cada item de documento está no documento é
feita na curadoria (``data/curadoria/fichas/conferencia.json``). Aqui só entra
a regra de montagem: item de documento sem trecho fica de fora.
"""

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "curadoria" / "mapa-de-assuntos.csv"
DRAFTS_DIR = ROOT / "data" / "curadoria" / "fichas"
DOCUMENTS_DIR = ROOT / "backend" / "data" / "documents"
OUTPUT_PATH = ROOT / "backend" / "data" / "fichas.json"

APPROVED_STATUSES = {"approved_by_specialist", "approved", "approved_with_reservations"}
SPECIES_CODE = {"ambos": "dog_and_cat", "cao": "dog", "gato": "cat"}

# --------------------------------------------------------------------------
# Ficha de leitura (regra de artefatos_rodada2/exp_setup.py, 23/09)
# --------------------------------------------------------------------------

READING_CONDUCT = {
    "imediato": "Isto e uma emergencia: procure um veterinario agora, sem esperar.",
    "ate_24h": "Nao e emergencia imediata, mas precisa de consulta nas proximas 24 horas; va antes se piorar.",
    "rotina": "Nao e emergencia: pode aguardar uma consulta de rotina, observando se surgem sinais de alarme.",
}
READING_SPECIES = {"ambos": "cao e gato", "cao": "cao", "gato": "gato"}
# Frases do `motivo` que são nota de curadoria, e não motivo clínico.
CURATION_NOTE = re.compile(
    r"\b(na base|base tem|a base|regua|caso b\d|protocolo|sintetic|hovet|usp\b|mapa|etapa|linha|onda|vtl)\b",
    re.I,
)


def clinical_reason(motivo: str) -> str:
    frases = [f.strip() for f in re.split(r";|\.\s", motivo or "") if f.strip()]
    return "; ".join(f for f in frases if not CURATION_NOTE.search(f))


def reading_title(row: dict) -> str:
    return f"Ficha de triagem: {row['quadro']}"


def reading_text(row: dict, rows: dict[str, dict]) -> str:
    par = row["par_de_confusao"].strip()
    partes = [f"Ficha de triagem: {row['quadro']} ({READING_SPECIES.get(row['especie'], row['especie'])})."]
    if row["sinais_que_o_tutor_relata"].strip():
        sinais = (s.strip() for s in row["sinais_que_o_tutor_relata"].split(";"))
        partes.append("Sinais que o tutor costuma relatar: " + ", ".join(s for s in sinais if s) + ".")
    if row["discriminador"].strip():
        partes.append("Como diferenciar: " + row["discriminador"].strip() + ".")
    # Um par só (as linhas com mais de uma gêmea não ganham esta frase: é a regra medida).
    if par and par in rows:
        partes.append("Pode ser confundido com: " + rows[par]["quadro"] + ".")
    # A coluna `por_que_importa` é a frase validada pelos especialistas; enquanto
    # estiver vazia, vale o `motivo` sem as notas de curadoria.
    motivo = (row.get("por_que_importa") or "").strip() or clinical_reason(row["motivo"])
    if motivo:
        partes.append("Por que importa: " + motivo + ".")
    partes.append("Conduta: " + READING_CONDUCT[row["urgencia"]])
    return " ".join(partes)


# --------------------------------------------------------------------------
# Ficha de busca (regra de _trabalho/fichas_claude_montar.py, 24/09)
# --------------------------------------------------------------------------

SEARCH_CONDUCT = {
    "imediato": "Isto é uma emergência: procure um veterinário agora, sem esperar.",
    "ate_24h": "Não é emergência imediata, mas precisa de consulta nas próximas 24 horas; vá antes se piorar.",
    "rotina": "Não é emergência: pode aguardar uma consulta de rotina, observando se surgem sinais de alarme.",
}
SEARCH_SPECIES = {"ambos": "cão e gato", "cao": "cão", "gato": "gato"}
_EMPTY_WORDS = {"nao", "sem", "com", "muito", "mais", "esta", "ele", "ela", "uma", "por", "para", "pra",
                "que", "dos", "das", "nos", "nas"}


def _without_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def _normalized_excerpt(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").casefold()
    text = (text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
            .replace("–", "-").replace("—", "-"))
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"[^\w%<>=\.\,\-\' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip(" .,")


def _stems(text: str) -> set[str]:
    return {w[:4] for w in re.findall(r"\w{3,}", _without_accents(text).casefold()) if w not in _EMPTY_WORDS}


def _covers(map_sign: str, sentence: str) -> bool:
    """O sinal do mapa aparece na frase do autor? (metade ou mais dos radicais)"""
    a = _without_accents(map_sign).casefold().strip(" .;")
    b = _without_accents(sentence).casefold().strip(" .;")
    if a in b:
        return True
    ra, rb = _stems(a), _stems(b)
    return bool(ra) and len(ra & rb) / len(ra) >= 0.5


def _sentence(text: str) -> str:
    return text.strip().rstrip(" .;")


def _accepted(item: dict) -> dict | None:
    texto = _sentence(item.get("texto") or "")
    if not texto:
        return None
    if (item.get("origem") or "").strip() in ("mapa", "geral"):
        return dict(item, texto=texto)
    if len(_normalized_excerpt(item.get("trecho") or "")) < 8:
        return None
    return dict(item, texto=texto)


def draft_items(draft: dict, row: dict) -> dict:
    conta = [x for x in map(_accepted, draft.get("como_o_tutor_conta", [])) if x]
    alarme = [x for x in map(_accepted, draft.get("sinais_de_alarme", [])) if x]
    difer = [x for x in map(_accepted, draft.get("como_diferenciar", [])) if x]
    pq = draft.get("por_que_importa") or {}
    pq = _accepted(pq) if pq.get("texto") else None
    sinais = [s.strip() for s in re.split(r"[;,]", row["sinais_que_o_tutor_relata"] or "") if s.strip()]
    textos = [x["texto"] for x in conta + alarme]
    faltando = [s for s in sinais if not any(_covers(s, t) for t in textos)]
    conta += [{"texto": s[0].upper() + s[1:], "origem": "mapa"} for s in faltando]
    return {"conta": conta, "alarme": alarme, "difer": difer, "pq": pq, "sinais_inseridos": faltando}


def display_title(topic: str, drafts: dict[str, dict], rows: dict[str, dict]) -> str:
    draft = drafts.get(topic) or {}
    return (draft.get("titulo") or rows[topic]["quadro"]).strip()


def search_text(topic: str, drafts: dict[str, dict], rows: dict[str, dict]) -> str:
    row, draft = rows[topic], drafts[topic]
    items = draft_items(draft, row)
    leigo = (draft.get("nome_leigo") or "").strip()
    nome = display_title(topic, drafts, rows)
    if leigo and nome.endswith(")"):  # "Distocia (parto difícil)" + "parto travado"
        titulo = f"Ficha de triagem: {nome[:-1]}, {leigo})"
    else:
        titulo = f"Ficha de triagem: {nome}" + (f" ({leigo})" if leigo else "")
    partes = [f"{titulo} — {SEARCH_SPECIES.get(row['especie'], row['especie'])}."]
    if items["conta"]:
        partes.append("Como o tutor costuma contar: " + "; ".join(x["texto"] for x in items["conta"]) + ".")
    if items["alarme"]:
        partes.append("Sinais de alarme: " + "; ".join(x["texto"] for x in items["alarme"]) + ".")
    for x in items["difer"]:
        gemea = (x.get("gemea") or "").strip()
        nome_gemea = display_title(gemea, drafts, rows) if gemea in rows else gemea
        partes.append(f"Como diferenciar de {nome_gemea.lower() if nome_gemea else 'quadros parecidos'}: {x['texto']}.")
    if items["pq"]:
        partes.append(f"Por que importa: {items['pq']['texto']}.")
    partes.append("Conduta: " + SEARCH_CONDUCT[row["urgencia"]])
    return " ".join(partes)


# --------------------------------------------------------------------------
# Referências e montagem
# --------------------------------------------------------------------------


def _text_bytes(path: Path) -> bytes:
    """Bytes do arquivo com quebras de linha normalizadas (B-71)."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_rows() -> dict[str, dict]:
    with MAP_PATH.open(encoding="utf-8", newline="") as source:
        return {row["id"].strip(): row for row in csv.DictReader(source)}


def load_drafts() -> dict[str, dict]:
    drafts = {}
    for path in sorted(DRAFTS_DIR.glob("*.json")):
        if path.name == "conferencia.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        drafts[data["topico"]] = data
    return drafts


def _document_file(sidecar: Path) -> str:
    for suffix in (".pdf", ".txt", ".md"):
        if sidecar.with_suffix(suffix).exists():
            return sidecar.with_suffix(suffix).name
    return ""


def load_references() -> dict[str, list[dict]]:
    by_topic: dict[str, list[dict]] = {}
    for sidecar in sorted(DOCUMENTS_DIR.glob("*.json")):
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
        if meta.get("validation_status") not in APPROVED_STATUSES:
            continue
        doi = (meta.get("doi") or "").strip()
        by_topic.setdefault(meta.get("topic", ""), []).append({
            "document": _document_file(sidecar),
            "title": (meta.get("full_title") or meta.get("title") or "").strip(),
            "journal": (meta.get("journal") or meta.get("source") or "").strip(),
            "year": meta.get("year"),
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else (meta.get("source_url") or "").strip(),
            "language": meta.get("language", ""),
        })
    return by_topic


def build_payload() -> dict:
    rows = load_rows()
    drafts = load_drafts()
    references = load_references()
    missing = sorted(set(rows) - set(drafts))
    if missing:
        raise SystemExit(f"rascunho de ficha ausente para: {', '.join(missing)}")

    fichas = []
    for topic, row in rows.items():
        busca = search_text(topic, drafts, rows)
        leitura = reading_text(row, rows)
        fichas.append({
            "topic": topic,
            "display_title": display_title(topic, drafts, rows),
            "reading_title": reading_title(row),
            "species": SPECIES_CODE.get(row["especie"], "dog_and_cat"),
            "classe": row["classe"],
            "urgency": row["urgencia"],
            "etapa": row["etapa"],
            "search_text": busca,
            "search_text_sha256": sha256_text(busca),
            "reading_text": leitura,
            "reading_text_sha256": sha256_text(leitura),
            "references": references.get(topic, []),
        })

    drafts_hash = hashlib.sha256()
    for path in sorted(DRAFTS_DIR.glob("*.json")):
        if path.name != "conferencia.json":
            drafts_hash.update(path.name.encode("utf-8") + b"\0" + _text_bytes(path))
    documents_hash = hashlib.sha256()
    for path in sorted(DOCUMENTS_DIR.glob("*.json")):
        documents_hash.update(path.name.encode("utf-8") + b"\0" + _text_bytes(path))

    return {
        "generator": "scripts/sync_fichas.py",
        "sources": {
            "map": "data/curadoria/mapa-de-assuntos.csv",
            "map_sha256": hashlib.sha256(_text_bytes(MAP_PATH)).hexdigest(),
            "drafts": "data/curadoria/fichas/",
            "drafts_sha256": drafts_hash.hexdigest(),
            "documents": "backend/data/documents/*.json",
            "documents_sha256": documents_hash.hexdigest(),
        },
        "count": len(fichas),
        "fichas": fichas,
    }


def render(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    expected = render(build_payload())
    current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""

    if args.check:
        if current.replace("\r\n", "\n") != expected:
            raise SystemExit(
                "backend/data/fichas.json está desatualizado; "
                "execute python scripts/sync_fichas.py"
            )
        print("fichas.json atualizado")
        return

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as output:
        output.write(expected)
    print(f"gerado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
