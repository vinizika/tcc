"""
Métricas das rodadas de avaliação.

Módulo puro: recebe um DataFrame de previsões e devolve um dicionário de
números. Não faz rede nem lê configuração, então roda offline sobre uma
rodada antiga e é fácil de testar.

Sobre a métrica principal. O conjunto tem 71 emergências e 27 não
emergências, então um modelo que sempre responde "emergência" acerta 72,4%.
Por isso o número de destaque é a **acurácia balanceada** (média do recall
das duas classes), que não depende dessa proporção. A acurácia estrita
continua sendo calculada porque é ela que liga os resultados novos à
medição de 04/05, que registrou 70,41%.

Abstenções (INCERTO) e respostas mal formadas (INVALID_JSON) contam como
erro em todas as acurácias: um sistema que se recusa a decidir não está
ajudando o tutor. `coverage` e `accuracy_decided` mostram o outro ângulo.
"""

import math
from typing import Any, Optional

import pandas as pd


CLASSES_REAIS = ["EMERGENCIA", "NAO_EMERGENCIA"]

COLUNAS_MATRIZ = [
    "EMERGENCIA",
    "NAO_EMERGENCIA",
    "INCERTO",
    "INVALID_JSON",
    "OTHER",
]

# Os cinco sintomas que a geração sintética usou para montar a classe "não
# emergência". Estão aqui para calcular o baseline trivial que mostra o
# quanto o conjunto é separável sem nenhum modelo.
SINTOMAS_LEVES = {
    "Eye Discharge",
    "Nasal Discharge",
    "Skin Lesions",
    "Sneezing",
    "Lameness",
}

LIMIAR_RELEVANCIA = 0.70


def _divisao(numerador: float, denominador: float) -> Optional[float]:
    """
    Devolve None em vez de zero quando não há denominador: zero seria lido
    como "mediu e deu zero", e a diferença importa nos estratos pequenos.
    """

    if not denominador:
        return None

    return numerador / denominador


def wilson_ci(acertos: int, total: int, z: float = 1.96) -> Optional[list]:
    """
    Intervalo de confiança de Wilson para uma proporção.

    Escolhido em vez do intervalo normal simples porque se comporta bem com
    poucas amostras e perto de 0 ou 1 — o caso dos estratos deste conjunto,
    onde a classe menor tem 27 linhas. Fórmula fechada, sem scipy.
    """

    if not total:
        return None

    proporcao = acertos / total
    denominador = 1 + z**2 / total

    centro = (proporcao + z**2 / (2 * total)) / denominador

    margem = (
        z
        * math.sqrt(
            proporcao * (1 - proporcao) / total
            + z**2 / (4 * total**2)
        )
        / denominador
    )

    return [
        round(max(0.0, centro - margem), 4),
        round(min(1.0, centro + margem), 4),
    ]


def precision_recall_f1(df: pd.DataFrame, classe: str) -> dict:
    """
    Precisão, revocação e F1 de uma classe.

    Mantém a semântica do script de 04/05: INCERTO e INVALID_JSON nunca são
    previsão de uma classe real, então entram apenas como falso negativo da
    classe esperada. É o que torna os números comparáveis com o histórico.
    """

    verdadeiro_positivo = len(
        df[(df["expected"] == classe) & (df["predicted"] == classe)]
    )
    falso_positivo = len(
        df[(df["expected"] != classe) & (df["predicted"] == classe)]
    )
    falso_negativo = len(
        df[(df["expected"] == classe) & (df["predicted"] != classe)]
    )

    precisao = _divisao(
        verdadeiro_positivo, verdadeiro_positivo + falso_positivo
    )
    revocacao = _divisao(
        verdadeiro_positivo, verdadeiro_positivo + falso_negativo
    )

    if precisao and revocacao:
        f1 = 2 * precisao * revocacao / (precisao + revocacao)
    elif precisao is None or revocacao is None:
        f1 = None
    else:
        f1 = 0.0

    return {
        "support": int(len(df[df["expected"] == classe])),
        "true_positive": verdadeiro_positivo,
        "false_positive": falso_positivo,
        "false_negative": falso_negativo,
        "precision": precisao,
        "recall": revocacao,
        "recall_ci95": wilson_ci(
            verdadeiro_positivo, verdadeiro_positivo + falso_negativo
        ),
        "f1": f1,
    }


def matriz_de_confusao(df: pd.DataFrame) -> dict:
    """
    Matriz no mesmo formato usado em 04/05, para leitura lado a lado.
    """

    matriz = pd.crosstab(df["expected"], df["predicted"], dropna=False)

    for coluna in COLUNAS_MATRIZ:
        if coluna not in matriz.columns:
            matriz[coluna] = 0

    matriz = matriz.reindex(
        index=CLASSES_REAIS,
        columns=COLUNAS_MATRIZ,
        fill_value=0,
    )

    return {
        real: {previsto: int(matriz.loc[real, previsto]) for previsto in COLUNAS_MATRIZ}
        for real in CLASSES_REAIS
    }


