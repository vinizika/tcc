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
<html><head><title>GDV em cães, exemplo</title></head><body>
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

PAGINA_EM_INGLES = """
<html><head><title>GDV in dogs</title></head><body>
<nav><a href="/">Home</a></nav>
<article>
<h1>Bloat in dogs</h1>
<h2>Signs</h2>
<p>The dog retches without bringing anything up, the belly becomes swollen
and hard, they drool a lot and pace around restlessly, unable to settle.
Breathing becomes fast and shallow as the condition progresses, and the gums
may turn pale. Owners usually notice the restlessness first.</p>
<h2>When to contact your vet</h2>
<p>Contact your vet straight away. This condition leads to shock within
hours, and every hour of delay lowers the chance that your dog will survive
the surgery they will almost certainly need.</p>
</article>
</body></html>
"""

BASE = ["https://exemplo.org/gdv", "--topic", "gastric_dilatation_volvulus"]


def capturar(tmp_path, *extras, pagina=PAGINA, tipo="text/html"):
    """
    `pagina` aceita texto (codificado em UTF-8) ou bytes já codificados,
    para os testes de codificação poderem entregar Latin-1.
    """

    bruto = pagina if isinstance(pagina, bytes) else pagina.encode("utf-8")
    main(
        [*BASE, "--slug", "exemplo", "--destino", str(tmp_path), *extras],
        baixador=BaixadorFalso(bruto, tipo),
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
# Codificação
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "codificacao, tipo",
    [
        ("utf-8", "text/html"),
        ("latin-1", "text/html"),
        ("latin-1", "text/html; charset=iso-8859-1"),
        ("cp1252", "text/html"),
    ],
)
def test_acentos_sobrevivem_em_qualquer_codificacao(tmp_path, codificacao, tipo):
    """
    Material veterinário de universidade e de conselho regional brasileiro
    costuma estar em Latin-1. Decodificar isso como UTF-8 transforma "Sinais
    clínicos" em "Sinais cl?nicos" **sem erro nenhum** — e o documento seria
    indexado como lixo. Como a página é a fonte em português que o projeto
    mais precisa, isto não pode depender do servidor declarar o charset.
    """

    texto = capturar(
        tmp_path, pagina=PAGINA.encode(codificacao), tipo=tipo
    ).with_suffix(".txt").read_text(encoding="utf-8")

    assert "Sinais clínicos" in texto
    assert "Torção gástrica em cães" in texto
    assert "�" not in texto


def test_mesma_pagina_em_codificacoes_diferentes_da_o_mesmo_hash(tmp_path):
    """
    O hash é o que liga a aprovação do especialista a um texto. Se ele
    dependesse da codificação de origem, a mesma fonte capturada em duas
    máquinas produziria duas aprovações diferentes.
    """

    import hashlib

    hashes = set()
    for i, (codificacao, tipo) in enumerate(
        [("utf-8", "text/html"), ("latin-1", "text/html; charset=iso-8859-1")]
    ):
        destino = tmp_path / str(i)
        destino.mkdir()
        base = capturar(destino, pagina=PAGINA.encode(codificacao), tipo=tipo)
        hashes.add(hashlib.sha256(base.with_suffix(".txt").read_bytes()).hexdigest())

    assert len(hashes) == 1


# ----------------------------------------------------------------------
# O que ela recusa
# ----------------------------------------------------------------------


def test_recusa_secao_declarada_que_nao_existe_no_texto(tmp_path):
    """
    Esta é a armadilha que o piloto pagou para descobrir: declarei uma seção
    a partir do resultado de busca, e ela não existia na página. O ingestor
    ignora seção não encontrada **em silêncio**, e a curadoria sai diferente
    do que se pensa. Melhor recusar aqui.
    """

    with pytest.raises(SystemExit, match="não existem no texto capturado"):
        capturar(tmp_path, "--include", "Primeiros socorros em casa")


def test_indentacao_nao_sobrevive_a_captura(tmp_path):
    """
    O markdown do trafilatura indenta o que estava aninhado na página. Num
    trecho de ~40 palavras a tabulação não ensina nada — e um heading
    indentado não bate, caractere por caractere, com o nome declarado na
    ficha. A captura da Cornell veio com quatro linhas assim.
    """

    pagina = PAGINA.replace(
        "<h2>Sinais clínicos</h2>",
        "<blockquote><h2>Sinais clínicos</h2></blockquote>",
    )

    linhas = capturar(tmp_path, pagina=pagina).with_suffix(".txt").read_text(
        encoding="utf-8"
    ).splitlines()

    assert not any(linha[:1] in (" ", "	") for linha in linhas if linha)


