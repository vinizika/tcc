"""
Testes da comparação entre rodadas.

Os valores de referência do McNemar são calculáveis à mão, e é isso que
torna o teste útil: se a fórmula for trocada por uma aproximação, o número
muda e o teste avisa.
"""

import numpy as np
import pytest

from report_evaluation import bootstrap_diferenca, mcnemar


# ----------------------------------------------------------------------
# McNemar
# ----------------------------------------------------------------------


def test_desacordo_unilateral_de_seis_linhas_e_significativo():
    """
    Com 6 desacordos todos na mesma direção, p = 2 * (1/2)^6 = 0,03125.
    É o menor desacordo que atinge significância neste conjunto — daí a
    ressalva de que a diferença mínima detectável é de cerca de 6 linhas.
    """

    resultado = mcnemar(b=6, c=0)

    assert resultado["p_exact"] == pytest.approx(0.03125, abs=1e-6)
    assert resultado["p_exact"] < 0.05


def test_cinco_linhas_ainda_nao_bastam():

    assert mcnemar(b=5, c=0)["p_exact"] == pytest.approx(0.0625, abs=1e-6)


def test_desacordo_equilibrado_nao_indica_diferenca():

    assert mcnemar(b=4, c=4)["p_exact"] == 1.0


def test_previsoes_identicas_sao_declaradas():
    """
    Sem desacordo não há o que testar; devolver p=1 com a explicação evita
    a leitura de que "o teste não encontrou diferença" quando na verdade as
    duas rodadas fizeram exatamente as mesmas previsões.
    """

    resultado = mcnemar(b=0, c=0)

    assert resultado["p_exact"] == 1.0
    assert "idênticas" in resultado["note"]


def test_p_mid_e_menos_conservador_que_o_exato():
    """
    A binomial exata é conservadora com poucas amostras. A variante mid-p é
    reportada ao lado justamente para não descartar um efeito real.
    """

    resultado = mcnemar(b=6, c=1)

    assert resultado["p_mid"] < resultado["p_exact"]


def test_o_teste_e_simetrico():

    assert mcnemar(b=7, c=2)["p_exact"] == mcnemar(b=2, c=7)["p_exact"]


# ----------------------------------------------------------------------
# Bootstrap
# ----------------------------------------------------------------------


def test_intervalo_contem_a_diferenca_observada():

    a = np.array([1] * 70 + [0] * 30)
    b = np.array([1] * 60 + [0] * 40)

    resultado = bootstrap_diferenca(a, b, reamostragens=2000)

    assert resultado["diff"] == pytest.approx(0.10, abs=1e-9)

    baixo, alto = resultado["ci95"]

    assert baixo <= resultado["diff"] <= alto


def test_intervalo_e_reproduzivel():
    """
    A mesma comparação precisa dar o mesmo intervalo, ou dois relatórios da
    mesma rodada discordariam entre si.
    """

    a = np.array([1, 0] * 30)
    b = np.array([1, 1, 0, 0] * 15)

    primeiro = bootstrap_diferenca(a, b, reamostragens=1000)
    segundo = bootstrap_diferenca(a, b, reamostragens=1000)

    assert primeiro["ci95"] == segundo["ci95"]


def test_sem_diferenca_o_intervalo_cerca_o_zero():

    iguais = np.array([1] * 50 + [0] * 50)

    resultado = bootstrap_diferenca(iguais, iguais, reamostragens=1000)

    assert resultado["diff"] == 0.0
    assert resultado["ci95"] == [0.0, 0.0]
