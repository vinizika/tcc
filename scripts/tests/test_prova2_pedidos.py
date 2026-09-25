import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import prova2_pedidos  # noqa: E402


def test_composicao_da_prova_2():
    por_lote = prova2_pedidos.gerar()
    todos = [p for lote in por_lote.values() for p in lote]

    assert len(todos) == 330
    do_mapa = [p for p in todos if p["topic"]]
    especiais = [p for p in todos if not p["topic"]]
    assert Counter(p["classe"] for p in do_mapa) == Counter({"EMERGENCIA": 190, "NAO_EMERGENCIA": 115})
    assert len(especiais) == 25
    assert Counter(p["difficulty_tag"] for p in especiais) == Counter(
        {"informacao_insuficiente": 10, "fora_do_mapa_clinico": 8, "nao_clinico": 7})
    assert len({p["id"] for p in todos}) == 330


def test_tom_mas_e_palpite_por_quadro():
    por_lote = prova2_pedidos.gerar()
    por_quadro: dict[str, list[dict]] = {}
    for p in (p for lote in por_lote.values() for p in lote if p["topic"]):
        por_quadro.setdefault(p["topic"], []).append(p)

    assert len(por_quadro) == 61
    for pedidos in por_quadro.values():
        classe = pedidos[0]["classe"]
        assert sorted(p["tom"] for p in pedidos) == sorted(prova2_pedidos.TONS[classe])
        assert sum(p["usar_mas"] for p in pedidos) == 2
        assert sum(p["palpite_permitido"] for p in pedidos) == 1
        assert len({p["persona"] for p in pedidos}) == 5
        for p in pedidos:
            if p["familia_calma"] == "mas_come_normal":
                assert p["usar_mas"]


def test_o_autor_nao_ve_o_topico_nem_a_urgencia_do_mapa():
    pedido = prova2_pedidos.gerar()[1][0]
    visto = prova2_pedidos.para_instancia(pedido)

    for campo in ("topic", "expected_urgency", "difficulty_tag", "confusion_pair_topic"):
        assert campo not in visto
    assert pedido["topic"] not in json.dumps(visto)


def test_arquivos_versionados_em_dia():
    prova2_pedidos.main(["--check"])


def test_casos_da_prova_2_em_dia_e_com_a_composicao_da_rodada_20():
    import prova2_montar

    prova2_montar.main(["--check"])
    _, conferencia = prova2_montar.montar()
    assert conferencia["n"] == 330
    assert conferencia["do_mapa_por_classe"] == {"EMERGENCIA": 190, "NAO_EMERGENCIA": 115}
    assert conferencia["quadros"] == 61
    assert conferencia["textos_repetidos"] == 0
