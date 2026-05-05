from pathlib import Path
import json

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "dataset1_augmented_llm_validated.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "evaluation"
OUTPUT_PATH = OUTPUT_DIR / "accuracy_results.csv"

API_URL = "http://localhost:8000/triagem"

FOCUS_ANIMALS = ["Dog", "Cat"]

SYMPTOM_COLUMNS = [
    "symptoms1",
    "symptoms2",
    "symptoms3",
    "symptoms4",
    "symptoms5",
]


def get_expected_label(dangerous):
    if dangerous == "Yes":
        return "EMERGENCIA"

    if dangerous == "No":
        return "NAO_EMERGENCIA"

    return "INVALID_LABEL"


def get_symptoms(row):
    symptoms = []

    for column in SYMPTOM_COLUMNS:
        value = row[column]

        if pd.notna(value) and str(value).strip() != "":
            symptoms.append(str(value).strip())

    return symptoms


def build_relato(row):
    animal = row["AnimalName"]
    symptoms = get_symptoms(row)

    return f"Animal: {animal}. Sintomas observados: {', '.join(symptoms)}."


def predict_classification(relato):
    response = requests.post(
        API_URL,
        json={
            "relato": relato,
            "especie": None,
            "idade": None,
        },
        timeout=120,
    )

    response.raise_for_status()

    resposta_modelo = response.json()["resposta_modelo"]

    try:
        resposta_json = json.loads(resposta_modelo)
        predicted = resposta_json["classificacao"].strip().upper()
        json_valid = True
    except Exception:
        predicted = "INVALID_JSON"
        json_valid = False

    return predicted, json_valid, resposta_modelo


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATASET_PATH)

    df = df[df["AnimalName"].isin(FOCUS_ANIMALS)].copy()

    results = []

    print("Iniciando avaliação de acurácia...")
    print(f"dataset: {DATASET_PATH}")
    print(f"animais_avaliados: {FOCUS_ANIMALS}")
    print(f"total_linhas_filtradas: {len(df)}")
    print(f"distribuicao_dangerous_filtrada: {df['Dangerous'].value_counts().to_dict()}")
    print(f"distribuicao_source_filtrada: {df['Source'].value_counts().to_dict()}")
    print()

    for index, row in df.iterrows():
        expected = get_expected_label(row["Dangerous"])
        relato = build_relato(row)

        predicted, json_valid, raw_response = predict_classification(relato)

        correct = expected == predicted

        results.append({
            "index": index,
            "animal": row["AnimalName"],
            "relato": relato,
            "expected": expected,
            "predicted": predicted,
            "correct": correct,
            "json_valid": json_valid,
            "source": row["Source"],
            "raw_response": raw_response,
        })

        print(f"linha_dataset: {index}")
        print(f"animal: {row['AnimalName']}")
        print(f"esperado: {expected}")
        print(f"previsto: {predicted}")
        print(f"json_valido: {json_valid}")
        print(f"acertou: {correct}")
        print()

    results_df = pd.DataFrame(results)

    total = len(results_df)
    correct_count = int(results_df["correct"].sum())
    invalid_json_count = int((results_df["json_valid"] == False).sum())

    accuracy = correct_count / total

    results_df.to_csv(OUTPUT_PATH, index=False)

    print("Avaliação concluída.")
    print(f"total_avaliado: {total}")
    print(f"total_acertos: {correct_count}")
    print(f"total_erros: {total - correct_count}")
    print(f"json_invalidos: {invalid_json_count}")
    print(f"acuracia: {accuracy:.4f}")
    print(f"acuracia_percentual: {accuracy * 100:.2f}%")
    print(f"arquivo_resultados: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()