def _baselines(df: pd.DataFrame) -> dict:
    """
    O que se acerta sem modelo nenhum.

    Existe porque o conjunto é muito mais separável do que parece: a classe
    "não emergência" foi gerada a partir de cinco sintomas leves e com menos
    sintomas por linha, então regras triviais chegam perto de 100%. Sem
    estes números ao lado, uma acurácia de 70% parece boa.
    """

    total = len(df)

    if not total:
        return {}

    esperado = df["expected"]

    sempre_emergencia = _divisao(
        int((esperado == "EMERGENCIA").sum()), total
    )

    resultado = {
        "always_emergencia": sempre_emergencia,
        "rule_few_symptoms": None,
        "rule_only_mild_symptoms": None,
    }

    if "n_symptoms" in df.columns and df["n_symptoms"].notna().any():
        previsto = df["n_symptoms"].apply(
            lambda n: "NAO_EMERGENCIA" if n < 5 else "EMERGENCIA"
        )
        resultado["rule_few_symptoms"] = _divisao(
            int((previsto == esperado).sum()), total
        )

    if "symptoms" in df.columns and df["symptoms"].notna().any():

        def por_vocabulario(sintomas) -> str:
            if not isinstance(sintomas, (list, tuple)):
                return "EMERGENCIA"

            leves = set(sintomas) <= SINTOMAS_LEVES

            return "NAO_EMERGENCIA" if leves else "EMERGENCIA"

        previsto = df["symptoms"].apply(por_vocabulario)
        resultado["rule_only_mild_symptoms"] = _divisao(
            int((previsto == esperado).sum()), total
        )

    return resultado


def _latencia(df: pd.DataFrame) -> dict:
    """
    Tempos por etapa, ignorando as linhas que pagaram o carregamento do
    modelo — elas medem a inicialização, não o sistema em uso.
    """

    if "load_duration_s" in df.columns:
        aquecidas = df[
            df["load_duration_s"].fillna(0) <= 0.5
        ]
        com_carga = len(df) - len(aquecidas)
    else:
        aquecidas = df
        com_carga = 0

    colunas = [
        "query_s",
        "retrieval_s",
        "generation_s",
        "total_s",
        "client_s",
    ]

    resumo: dict[str, Any] = {"rows_with_model_load": com_carga}

    for coluna in colunas:
        if coluna not in aquecidas.columns:
            continue

        valores = pd.to_numeric(aquecidas[coluna], errors="coerce").dropna()

        if valores.empty:
            continue

        resumo[coluna] = {
            "mean": round(float(valores.mean()), 3),
            "median": round(float(valores.median()), 3),
            "p95": round(float(valores.quantile(0.95)), 3),
        }

    for coluna in ("prompt_tokens", "completion_tokens"):
        if coluna in aquecidas.columns:
            valores = pd.to_numeric(
                aquecidas[coluna], errors="coerce"
            ).dropna()
            if not valores.empty:
                resumo[coluna + "_mean"] = round(float(valores.mean()), 1)

    return resumo


def _ancoragem(df: pd.DataFrame, com_recuperacao: bool) -> Optional[dict]:
    """
    O quanto as respostas se apoiaram nos documentos.

    Devolve None quando a rodada não usou recuperação: ali "zero citações"
    não é um resultado ruim, é a ausência da etapa — e um zero no relatório
    seria lido como falha.
    """

    if not com_recuperacao:
        return None

    total = len(df)

    if not total:
        return None

    resultado: dict[str, Any] = {}

    if "n_sources_cited" in df.columns:
        citadas = pd.to_numeric(
            df["n_sources_cited"], errors="coerce"
        ).fillna(0)
        resultado["mean_cited_sources"] = round(float(citadas.mean()), 2)
        resultado["share_rows_with_citation"] = _divisao(
            int((citadas > 0).sum()), total
        )

    if "n_invalid_citations" in df.columns:
        invalidas = pd.to_numeric(
            df["n_invalid_citations"], errors="coerce"
        ).fillna(0)
        resultado["share_rows_invalid_citation"] = _divisao(
            int((invalidas > 0).sum()), total
        )

    # Dois cortes diferentes convivem no sistema e não podem ser
    # confundidos: este é o limiar de relevância da busca.
    if "retrieval_max_score" in df.columns:
        maximo = pd.to_numeric(
            df["retrieval_max_score"], errors="coerce"
        )
        avaliaveis = maximo.notna().sum()
        if avaliaveis:
            resultado["share_rows_max_score_below_0_70"] = _divisao(
                int((maximo < LIMIAR_RELEVANCIA).sum()), int(avaliaveis)
            )
            resultado["mean_max_score"] = round(float(maximo.mean()), 4)

    if "cited_chunk_ids" in df.columns:
        contagem: dict[str, int] = {}
        for lista in df["cited_chunk_ids"].dropna():
            if isinstance(lista, (list, tuple)):
                for identificador in lista:
                    contagem[identificador] = (
                        contagem.get(identificador, 0) + 1
                    )
        if contagem:
            resultado["citations_per_chunk"] = dict(
                sorted(contagem.items(), key=lambda par: -par[1])
            )

    return resultado


