"""
Captura uma fonte da web para virar documento da base.

O agente pesquisador **lê** páginas para julgar se servem; este script
**captura** a que foi escolhida. A diferença importa: o que um modelo lê é o
que ele entendeu da página, e indexar isso faria a base ser paráfrase — o
oposto da decisão de usar fontes originais. Aqui o texto sai da página, não
de um resumo, e fica gravado com hash e data.

    python scripts/capturar_fonte.py https://exemplo.org/gdv \\
        --topic gastric_dilatation_volvulus --slug pdsa \\
        --include "GDV Symptoms" --include "When to contact your vet" \\
        --language en --register tutor --source PDSA

Grava em `data/curadoria/fontes/capturas/` dois arquivos irmãos:

- `<topic>__<slug>.txt` (ou `.pdf`), que é o que o especialista aprova e o
  que a ingestão indexa depois;
- `<topic>__<slug>.json`, a ficha rascunho, no formato que
  `backend/data/documents/` espera.

O que ele **não** faz: não indexa, não aprova, não traduz e não reescreve. A
cópia para a pasta da base é do agente de ingestão, depois do aval do
especialista.
"""

import argparse
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[1]
MAPA = RAIZ / "data" / "curadoria" / "mapa-de-assuntos.csv"
DESTINO_PADRAO = RAIZ / "data" / "curadoria" / "fontes" / "capturas"

# Identifica o projeto para quem hospeda a página. Um capturador anônimo é
# indistinguível de um raspador, e vários sites recusam por isso.
AGENTE = (
    "TCC-FEI-pre-triagem-veterinaria/1.0 "
    "(pesquisa academica; contato pelo repositorio)"
)
TEMPO_LIMITE = (10, 60)

# Vocabulários da ficha. São os mesmos que o mapa e o `compare` usam; ficam
# aqui para a captura recusar um valor inventado antes de escrever o arquivo.
REGISTROS = {"tutor", "clinico", "academico"}
TIPOS = {
    "owner_guidance",
    "professional_manual",
    "guideline",
    "technical_bulletin",
    "peer_reviewed_article",
    "case_report",
    "team_summary",
    "synthetic_protocol",
}
ESPECIES = {"dog", "cat", "dogs_and_cats"}

# O título entra no começo de todo trecho do documento, e um trecho tem ~40
# palavras: título comprido é conteúdo clínico que não cabe.
MAX_PALAVRAS_TITULO = 6

# Abaixo do piso não é fonte, é página de erro, muro de login ou conteúdo que
# só existe depois do JavaScript rodar. Entre o piso e o aviso pode ser uma
# lista curta de "quando levar ao veterinário", que é legítima e valiosa — por
# isso avisa em vez de recusar.
MIN_PALAVRAS = 50
POUCAS_PALAVRAS = 150

_MARCA_DE_TITULO = re.compile(r"^#{1,6}\s*")
# Negrito e itálico do markdown viram lixo dentro do trecho indexado, e um
# trecho tem ~40 palavras. O modelo não ganha nada lendo asteriscos.
_ENFASE = re.compile(r"\*{1,3}|_{2,3}")
_LINHAS_VAZIAS = re.compile(r"\n{3,}")


class Baixador:
    """
    O acesso à rede, atrás de uma classe — é o padrão do `ApiClient` do
    runner, e é o que deixa os testes rodarem sem internet.
    """

    def buscar(self, url: str) -> tuple[bytes, str]:
        resposta = requests.get(
            url, headers={"User-Agent": AGENTE}, timeout=TEMPO_LIMITE
        )
        resposta.raise_for_status()

        return resposta.content, resposta.headers.get("Content-Type", "")


def _curto(caminho: Path) -> str:
    """Caminho relativo à raiz quando der; absoluto quando o destino for outro."""

    try:
        return str(caminho.relative_to(RAIZ))
    except ValueError:
        return str(caminho)


def topicos_do_mapa() -> set[str]:
    if not MAPA.exists():
        raise SystemExit(f"Mapa de assuntos não encontrado: {MAPA}")

    with open(MAPA, encoding="utf-8", newline="") as arquivo:
        return {linha["id"] for linha in csv.DictReader(arquivo)}


