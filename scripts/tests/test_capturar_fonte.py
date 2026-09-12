"""
Testes da captura de fontes.

A captura é o que separa "a base tem fontes originais" de "a base tem
paráfrase": o arquivo gravado aqui é o que o especialista aprova e o que a
ingestão indexa. Estes testes existem para que isso continue verdadeiro —
sem rede, com HTML de mentira.
"""

import json

import pytest

from capturar_fonte import main


class BaixadorFalso:
    """Substitui a rede. Devolve o que o teste mandar."""

    def __init__(self, conteudo: bytes, tipo: str = "text/html; charset=utf-8"):
        self.conteudo = conteudo
        self.tipo = tipo
        self.urls = []

    def buscar(self, url):
        self.urls.append(url)
        return self.conteudo, self.tipo


PAGINA = """
<html><head><title>GDV em cães — Exemplo</title></head><body>
<nav><a href="/">Início</a><a href="/caes">Cães</a><a href="/gatos">Gatos</a></nav>
<div class="cookie">Este site usa cookies. Aceitar todos.</div>
<article>
<h1>Torção gástrica em cães</h1>
<h2>Sinais clínicos</h2>
<p>O cão tenta vomitar e não sai nada, a barriga fica inchada e dura, ele
saliva muito e fica inquieto, andando de um lado para o outro sem descanso.</p>
<ul><li>Barriga inchada e dura</li><li>Tentativa de vômito sem resultado</li></ul>
<h2>Quando levar ao veterinário</h2>
<p><strong>Procure atendimento imediatamente.</strong> Cada hora conta, e o
quadro leva o cão ao choque em poucas horas.</p>
<h2>Tratamento</h2>
<p>Descompressão gástrica e correção cirúrgica com gastropexia.</p>
</article>
<footer>Copyright 2026 Exemplo. Todos os direitos reservados. Fale conosco.</footer>
</body></html>
"""

BASE = ["https://exemplo.org/gdv", "--topic", "gastric_dilatation_volvulus"]


def capturar(tmp_path, *extras, pagina=PAGINA, tipo="text/html"):
    baixador = BaixadorFalso(pagina.encode("utf-8"), tipo)
    main(
        [*BASE, "--slug", "exemplo", "--destino", str(tmp_path), *extras],
        baixador=baixador,
    )
    return tmp_path / "gastric_dilatation_volvulus__exemplo"


# ----------------------------------------------------------------------
# O que é gravado
# ----------------------------------------------------------------------


def test_menu_cookie_e_rodape_ficam_de_fora(tmp_path):
    """
    Um trecho tem ~40 palavras. "Aceitar todos os cookies" ocupando um deles
    é uma resposta que o classificador pode receber no lugar de conteúdo
    clínico — e foi assim que a rodada 10 mediu o custo do ruído.
    """

    texto = capturar(tmp_path).with_suffix(".txt").read_text(encoding="utf-8")

    for lixo in ("cookies", "Copyright", "Fale conosco", "Início"):
        assert lixo not in texto, lixo


def test_conteudo_clinico_e_preservado_literal(tmp_path):
    """
    A captura não resume nem traduz: se o texto gravado não for o da página,
    a base deixa de ser feita de fontes originais.
    """

    texto = capturar(tmp_path).with_suffix(".txt").read_text(encoding="utf-8")

    assert "tenta vomitar e não sai nada" in texto
    assert "Procure atendimento imediatamente" in texto


def test_titulos_de_secao_viram_linhas_sem_marcacao(tmp_path):
    """
    É assim que o ingestor os reconhece quando a ficha os declara em
    `include_sections`. Com `## ` na frente, o nome da seção viraria
    "## Sinais Clínicos" no caminho do fallback.
    """

    linhas = capturar(tmp_path).with_suffix(".txt").read_text(
        encoding="utf-8"
    ).splitlines()

    assert "Sinais clínicos" in linhas
    assert "Quando levar ao veterinário" in linhas
    assert not any(linha.startswith("#") for linha in linhas)


def test_marcacao_de_negrito_nao_entra_no_trecho(tmp_path):
    """
    Um trecho tem ~40 palavras. Asterisco de markdown ocupa espaço e não
    ensina nada ao modelo — e a página do piloto trazia quatro seguidos.
    """

    texto = capturar(tmp_path).with_suffix(".txt").read_text(encoding="utf-8")

    assert "*" not in texto


def test_arquivo_sai_em_utf8_sem_bom_e_sem_cr(tmp_path):
    """
    O ingestor lê com `encoding="utf-8"` fixo e sem `utf-8-sig`: um BOM
    quebraria o primeiro heading. E `\\r` mudaria o sha256 entre máquinas.
    """

    bruto = capturar(tmp_path).with_suffix(".txt").read_bytes()

    assert not bruto.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in bruto
    bruto.decode("utf-8")


# ----------------------------------------------------------------------
# A ficha
# ----------------------------------------------------------------------


