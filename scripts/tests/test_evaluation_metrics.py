"""
Testes das métricas de avaliação.

O mais importante é o "teste dourado": alimentar o módulo com as 98
respostas registradas em 04/05 e conferir que ele reproduz exatamente os
números daquele dia. É isso que garante que a régua nova mede a mesma coisa
que a antiga — sem essa garantia, comparar os resultados novos com os
70,41% históricos não faria sentido.
"""

from pathlib import Path

import pandas as pd
import pytest

from evaluation_metrics import (
    compute_metrics,
    precision_recall_f1,
    wilson_ci,
)


RAIZ = Path(__file__).resolve().parents[2]
RESULTADO_HISTORICO = RAIZ / "data" / "evaluation" / "accuracy_results.csv"


@pytest.fixture
def previsoes_de_2026_05_04() -> pd.DataFrame:
    """
    As respostas reais da medição de 04/05, no formato que o runner novo
    produz. As colunas de instrumentação não existiam na época.
    """

    df = pd.read_csv(RESULTADO_HISTORICO)

    return pd.DataFrame(
        {
            "row_id": df["index"],
            "animal": df["animal"],
            "source": df["source"],
            "expected": df["expected"],
            "predicted": df["predicted"],
            "status": "ok",
            "json_parsed": df["json_valid"],
            "schema_valid": df["json_valid"],
        }
    )


def linha(**campos) -> dict:
    base = {
        "row_id": 0,
        "animal": "Dog",
        "source": "original",
        "expected": "EMERGENCIA",
        "predicted": "EMERGENCIA",
        "status": "ok",
    }
    base.update(campos)
    return base


# ----------------------------------------------------------------------
# Teste dourado
# ----------------------------------------------------------------------


def test_reproduz_os_numeros_de_04_05(previsoes_de_2026_05_04):

    m = compute_metrics(previsoes_de_2026_05_04)
    c = m["classification"]

    assert c["n"] == 98

    # Acurácia estrita: 69 acertos em 98, os 70,41% do diário.
    assert c["accuracy_strict"] == pytest.approx(0.7041, abs=1e-4)

    emergencia = c["per_class"]["EMERGENCIA"]
    nao_emergencia = c["per_class"]["NAO_EMERGENCIA"]

    assert emergencia["support"] == 71
    assert emergencia["true_positive"] == 65
    assert emergencia["recall"] == pytest.approx(65 / 71, abs=1e-4)
    assert emergencia["precision"] == pytest.approx(0.7738, abs=1e-4)
    assert emergencia["f1"] == pytest.approx(0.8387, abs=1e-4)

    assert nao_emergencia["support"] == 27
    assert nao_emergencia["true_positive"] == 4
    assert nao_emergencia["recall"] == pytest.approx(4 / 27, abs=1e-4)

    assert c["false_non_urgent"] == 4
    assert c["false_urgent"] == 19
    assert c["confusion_matrix"]["EMERGENCIA"]["INCERTO"] == 2
    assert c["confusion_matrix"]["NAO_EMERGENCIA"]["INCERTO"] == 4
    assert c["invalid_rate"] == 0.0


def test_a_metrica_principal_revela_o_que_a_acuracia_esconde(
    previsoes_de_2026_05_04,
):
    """
    A acurácia estrita de 70,41% fica abaixo do chute ingênuo de 72,4%. A
    balanceada mostra por quê: o sistema acerta quase toda emergência e
    quase nenhuma não emergência.
    """

    m = compute_metrics(previsoes_de_2026_05_04)
    c = m["classification"]

    esperada = (65 / 71 + 4 / 27) / 2

    assert c["balanced_accuracy"] == pytest.approx(esperada, abs=1e-4)
    assert c["balanced_accuracy"] < 0.54
    assert c["accuracy_strict"] < m["baselines"]["always_emergencia"]


def test_estrato_por_origem_nao_inventa_precisao(previsoes_de_2026_05_04):
    """
    Neste conjunto cada origem tem um único rótulo, então precisão e F1 não
    significam nada e precisam sair como nulos, com a limitação declarada.
    """

    por_origem = compute_metrics(previsoes_de_2026_05_04)["strata"][
        "by_source"
    ]

    sintetico = por_origem["llm_data_augmentation"]

    assert sintetico["n"] == 27
    assert sintetico["labels"] == ["NAO_EMERGENCIA"]
    assert sintetico["precision"] is None
    assert sintetico["f1"] is None
    assert sintetico["note"]
    assert sintetico["recall"] == pytest.approx(4 / 27, abs=1e-4)


# ----------------------------------------------------------------------
# Baselines triviais
# ----------------------------------------------------------------------


def test_baselines_triviais_expoem_a_separabilidade_do_conjunto():
    """
    A classe "não emergência" foi gerada a partir de cinco sintomas leves e
    com menos sintomas por linha. Regras sem nenhum modelo acertam quase
    tudo — e é por isso que elas aparecem no relatório ao lado do resultado.
    """

    dados = pd.DataFrame(
        [
            linha(
                row_id=1,
                expected="EMERGENCIA",
                predicted="EMERGENCIA",
                n_symptoms=5,
                symptoms=["Fever", "Vomiting", "Seizures", "Pain", "Shock"],
            ),
            linha(
                row_id=2,
                expected="NAO_EMERGENCIA",
                predicted="EMERGENCIA",
                n_symptoms=3,
                symptoms=["Sneezing", "Nasal Discharge", "Lameness"],
            ),
        ]
    )

    baselines = compute_metrics(dados)["baselines"]

    assert baselines["rule_few_symptoms"] == 1.0
    assert baselines["rule_only_mild_symptoms"] == 1.0
    assert baselines["always_emergencia"] == 0.5


