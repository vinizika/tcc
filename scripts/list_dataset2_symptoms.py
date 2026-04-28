from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET2_CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "dataset2_clean.csv"

FOCUS_ANIMALS = ["Dog", "Cat"]

TEXT_SYMPTOM_COLUMNS = [
    "Symptom_1",
    "Symptom_2",
    "Symptom_3",
    "Symptom_4",
]

BINARY_SYMPTOM_COLUMNS = [
    "Appetite_Loss",
    "Vomiting",
    "Diarrhea",
    "Coughing",
    "Labored_Breathing",
    "Lameness",
    "Skin_Lesions",
    "Nasal_Discharge",
    "Eye_Discharge",
]


def format_binary_symptom(column_name):
    return column_name.replace("_", " ").title()


def main():
    df = pd.read_csv(DATASET2_CLEAN_PATH)

    df = df[df["Animal_Type"].isin(FOCUS_ANIMALS)].copy()

    symptoms = set()

    for column in TEXT_SYMPTOM_COLUMNS:
        for symptom in df[column].dropna():
            symptom = str(symptom).strip()

            if symptom != "":
                symptoms.add(symptom)

    for column in BINARY_SYMPTOM_COLUMNS:
        positive_rows = df[df[column] == "Yes"]

        if len(positive_rows) > 0:
            symptoms.add(format_binary_symptom(column))

    symptoms = sorted(symptoms)

    print("=== Sintomas encontrados no Dataset 2 ===")
    print(f"animais_filtrados: {FOCUS_ANIMALS}")
    print(f"quantidade_sintomas: {len(symptoms)}")
    print()

    for symptom in symptoms:
        print(f"- {symptom}")


if __name__ == "__main__":
    main()