def test_ficha_registra_procedencia_e_que_ninguem_validou(tmp_path):
    """
    `pending_specialist` é o que impede uma fonte recém-baixada de parecer
    aprovada. A data e o hash são o que tornam a aprovação verificável: o
    especialista aprova um arquivo, não uma URL que pode mudar amanhã.
    """

    ficha = json.loads(
        capturar(tmp_path).with_suffix(".json").read_text(encoding="utf-8")
    )

    assert ficha["topic"] == "gastric_dilatation_volvulus"
    assert ficha["source_url"] == "https://exemplo.org/gdv"
    assert ficha["validation_status"] == "pending_specialist"
    assert len(ficha["captured_sha256"]) == 64
    assert ficha["access_date"]
    assert ficha["specialist"] == {"verdict": "", "name": "", "date": ""}


def test_hash_da_ficha_e_o_hash_do_arquivo_gravado(tmp_path):
    """
    Se divergirem, a aprovação do especialista deixa de valer como prova de
    que ele viu este texto.
    """

    import hashlib

    base = capturar(tmp_path)
    ficha = json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))

    assert ficha["captured_sha256"] == hashlib.sha256(
        base.with_suffix(".txt").read_bytes()
    ).hexdigest()


def test_secoes_escolhidas_vao_para_a_ficha(tmp_path):
    """
    Curadoria por seção: o manual inteiro não entra, só as partes que
    respondem a uma triagem. "Tratamento" fica de fora de propósito — o
    sistema não prescreve.
    """

    base = capturar(
        tmp_path,
        "--include", "Sinais clínicos",
        "--include", "Quando levar ao veterinário",
    )
    ficha = json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))

    assert ficha["indexing"]["include_sections"] == [
        "Sinais clínicos",
        "Quando levar ao veterinário",
    ]


def test_secoes_declaradas_existem_no_texto_capturado(tmp_path):
    """
    O ingestor compara o nome da seção caractere por caractere, e o
    normalizador **apaga** acentos em vez de normalizá-los: "Diagnóstico" e
    "Diagnostico" são chaves diferentes. Uma seção declarada com acento
    errado é descartada em silêncio.
    """

    base = capturar(tmp_path, "--include", "Sinais clínicos")
    ficha = json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))
    linhas = base.with_suffix(".txt").read_text(encoding="utf-8").splitlines()

    for secao in ficha["indexing"]["include_sections"]:
        assert secao in linhas, secao


def test_ficha_carrega_idioma_e_registro(tmp_path):
    """
    Não chegam ao ChromaDB, e é por isso que precisam estar na ficha: é por
    eles que a etapa 1 vai responder se a busca prefere a língua do relato ou
    o registro de quem escreve para tutor.
    """

    base = capturar(tmp_path, "--language", "pt", "--register", "tutor")
    ficha = json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))

    assert ficha["language"] == "pt"
    assert ficha["register"] == "tutor"


# ----------------------------------------------------------------------
# O que ela recusa
# ----------------------------------------------------------------------


def test_recusa_topico_que_nao_esta_no_mapa(tmp_path):
    """
    O `topic` é o contrato com a base e com o `compare`. Capturar para um
    assunto que ninguém decidiu cobrir cria cobertura que o mapa não conhece.
    """

    baixador = BaixadorFalso(PAGINA.encode("utf-8"), "text/html")

    with pytest.raises(SystemExit, match="mapa de assuntos"):
        main(
            ["https://exemplo.org/x", "--topic", "assunto_inventado",
             "--slug", "x", "--destino", str(tmp_path)],
            baixador=baixador,
        )

    assert not baixador.urls, "recusou depois de baixar; devia recusar antes"


def test_recusa_conteudo_que_a_base_nao_indexa(tmp_path):
    """
    O ingestor aceita só PDF e TXT, e **ignora em silêncio** o resto. Melhor
    falhar aqui, alto, do que descobrir depois que o arquivo nunca foi lido.
    """

    with pytest.raises(SystemExit, match="não suportado"):
        capturar(tmp_path, tipo="application/msword")


def test_pdf_passa_intacto(tmp_path):
    """
    Artigo e caderno técnico são PDF; o extrator de layout do trilho A já
    cuida deles. Reescrever seria estragar.
    """

    bytes_pdf = b"%PDF-1.7\n... conteudo ...\n%%EOF"
    baixador = BaixadorFalso(bytes_pdf, "application/pdf")
    main(
        [*BASE, "--slug", "artigo", "--destino", str(tmp_path)],
        baixador=baixador,
    )

    assert (tmp_path / "gastric_dilatation_volvulus__artigo.pdf").read_bytes() == bytes_pdf


def test_recusa_slug_fora_da_convencao(tmp_path):
    """
    O nome do arquivo é `<topic>__<slug>`, e é por ele que uma captura é
    ligada a uma linha do mapa. Espaço ou acento no slug quebraria isso.
    """

    baixador = BaixadorFalso(PAGINA.encode("utf-8"), "text/html")

    with pytest.raises(SystemExit, match="slug"):
        main(
            [*BASE, "--slug", "PDSA 2024", "--destino", str(tmp_path)],
            baixador=baixador,
        )
