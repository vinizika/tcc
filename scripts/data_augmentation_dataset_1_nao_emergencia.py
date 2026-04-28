from pathlib import Path
from itertools import combinations

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

DATASET1_CLEAN_PATH = PROCESSED_DIR / "dataset1_clean.csv"

SYNTHETIC_OUTPUT_PATH = PROCESSED_DIR / "dataset1_synthetic_no_cases.csv"
AUGMENTED_OUTPUT_PATH = PROCESSED_DIR / "dataset1_augmented.csv"

FOCUS_ANIMALS = ["Dog", "Cat"]

ALLOWED_SYMPTOMS = [
    "Eye Discharge",
    "Nasal Discharge",
    "Skin Lesions",
    "Sneezing",
    "Lameness",
]

SYMPTOM_COLUMNS = [
    "symptoms1",
    "symptoms2",
    "symptoms3",
    "symptoms4",
    "symptoms5",
]


def create_signature(animal, symptoms):
    valid_symptoms = [symptom for symptom in symptoms if symptom != ""]
    ordered_symptoms = sorted(valid_symptoms)
    return f"{animal} | {' | '.join(ordered_symptoms)}"


def create_synthetic_row(animal, symptoms):
    symptoms = list(symptoms)
    symptoms = symptoms + [""] * (5 - len(symptoms))

    return {
        "AnimalName": animal,
        "symptoms1": symptoms[0],
        "symptoms2": symptoms[1],
        "symptoms3": symptoms[2],
        "symptoms4": symptoms[3],
        "symptoms5": symptoms[4],
        "Dangerous": "No",
        "Source": "llm_data_augmentation",
    }


def main():
    df = pd.read_csv(DATASET1_CLEAN_PATH)

    if "Source" not in df.columns:
        df["Source"] = "original"

    existing_signatures = set()

    for _, row in df.iterrows():
        animal = row["AnimalName"]

        symptoms = []

        for column in SYMPTOM_COLUMNS:
            value = row[column]

            if pd.notna(value) and str(value).strip() != "":
                symptoms.append(str(value).strip())

        signature = create_signature(animal, symptoms)
        existing_signatures.add(signature)

    synthetic_rows = []
    skipped_rows = 0

    for animal in FOCUS_ANIMALS:
        for combination_size in [3, 4, 5]:
            for symptom_combination in combinations(ALLOWED_SYMPTOMS, combination_size):
                signature = create_signature(animal, symptom_combination)

                if signature in existing_signatures:
                    skipped_rows += 1
                    continue

                synthetic_row = create_synthetic_row(animal, symptom_combination)
                synthetic_rows.append(synthetic_row)

    synthetic_df = pd.DataFrame(synthetic_rows)

    augmented_df = pd.concat([df, synthetic_df], ignore_index=True)

    synthetic_df.to_csv(SYNTHETIC_OUTPUT_PATH, index=False)
    augmented_df.to_csv(AUGMENTED_OUTPUT_PATH, index=False)

    print("Data augmentation concluído.")
    print(f"animais_utilizados: {FOCUS_ANIMALS}")
    print(f"sintomas_permitidos: {ALLOWED_SYMPTOMS}")
    print(f"linhas_originais: {len(df)}")
    print(f"linhas_sinteticas_geradas: {len(synthetic_df)}")
    print(f"linhas_sinteticas_ignoradas_por_duplicidade: {skipped_rows}")
    print(f"linhas_dataset_final: {len(augmented_df)}")
    print(f"distribuicao_dangerous_final: {augmented_df['Dangerous'].value_counts().to_dict()}")
    print(f"distribuicao_source_final: {augmented_df['Source'].value_counts().to_dict()}")
    print(f"arquivo_sintetico: {SYNTHETIC_OUTPUT_PATH}")
    print(f"arquivo_final_aumentado: {AUGMENTED_OUTPUT_PATH}")


if __name__ == "__main__":
    main()