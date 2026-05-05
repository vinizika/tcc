from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_PATH = PROJECT_ROOT / "data" / "evaluation" / "accuracy_results.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "evaluation" / "confusion_matrix.csv"

LABELS = [
    "EMERGENCIA",
    "NAO_EMERGENCIA",
    "INCERTO",
    "INVALID_JSON",
]


def calculate_precision_recall_f1(df, label):
    true_positive = len(
        df[
            (df["expected"] == label)
            & (df["predicted"] == label)
        ]
    )

    false_positive = len(
        df[
            (df["expected"] != label)
            & (df["predicted"] == label)
        ]
    )

    false_negative = len(
        df[
            (df["expected"] == label)
            & (df["predicted"] != label)
        ]
    )

    if true_positive + false_positive == 0:
        precision = 0
    else:
        precision = true_positive / (true_positive + false_positive)

    if true_positive + false_negative == 0:
        recall = 0
    else:
        recall = true_positive / (true_positive + false_negative)

    if precision + recall == 0:
        f1_score = 0
    else:
        f1_score = 2 * precision * recall / (precision + recall)

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
    }


def main():
    df = pd.read_csv(RESULTS_PATH)

    df["expected"] = df["expected"].astype(str).str.strip().str.upper()
    df["predicted"] = df["predicted"].astype(str).str.strip().str.upper()

    confusion_matrix = pd.crosstab(
        df["expected"],
        df["predicted"],
        rownames=["real"],
        colnames=["previsto"],
        dropna=False,
    )

    for label in LABELS:
        if label not in confusion_matrix.columns:
            confusion_matrix[label] = 0

    confusion_matrix = confusion_matrix.reindex(
        index=["EMERGENCIA", "NAO_EMERGENCIA"],
        columns=LABELS,
        fill_value=0,
    )

    confusion_matrix.to_csv(OUTPUT_PATH)

    total = len(df)

    emergencia_real = len(df[df["expected"] == "EMERGENCIA"])
    nao_emergencia_real = len(df[df["expected"] == "NAO_EMERGENCIA"])

    acertos_emergencia = len(
        df[
            (df["expected"] == "EMERGENCIA")
            & (df["predicted"] == "EMERGENCIA")
        ]
    )

    acertos_nao_emergencia = len(
        df[
            (df["expected"] == "NAO_EMERGENCIA")
            & (df["predicted"] == "NAO_EMERGENCIA")
        ]
    )

    falsos_nao_urgentes = len(
        df[
            (df["expected"] == "EMERGENCIA")
            & (df["predicted"] == "NAO_EMERGENCIA")
        ]
    )

    falsos_urgentes = len(
        df[
            (df["expected"] == "NAO_EMERGENCIA")
            & (df["predicted"] == "EMERGENCIA")
        ]
    )

    casos_incertos = len(df[df["predicted"] == "INCERTO"])
    json_invalidos = len(df[df["predicted"] == "INVALID_JSON"])

    metricas_emergencia = calculate_precision_recall_f1(df, "EMERGENCIA")
    metricas_nao_emergencia = calculate_precision_recall_f1(df, "NAO_EMERGENCIA")

    print("Matriz de confusão")
    print()
    print(confusion_matrix)
    print()

    print("Resumo")
    print(f"total_avaliado: {total}")
    print(f"emergencia_real: {emergencia_real}")
    print(f"nao_emergencia_real: {nao_emergencia_real}")
    print(f"acertos_emergencia: {acertos_emergencia}")
    print(f"acertos_nao_emergencia: {acertos_nao_emergencia}")
    print(f"falsos_nao_urgentes: {falsos_nao_urgentes}")
    print(f"falsos_urgentes: {falsos_urgentes}")
    print(f"casos_incertos: {casos_incertos}")
    print(f"json_invalidos: {json_invalidos}")
    print()

    print("Métricas da classe EMERGENCIA")
    print(f"true_positive: {metricas_emergencia['true_positive']}")
    print(f"false_positive: {metricas_emergencia['false_positive']}")
    print(f"false_negative: {metricas_emergencia['false_negative']}")
    print(f"precision: {metricas_emergencia['precision']:.4f}")
    print(f"precision_percentual: {metricas_emergencia['precision'] * 100:.2f}%")
    print(f"recall: {metricas_emergencia['recall']:.4f}")
    print(f"recall_percentual: {metricas_emergencia['recall'] * 100:.2f}%")
    print(f"f1_score: {metricas_emergencia['f1_score']:.4f}")
    print(f"f1_score_percentual: {metricas_emergencia['f1_score'] * 100:.2f}%")
    print()

    print("Métricas da classe NAO_EMERGENCIA")
    print(f"true_positive: {metricas_nao_emergencia['true_positive']}")
    print(f"false_positive: {metricas_nao_emergencia['false_positive']}")
    print(f"false_negative: {metricas_nao_emergencia['false_negative']}")
    print(f"precision: {metricas_nao_emergencia['precision']:.4f}")
    print(f"precision_percentual: {metricas_nao_emergencia['precision'] * 100:.2f}%")
    print(f"recall: {metricas_nao_emergencia['recall']:.4f}")
    print(f"recall_percentual: {metricas_nao_emergencia['recall'] * 100:.2f}%")
    print(f"f1_score: {metricas_nao_emergencia['f1_score']:.4f}")
    print(f"f1_score_percentual: {metricas_nao_emergencia['f1_score'] * 100:.2f}%")
    print()

    print(f"arquivo_matriz_confusao: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()