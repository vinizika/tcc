"""
Testes do gerador das fichas de triagem (rodada 23 do João).

O texto que sai do gerador é o texto que a autópsia 2 mediu. Estes testes
travam as regras de montagem nos pontos em que um "conserto" inocente mudaria
o texto das fichas sem ninguém medir.
"""

import sync_fichas


def _linha(**kw):
    base = {
        "id": "x", "quadro": "Quadro X", "especie": "ambos", "classe": "emergencia",
        "urgencia": "imediato", "sinais_que_o_tutor_relata": "tossindo;respira rapido",
        "discriminador": "Ha esforco para respirar?", "par_de_confusao": "y",
        "motivo": "Queixa frequente no pronto-socorro; caso b03 da regua", "etapa": "1",
        "por_que_importa": "",
    }
    base.update(kw)
    return base


def _linhas(**kw):
    x = _linha(**kw)
    return {"x": x, "y": _linha(id="y", quadro="Quadro Y", urgencia="rotina"), "z": _linha(id="z", quadro="Quadro Z")}


def test_arquivo_gerado_em_dia():
    sync_fichas.main(["--check"])


def test_ficha_de_leitura_segue_a_regra_medida():
    linhas = _linhas()
    texto = sync_fichas.reading_text(linhas["x"], linhas)

    assert texto == (
        "Ficha de triagem: Quadro X (cao e gato). "
        "Sinais que o tutor costuma relatar: tossindo, respira rapido. "
        "Como diferenciar: Ha esforco para respirar?. "
        "Pode ser confundido com: Quadro Y. "
        "Por que importa: Queixa frequente no pronto-socorro. "
        "Conduta: Isto e uma emergencia: procure um veterinario agora, sem esperar."
    )
    assert sync_fichas.reading_title(linhas["x"]) == "Ficha de triagem: Quadro X"


def test_por_que_importa_preenchido_substitui_o_motivo():
    linhas = _linhas(por_que_importa="Sem ar, o animal pode morrer em minutos")
    texto = sync_fichas.reading_text(linhas["x"], linhas)

    assert "Por que importa: Sem ar, o animal pode morrer em minutos." in texto
    assert "pronto-socorro" not in texto


def test_linha_com_mais_de_uma_gemea_nao_ganha_a_frase_do_par():
    linhas = _linhas(par_de_confusao="y;z")

    assert "Pode ser confundido com" not in sync_fichas.reading_text(linhas["x"], linhas)


def _rascunho(**kw):
    base = {
        "topico": "x", "titulo": "Quadro X (nome técnico)", "nome_leigo": "falta de ar", "especie": "cão e gato",
        "como_o_tutor_conta": [
            {"texto": "Tá tossindo muito.", "origem": "mapa", "trecho": "", "fonte": ""},
            {"texto": "Frase de documento sem trecho", "origem": "documento", "trecho": "", "fonte": "a.pdf"},
            {"texto": "Frase de documento", "origem": "documento", "trecho": "coughing dogs were seen", "fonte": "a.pdf"},
        ],
        "sinais_de_alarme": [{"texto": "Língua roxa", "origem": "geral", "trecho": "", "fonte": ""}],
        "como_diferenciar": [{"texto": "No quadro Y o cão está bem", "origem": "geral", "gemea": "y"}],
        "por_que_importa": {"texto": "Pode ser grave", "origem": "mapa"},
    }
    base.update(kw)
    return base


def test_ficha_de_busca_segue_a_regra_medida():
    linhas = _linhas()
    rascunhos = {"x": _rascunho(), "y": {"topico": "y", "titulo": "Quadro Y leve"}}
    texto = sync_fichas.search_text("x", rascunhos, linhas)

    assert texto == (
        "Ficha de triagem: Quadro X (nome técnico, falta de ar) — cão e gato. "
        "Como o tutor costuma contar: Tá tossindo muito; Frase de documento; Respira rapido. "
        "Sinais de alarme: Língua roxa. "
        "Como diferenciar de quadro y leve: No quadro Y o cão está bem. "
        "Por que importa: Pode ser grave. "
        "Conduta: Isto é uma emergência: procure um veterinário agora, sem esperar."
    )


def test_sinal_do_mapa_coberto_pelo_autor_nao_e_repetido():
    linhas = _linhas(sinais_que_o_tutor_relata="tossindo")
    itens = sync_fichas.draft_items(_rascunho(), linhas["x"])

    assert itens["sinais_inseridos"] == []


def test_referencias_so_de_documentos_aprovados():
    payload = sync_fichas.build_payload()

    assert payload["count"] == 61
    for ficha in payload["fichas"]:
        assert ficha["references"], ficha["topic"]
        for referencia in ficha["references"]:
            assert referencia["title"] and referencia["document"]


def test_hash_ignora_quebra_de_linha_do_checkout(tmp_path):
    lf, crlf = tmp_path / "lf.csv", tmp_path / "crlf.csv"
    lf.write_bytes(b"a,b\n1,2\n")
    crlf.write_bytes(b"a,b\r\n1,2\r\n")

    assert sync_fichas._text_bytes(lf) == sync_fichas._text_bytes(crlf)