def decodificar(conteudo: bytes, tipo: str) -> str:
    """
    Converte os bytes da página em texto, respeitando a codificação dela.

    Não é detalhe: material veterinário de universidade e de conselho
    regional brasileiro costuma estar em Latin-1, e decodificar isso como
    UTF-8 transforma "Sinais clínicos" em "Sinais cl�nicos" **sem erro
    nenhum**. Um documento assim seria indexado e recuperado como lixo.
    """

    declarada = ""
    if "charset=" in tipo.lower():
        declarada = tipo.lower().split("charset=")[1].split(";")[0].strip(" \"'")

    candidatas = [declarada, "utf-8", "cp1252", "latin-1"]

    # A página também declara a codificação dentro do HTML, e é comum o
    # servidor mentir e o <meta> estar certo.
    cabecalho = conteudo[:2048].decode("ascii", errors="ignore").lower()
    achado = re.search(r'charset=["\']?([\w-]+)', cabecalho)
    if achado:
        candidatas.insert(1, achado.group(1))

    for codificacao in candidatas:
        if not codificacao:
            continue
        try:
            texto = conteudo.decode(codificacao)
        except (UnicodeDecodeError, LookupError):
            continue
        # `latin-1` decodifica qualquer byte, então ela nunca falha — é a
        # última da fila justamente por isso, e ainda assim conferimos se o
        # resultado tem cara de texto e não de bytes mal interpretados.
        if "�" not in texto:
            return texto

    return conteudo.decode("utf-8", errors="replace")


def _chave_de_secao(titulo: str) -> str:
    """
    A mesma normalização que o ingestor aplica antes de comparar nomes de
    seção (`document_processing._section_key`): tudo que não é letra ou
    dígito cai fora. **Acento não é normalizado** — "Diagnóstico" e
    "Diagnostico" continuam sendo chaves diferentes, lá e aqui.
    """

    return re.sub(r"[^a-z0-9]+", "", titulo.lower())


def idioma_provavel(texto: str) -> str:
    """
    Chuta o idioma do **corpo** por palavras funcionais, para pegar um caso
    que o piloto encontrou: sites traduzem o menu e os títulos e deixam o
    texto em inglês. Uma ficha que diz `language: pt` sobre um corpo em
    inglês faz o experimento de idioma × registro medir a coisa errada.

    É heurística, e serve para avisar — nunca para decidir sozinha.
    """

    palavras = re.findall(r"[a-záàâãéêíóôõúç]+", texto.lower())
    if len(palavras) < 40:
        return ""

    amostra = set(palavras)
    pt = sum(p in amostra for p in (
        "não", "para", "com", "uma", "que", "são", "pode", "quando", "cão",
        "está", "sinais", "veterinário", "também", "mais", "sobre",
    ))
    en = sum(p in amostra for p in (
        "the", "and", "your", "with", "they", "will", "when", "dog",
        "should", "signs", "veterinary", "also", "more", "about", "have",
    ))

    if pt >= en + 3:
        return "pt"
    if en >= pt + 3:
        return "en"
    return ""


def texto_principal(html: str) -> tuple[str, str]:
    """
    Extrai o corpo da página e o título, devolvendo texto limpo.

    Menu, rodapé, banner de cookie e "leia também" não entram: eles não são
    conteúdo clínico e, num chunk de ~40 palavras, deslocariam conteúdo que é.
    Os títulos de seção viram **linhas próprias sem marcação** — é assim que o
    ingestor os reconhece quando a ficha os declara em `include_sections`.
    """

    import trafilatura

    extraido = trafilatura.extract(
        html,
        output_format="markdown",
        include_comments=False,
        include_tables=True,
        include_images=False,
        include_links=False,
        favor_precision=True,
    )

    if not extraido:
        raise SystemExit(
            "Não foi possível extrair o texto principal desta página. "
            "Salve o conteúdo à mão, se a fonte valer a pena."
        )

    # `strip()` e não `rstrip()`: o markdown do trafilatura indenta o que
    # estava aninhado na página, e num trecho de ~40 palavras a tabulação não
    # ensina nada. Pior: um heading indentado não bate, caractere por
    # caractere, com o nome declarado na ficha — e foi assim que a captura da
    # Cornell quase perdeu duas seções.
    linhas = [
        _ENFASE.sub("", _MARCA_DE_TITULO.sub("", linha)).strip()
        for linha in extraido.splitlines()
    ]
    texto = _LINHAS_VAZIAS.sub("\n\n", "\n".join(linhas)).strip()

    metadados = trafilatura.extract_metadata(html)
    titulo = (getattr(metadados, "title", "") or "").strip()

    return texto + "\n", titulo


