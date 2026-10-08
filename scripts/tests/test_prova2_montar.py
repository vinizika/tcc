"""
A divisão da prova 2 (rodada 20 do João, decisão 4; feita na rodada 17 do
Ryu): um relato de cada quadro na calibração, 2 + 2 + 1 dos especiais, e o
sorteio reproduzível pela semente.
"""

from collections import Counter

import prova2_montar
from prova2_montar import dividir


def linhas_sinteticas():
    linhas = []
    for quadro in ("a", "b", "c"):
        for indice in range(5):
            linhas.append({"id": f"{quadro}{indice}", "topic": quadro, "difficulty_tag": "controle_leve"})
    for tag, quantos in (("informacao_insuficiente", 10), ("fora_do_mapa_clinico", 8), ("nao_clinico", 7)):
        for indice in range(quantos):
            linhas.append({"id": f"{tag}{indice}", "topic": "", "difficulty_tag": tag})
    return linhas


def test_um_por_quadro_e_especiais_na_proporcao():
    linhas = linhas_sinteticas()

    dividir(linhas)

    calibracao = [l for l in linhas if l["split"] == "calibracao"]
    assert Counter(l["topic"] for l in calibracao if l["topic"]) == {"a": 1, "b": 1, "c": 1}
    assert Counter(l["difficulty_tag"] for l in calibracao if not l["topic"]) == {
        "informacao_insuficiente": 2, "fora_do_mapa_clinico": 2, "nao_clinico": 1}
    assert {l["split"] for l in linhas} == {"calibracao", "teste"}


def test_sorteio_reproduz_e_depende_da_semente():
    primeira, segunda, outra = linhas_sinteticas(), linhas_sinteticas(), linhas_sinteticas()

    dividir(primeira)
    dividir(segunda)
    dividir(outra, semente="outra-semente")

    assert [l["split"] for l in primeira] == [l["split"] for l in segunda]
    assert [l["split"] for l in primeira] != [l["split"] for l in outra]


def test_a_prova_2_versionada_tem_66_de_calibracao_e_264_de_teste():
    conteudo, conferencia = prova2_montar.montar()

    totais = {split: sum(classes.values()) for split, classes in conferencia["por_split"].items()}
    assert totais == {"calibracao": 66, "teste": 264}
    assert conferencia["quadros"] == 61