def _bloco_de_classificacao(df: pd.DataFrame) -> dict:
    """
    O núcleo: acurácias, matriz e métricas por classe.
    """

    total = len(df)

    acertos = int((df["expected"] == df["predicted"]).sum())

    decididas = df[df["predicted"].isin(CLASSES_REAIS)]

    por_classe = {
        classe: precision_recall_f1(df, classe) for classe in CLASSES_REAIS
    }

    revocacoes = [
        por_classe[classe]["recall"]
        for classe in CLASSES_REAIS
        if por_classe[classe]["recall"] is not None
    ]

    f1s = [
        por_classe[classe]["f1"]
        for classe in CLASSES_REAIS
        if por_classe[classe]["f1"] is not None
    ]

    bloco = {
        "n": total,
        "balanced_accuracy": (
            sum(revocacoes) / len(revocacoes) if revocacoes else None
        ),
        "accuracy_strict": _divisao(acertos, total),
        "accuracy_strict_ci95": wilson_ci(acertos, total),
        "coverage": _divisao(len(decididas), total),
        "accuracy_decided": _divisao(
            int((decididas["expected"] == decididas["predicted"]).sum()),
            len(decididas),
        ),
        "macro_f1": (sum(f1s) / len(f1s) if f1s else None),
        "per_class": por_classe,
        "confusion_matrix": matriz_de_confusao(df),
    }

    # O par clínico: o denominador é o total de cada classe, não o conjunto
    # todo, porque é assim que a leitura faz sentido ("de 71 emergências,
    # quantas passaram como leves").
    emergencias = int((df["expected"] == "EMERGENCIA").sum())
    nao_emergencias = int((df["expected"] == "NAO_EMERGENCIA").sum())

    bloco["false_non_urgent"] = int(
        len(
            df[
                (df["expected"] == "EMERGENCIA")
                & (df["predicted"] == "NAO_EMERGENCIA")
            ]
        )
    )
    bloco["false_non_urgent_rate"] = _divisao(
        bloco["false_non_urgent"], emergencias
    )

    bloco["false_urgent"] = int(
        len(
            df[
                (df["expected"] == "NAO_EMERGENCIA")
                & (df["predicted"] == "EMERGENCIA")
            ]
        )
    )
    bloco["false_urgent_rate"] = _divisao(
        bloco["false_urgent"], nao_emergencias
    )

    bloco["incerto_rate"] = _divisao(
        int((df["predicted"] == "INCERTO").sum()), total
    )
    bloco["invalid_rate"] = _divisao(
        int((df["predicted"] == "INVALID_JSON").sum()), total
    )
    bloco["other_rate"] = _divisao(
        int((df["predicted"] == "OTHER").sum()), total
    )

    # A reprodução da medição antiga é aproximada: hoje o sistema tenta
    # duas vezes, antes era tiro único. Esta variante recontabiliza as
    # linhas que precisaram de segunda tentativa como inválidas.
    if "attempts" in df.columns and df["attempts"].notna().any():
        tentativas = pd.to_numeric(df["attempts"], errors="coerce").fillna(1)
        primeira = df["expected"] == df["predicted"]
        bloco["accuracy_single_attempt"] = _divisao(
            int((primeira & (tentativas <= 1)).sum()), total
        )

    return bloco


def _estratos(df: pd.DataFrame) -> dict:
    """
    Recorte por origem do dado e por espécie.

    Por origem, só a revocação faz sentido: cada origem contém um único
    rótulo neste conjunto (as emergências são todas originais e as não
    emergências todas sintéticas), então precisão e F1 seriam 0/0 ou
    trivialmente 1. Isso é uma limitação do conjunto, não do cálculo, e
    está registrada na documentação da avaliação.
    """

    estratos: dict[str, Any] = {}

    if "source" in df.columns:
        por_origem = {}

        for origem, grupo in df.groupby("source"):
            rotulos = grupo["expected"].unique().tolist()
            acertos = int((grupo["expected"] == grupo["predicted"]).sum())

            por_origem[str(origem)] = {
                "n": len(grupo),
                "labels": rotulos,
                "recall": _divisao(acertos, len(grupo)),
                "recall_ci95": wilson_ci(acertos, len(grupo)),
                "incerto_rate": _divisao(
                    int((grupo["predicted"] == "INCERTO").sum()), len(grupo)
                ),
                "invalid_rate": _divisao(
                    int((grupo["predicted"] == "INVALID_JSON").sum()),
                    len(grupo),
                ),
                "precision": None,
                "f1": None,
                "note": (
                    "estrato contém um único rótulo; precisão e F1 não se "
                    "aplicam"
                    if len(rotulos) == 1
                    else None
                ),
            }

        estratos["by_source"] = por_origem

    if "animal" in df.columns:
        por_especie = {}

        for especie, grupo in df.groupby("animal"):
            por_especie[str(especie)] = _bloco_de_classificacao(grupo)

        estratos["by_animal"] = por_especie

    return estratos