def montar_ficha(argumentos, url: str, sha256: str, titulo_sugerido: str) -> dict:
    """
    A ficha no formato que `backend/data/documents/` espera, com os campos de
    procedência que o pesquisador conhece e um `validation_status` que diz, em
    voz alta, que ninguém validou ainda.
    """

    ficha = {
        "title": argumentos.title or titulo_sugerido or argumentos.slug,
        "source": argumentos.source or "",
        "document_type": argumentos.document_type or "",
        "validation_status": "pending_specialist",
        "species": argumentos.species or "",
        "topic": argumentos.topic,
        "language": argumentos.language or "",
        "source_url": url,
        "indexing": {
            "include_sections": list(argumentos.include or []),
            "exclude_sections": list(argumentos.exclude or []),
            "exclude_pages": [],
        },
        # Os quatro abaixo não chegam ao ChromaDB — o ingestor só copia uma
        # lista fechada de campos. Vivem aqui, versionados, porque é a ficha
        # que o especialista lê e é ela que sustenta a procedência.
        "register": argumentos.register or "",
        "access_date": date.today().isoformat(),
        "captured_sha256": sha256,
        "map_line": argumentos.topic,
        "specialist": {"verdict": "", "name": "", "date": ""},
    }

    if argumentos.year:
        ficha["year"] = argumentos.year
    if argumentos.authors:
        ficha["authors"] = argumentos.authors

    return ficha