# ----------------------------------------------------------------------
# Casos de borda
# ----------------------------------------------------------------------


def test_tudo_incerto_nao_quebra_e_zera_a_cobertura():

    dados = pd.DataFrame(
        [linha(row_id=i, predicted="INCERTO") for i in range(4)]
    )

    c = compute_metrics(dados)["classification"]

    assert c["coverage"] == 0.0
    assert c["accuracy_decided"] is None
    assert c["accuracy_strict"] == 0.0
    assert c["incerto_rate"] == 1.0


def test_rotulo_desconhecido_conta_como_erro():
    """
    Um rótulo fora do vocabulário não pode sumir das contas: viraria uma
    acurácia calculada sobre menos linhas do que a rodada teve.
    """

    dados = pd.DataFrame(
        [
            linha(row_id=1, predicted="EMERGENCIA"),
            linha(row_id=2, predicted="Emergência!"),
        ]
    )

    c = compute_metrics(dados)["classification"]

    assert c["other_rate"] == 0.5
    assert c["accuracy_strict"] == 0.5
    assert c["confusion_matrix"]["EMERGENCIA"]["OTHER"] == 1


def test_linhas_com_erro_saem_da_conta_mas_sao_reportadas():

    dados = pd.DataFrame(
        [
            linha(row_id=1),
            linha(row_id=2, status="error", predicted=None),
        ]
    )

    m = compute_metrics(dados)

    assert m["rows_evaluated"] == 1
    assert m["rows_with_error"] == 1


def test_sem_recuperacao_a_ancoragem_e_nula_e_nao_zero():
    """
    Numa rodada sem busca, "zero citações" seria lido como falha de
    ancoragem, quando na verdade a etapa nem existiu.
    """

    dados = pd.DataFrame(
        [linha(row_id=1, retrieval_returned=0, n_sources_cited=0)]
    )

    assert compute_metrics(dados)["grounding"] is None


def test_com_recuperacao_mede_quantas_linhas_ficaram_abaixo_do_limiar():

    dados = pd.DataFrame(
        [
            linha(
                row_id=1,
                retrieval_returned=3,
                n_sources_cited=1,
                n_invalid_citations=0,
                retrieval_max_score=0.85,
                cited_chunk_ids=["c1"],
            ),
            linha(
                row_id=2,
                retrieval_returned=3,
                n_sources_cited=0,
                n_invalid_citations=1,
                retrieval_max_score=0.42,
                cited_chunk_ids=[],
            ),
        ]
    )

    ancoragem = compute_metrics(dados)["grounding"]

    assert ancoragem["share_rows_with_citation"] == 0.5
    assert ancoragem["share_rows_max_score_below_0_70"] == 0.5
    assert ancoragem["share_rows_invalid_citation"] == 0.5
    assert ancoragem["citations_per_chunk"] == {"c1": 1}


def test_latencia_ignora_a_linha_que_carregou_o_modelo():

    dados = pd.DataFrame(
        [
            linha(row_id=1, total_s=30.0, load_duration_s=28.0),
            linha(row_id=2, total_s=2.0, load_duration_s=0.0),
            linha(row_id=3, total_s=3.0, load_duration_s=0.0),
        ]
    )

    latencia = compute_metrics(dados)["latency"]

    assert latencia["rows_with_model_load"] == 1
    assert latencia["total_s"]["mean"] == pytest.approx(2.5)


# ----------------------------------------------------------------------
# Repetições
# ----------------------------------------------------------------------


def test_repeticoes_medem_a_instabilidade_linha_a_linha():
    """
    Uma linha que muda de classificação entre execuções idênticas é ruído,
    não resultado. O número de linhas instáveis é o que descreve isso.
    """

    dados = pd.DataFrame(
        [
            linha(row_id=1, repeat=0, predicted="EMERGENCIA"),
            linha(row_id=2, repeat=0, predicted="EMERGENCIA"),
            linha(row_id=1, repeat=1, predicted="EMERGENCIA"),
            linha(row_id=2, repeat=1, predicted="NAO_EMERGENCIA"),
        ]
    )

    repeticoes = compute_metrics(dados)["repeats"]

    assert repeticoes["n_repeats"] == 2
    assert repeticoes["exact_agreement_rate"] == 0.5
    assert repeticoes["unstable_row_ids"] == [2]
    assert len(repeticoes["per_repeat"]) == 2


def test_sem_repeticoes_o_bloco_nao_aparece():

    dados = pd.DataFrame([linha(row_id=1, repeat=0)])

    assert compute_metrics(dados)["repeats"] is None


# ----------------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------------


def test_intervalo_de_wilson_em_valor_conhecido():

    baixo, alto = wilson_ci(65, 71)

    assert baixo == pytest.approx(0.8272, abs=1e-3)
    assert alto == pytest.approx(0.9598, abs=1e-3)

    assert wilson_ci(0, 0) is None


def test_classe_ausente_devolve_nulo_em_vez_de_zero():

    dados = pd.DataFrame([linha(row_id=1)])

    resultado = precision_recall_f1(dados, "NAO_EMERGENCIA")

    assert resultado["support"] == 0
    assert resultado["recall"] is None
    assert resultado["f1"] is None