def _repeticoes(df: pd.DataFrame) -> Optional[dict]:
    """
    Estabilidade entre execuções idênticas.

    Existe porque a etapa de consulta do pipeline usa seed aleatória: o
    mesmo relato pode mudar de classificação entre execuções. Sem medir
    isso, uma diferença entre duas rodadas pode ser só ruído.
    """

    if "repeat" not in df.columns or df["repeat"].nunique() < 2:
        return None

    repeticoes = sorted(df["repeat"].unique())

    por_repeticao = {
        int(k): _bloco_de_classificacao(df[df["repeat"] == k])
        for k in repeticoes
    }

    balanceadas = [
        bloco["balanced_accuracy"]
        for bloco in por_repeticao.values()
        if bloco["balanced_accuracy"] is not None
    ]

    agregado: dict[str, Any] = {}

    if balanceadas:
        media = sum(balanceadas) / len(balanceadas)
        variancia = sum((x - media) ** 2 for x in balanceadas) / len(
            balanceadas
        )
        agregado = {
            "balanced_accuracy_mean": media,
            "balanced_accuracy_sd": math.sqrt(variancia),
            "balanced_accuracy_min": min(balanceadas),
            "balanced_accuracy_max": max(balanceadas),
        }

    # Concordância: em quantas linhas todas as execuções deram o mesmo
    # rótulo. É o número que descreve a instabilidade em uma frase.
    por_linha = df.groupby("row_id")["predicted"]

    concordancia_total = por_linha.nunique()
    linhas_estaveis = int((concordancia_total == 1).sum())

    votos = por_linha.agg(
        lambda serie: serie.value_counts().idxmax()
    )
    esperados = df.groupby("row_id")["expected"].first()

    voto = pd.DataFrame(
        {"predicted": votos, "expected": esperados}
    ).reset_index()

    instaveis = concordancia_total[concordancia_total > 1].index.tolist()

    return {
        "n_repeats": len(repeticoes),
        "per_repeat": por_repeticao,
        "aggregate": agregado,
        "exact_agreement_rate": _divisao(
            linhas_estaveis, len(concordancia_total)
        ),
        "n_unstable_rows": len(instaveis),
        "unstable_row_ids": instaveis,
        "majority_vote": _bloco_de_classificacao(voto),
    }


def compute_metrics(df: pd.DataFrame) -> dict:
    """
    Ponto de entrada. Recebe as previsões de uma rodada e devolve todos os
    números que o relatório e a comparação entre rodadas usam.
    """

    if "status" in df.columns:
        com_erro = int((df["status"] != "ok").sum())
        df = df[df["status"] == "ok"].copy()
    else:
        com_erro = 0

    df = df.copy()

    # Qualquer rótulo fora do vocabulário conhecido vira OTHER e conta como
    # erro, em vez de sumir silenciosamente de todas as contas.
    conhecidos = set(COLUNAS_MATRIZ)
    df["predicted"] = df["predicted"].apply(
        lambda valor: valor if valor in conhecidos else "OTHER"
    )

    com_recuperacao = bool(
        "retrieval_returned" in df.columns
        and pd.to_numeric(
            df["retrieval_returned"], errors="coerce"
        ).fillna(0).gt(0).any()
    )

    # Com repetições, as métricas gerais descrevem a primeira execução; o
    # resto está no bloco de repetições. Misturar as execuções numa conta só
    # trataria a mesma linha como observações independentes.
    if "repeat" in df.columns and df["repeat"].nunique() > 1:
        principal = df[df["repeat"] == df["repeat"].min()]
    else:
        principal = df

    metricas = {
        "rows_evaluated": len(principal),
        "rows_with_error": com_erro,
        "classification": _bloco_de_classificacao(principal),
        "baselines": _baselines(principal),
        "strata": _estratos(principal),
        "latency": _latencia(principal),
        "grounding": _ancoragem(principal, com_recuperacao),
        "repeats": _repeticoes(df),
    }

    return metricas