def main(argv=None, baixador: Baixador | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Captura uma fonte da web para a curadoria da base."
    )
    parser.add_argument("url")
    parser.add_argument(
        "--topic",
        required=True,
        help="O assunto, que precisa ser um id do mapa de assuntos.",
    )
    parser.add_argument(
        "--slug",
        required=True,
        help="Apelido curto da fonte (pdsa, msd, scielo_2012).",
    )
    parser.add_argument("--title", help="Título da ficha. Curto: cada token "
                                        "dele é cobrado em todos os trechos.")
    parser.add_argument("--source", help="Instituição ou periódico.")
    parser.add_argument("--document-type", choices=sorted(TIPOS))
    parser.add_argument("--species", choices=sorted(ESPECIES))
    parser.add_argument("--language", help="pt, pt-PT, en…")
    parser.add_argument("--register", choices=sorted(REGISTROS))
    parser.add_argument("--year", type=int)
    parser.add_argument("--authors")
    parser.add_argument(
        "--include",
        action="append",
        help="Seção que entra na indexação. Repita para várias. O texto "
             "precisa bater com o do documento, acento por acento.",
    )
    parser.add_argument("--exclude", action="append")
    parser.add_argument("--destino", type=Path, default=DESTINO_PADRAO)
    parser.add_argument(
        "--forcar",
        action="store_true",
        help="Sobrescreve uma captura existente. Sem isto, o script recusa: "
             "o especialista aprova um arquivo com hash, e trocá-lo por "
             "baixo invalidaria a aprovação em silêncio.",
    )

    argumentos = parser.parse_args(argv)

    if argumentos.topic not in topicos_do_mapa():
        raise SystemExit(
            f"'{argumentos.topic}' não é uma linha do mapa de assuntos. "
            "Assunto novo ganha linha no mapa antes de ganhar documento."
        )

    if not re.fullmatch(r"[a-z0-9_]+", argumentos.slug):
        raise SystemExit("--slug aceita só letras minúsculas, dígitos e _.")

    if argumentos.title and len(argumentos.title.split()) > MAX_PALAVRAS_TITULO:
        raise SystemExit(
            f"--title tem {len(argumentos.title.split())} palavras. O título "
            f"entra no começo de **todos** os trechos deste documento, e cada "
            f"trecho tem ~40 palavras: use no máximo {MAX_PALAVRAS_TITULO}."
        )

    argumentos.destino.mkdir(parents=True, exist_ok=True)
    base = argumentos.destino / f"{argumentos.topic}__{argumentos.slug}"

    existentes = [
        base.with_suffix(sufixo)
        for sufixo in (".txt", ".pdf", ".json")
        if base.with_suffix(sufixo).exists()
    ]
    if existentes and not argumentos.forcar:
        raise SystemExit(
            f"Já existe captura com este nome: {_curto(existentes[0])}. "
            "Use outro --slug, ou --forcar se a intenção é substituir. "
            "Trocar o arquivo por baixo invalida a aprovação do especialista, "
            "que é dada sobre um hash."
        )

    conteudo, tipo = (baixador or Baixador()).buscar(argumentos.url)

    ehpdf = conteudo[:5] == b"%PDF-"

    if ehpdf:
        corpo, extensao, titulo, texto = conteudo, ".pdf", "", ""
    elif "pdf" in tipo.lower():
        raise SystemExit(
            "O servidor anunciou PDF, mas o conteúdo não começa com %PDF-. "
            "Provavelmente é uma página de erro ou de login. Abra a URL no "
            "navegador e confira."
        )
    elif "html" in tipo.lower() or not tipo:
        texto, titulo = texto_principal(decodificar(conteudo, tipo))
        corpo, extensao = texto.encode("utf-8"), ".txt"
    else:
        raise SystemExit(
            f"Tipo de conteúdo não suportado: {tipo}. A base aceita só PDF "
            "e texto."
        )

    palavras = len(texto.split()) if texto else 0

    if extensao == ".txt" and palavras < MIN_PALAVRAS:
        raise SystemExit(
            f"Só {palavras} palavras foram extraídas — página de erro, muro "
            "de login ou conteúdo carregado por JavaScript. Abra a URL no "
            "navegador antes de insistir."
        )

    avisos = []

    if extensao == ".txt" and palavras < POUCAS_PALAVRAS:
        avisos.append(
            f"só {palavras} palavras. Pode ser uma lista curta legítima, mas "
            "também é o que uma página carregada por JavaScript devolve — "
            "abra a URL no navegador e compare."
        )

    if extensao == ".txt" and argumentos.include:
        # Compara pela mesma chave que o ingestor usa (`_section_key`), e não
        # pela linha literal: ele ignora pontuação e espaço, mas **não**
        # normaliza acento. Uma trava mais rígida que o ingestor recusaria
        # seção que funcionaria.
        linhas = {_chave_de_secao(linha) for linha in texto.splitlines()}
        ausentes = [
            secao for secao in argumentos.include
            if _chave_de_secao(secao) not in linhas
        ]
        if ausentes:
            raise SystemExit(
                "Estas seções não existem no texto capturado, linha por "
                f"linha: {ausentes}. O ingestor as ignoraria **em silêncio**, "
                "e a curadoria sairia diferente do que você pensa. Abra o "
                "arquivo, veja os títulos que existem de verdade e declare "
                "esses — acento por acento."
            )

    if extensao == ".txt" and argumentos.language:
        detectado = idioma_provavel(texto)
        declarado = argumentos.language.split("-")[0].lower()
        if detectado and detectado != declarado:
            avisos.append(
                f"a ficha diz language={argumentos.language}, mas o corpo "
                f"parece estar em '{detectado}'. Sites traduzem o menu e os "
                "títulos e deixam o texto no idioma original — confira antes "
                "de seguir."
            )

    caminho = base.with_suffix(extensao)

    # Bytes, e não `write_text`: escrever assim evita que o Windows troque
    # \n por \r\n e mude o sha256 entre máquinas.
    caminho.write_bytes(corpo)

    sha256 = hashlib.sha256(corpo).hexdigest()
    ficha = montar_ficha(argumentos, argumentos.url, sha256, titulo)
    base.with_suffix(".json").write_text(
        json.dumps(ficha, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Capturado: {_curto(caminho)}")
    print(f"  sha256   : {sha256[:16]}…")
    print(f"  palavras : {palavras}" if extensao == ".txt" else "  (PDF)")
    print(f"  ficha    : {_curto(base.with_suffix('.json'))}")

    for aviso in avisos:
        print(f"\n  ATENÇÃO: {aviso}")
    print(
        "\nPróximo passo: inspecionar sem tocar no banco.\n"
        "  docker compose exec backend python -m app.database.ingest_documents "
        f"--inspect --file {caminho.name}\n"
        "(o arquivo precisa estar em backend/data/documents/ para isso; "
        "a cópia é do agente de ingestão, depois do aval do especialista)"
    )


if __name__ == "__main__":
    main()