def test_secao_declarada_casa_pela_mesma_chave_que_o_ingestor(tmp_path):
    """
    O ingestor compara nomes de seção por uma chave que descarta pontuação e
    espaço. Uma trava mais rígida que ele recusaria seção que funcionaria —
    e foi o que quase aconteceu com "Hazardous Potential", que vinha com
    tabulação na frente.
    """

    capturar(tmp_path, "--include", "Sinais clínicos!")


def test_a_tolerancia_nao_alcanca_acento(tmp_path):
    """
    O ingestor **apaga** acentos em vez de normalizá-los, então "clinicos" e
    "clínicos" são chaves diferentes lá. Aqui também têm de ser: relaxar isso
    devolveria o descarte silencioso que a trava existe para evitar.
    """

    with pytest.raises(SystemExit, match="não existem no texto capturado"):
        capturar(tmp_path, "--include", "Sinais clinicos")


def test_recusa_secao_declarada_sem_acento(tmp_path):
    """
    A variante sutil da anterior: o ingestor compara sem normalizar acentos,
    então "Sinais clinicos" e "Sinais clínicos" são chaves diferentes. Um
    acento faltando descarta a seção inteira sem avisar.
    """

    with pytest.raises(SystemExit, match="não existem no texto capturado"):
        capturar(tmp_path, "--include", "Sinais clinicos")


def test_recusa_pagina_curta_demais_para_ser_fonte(tmp_path):
    """
    Página de erro, muro de login e conteúdo que só existe depois do
    JavaScript devolvem pouquíssimo texto — e viraram documento silencioso
    antes desta trava.
    """

    vazia = "<html><body><article><p>Página não encontrada</p></article></body></html>"

    with pytest.raises(SystemExit, match="palavras foram extraídas"):
        capturar(tmp_path, pagina=vazia)


def test_recusa_html_que_o_servidor_anuncia_como_pdf(tmp_path):
    """
    Acontece com repositório universitário: o link termina em .pdf, o
    servidor diz `application/pdf` e devolve a página de login. O arquivo
    salvo passaria pelo extrator de PDF e falharia lá na frente, longe daqui.
    """

    with pytest.raises(SystemExit, match="não começa com %PDF"):
        capturar(tmp_path, tipo="application/pdf")


def test_recusa_titulo_longo(tmp_path):
    """
    O título entra no começo de **todos** os trechos do documento, e um
    trecho tem ~40 palavras. Título comprido é conteúdo clínico que não cabe.
    """

    with pytest.raises(SystemExit, match="palavras"):
        capturar(tmp_path, "--title", "Um titulo muito longo que ocupa espaco demais")


def test_recusa_sobrescrever_captura_existente(tmp_path):
    """
    O especialista aprova um arquivo com hash. Trocar o arquivo por baixo,
    mantendo o nome, invalidaria a aprovação sem que ninguém percebesse.
    """

    capturar(tmp_path)

    with pytest.raises(SystemExit, match="Já existe captura"):
        capturar(tmp_path)


def test_forcar_permite_substituir_de_proposito(tmp_path):
    """
    Recapturar é legítimo — a página mudou, ou a captura anterior saiu ruim.
    O que não pode é acontecer sem querer.
    """

    primeiro = capturar(tmp_path).with_suffix(".txt").read_text(encoding="utf-8")
    outra = PAGINA.replace("Sinais clínicos", "Sinais clínicos revisados")
    segundo = capturar(tmp_path, "--forcar", pagina=outra).with_suffix(
        ".txt"
    ).read_text(encoding="utf-8")

    assert primeiro != segundo


def test_avisa_quando_o_idioma_declarado_nao_e_o_do_corpo(tmp_path, capsys):
    """
    A armadilha do MSD, encontrada no piloto: o site traduz o menu e os
    títulos e deixa o corpo em inglês. Uma ficha que diz `language: pt` sobre
    um corpo em inglês faria o experimento de idioma × registro medir a coisa
    errada. Avisa, não recusa — a heurística não é boa o bastante para
    decidir sozinha.
    """

    capturar(tmp_path, "--language", "pt", pagina=PAGINA_EM_INGLES)

    assert "corpo parece estar em 'en'" in capsys.readouterr().out


def test_nao_avisa_quando_o_idioma_bate(tmp_path, capsys):

    capturar(tmp_path, "--language", "en", pagina=PAGINA_EM_INGLES)

    assert "corpo parece estar" not in capsys.readouterr().out


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
