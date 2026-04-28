from pathlib import Path
import unicodedata

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

DATASET1_PATH = DATA_DIR / "dataset1.csv"
DATASET1_RAW_PATH = DATA_DIR / "dataset1_raw.csv"
DATASET2_PATH = DATA_DIR / "dataset2.csv"

DATASET1_CLEAN_PATH = PROCESSED_DIR / "dataset1_clean.csv"
DATASET2_CLEAN_PATH = PROCESSED_DIR / "dataset2_clean.csv"
SYMPTOM_VOCABULARY_PATH = PROCESSED_DIR / "symptom_vocabulary_dataset2.csv"


ANIMAL_MAPPING = {
    "dog": "Dog",
    "dogs": "Dog",
    "cat": "Cat",
    "cats": "Cat",
    "cattle": "Cattle",
    "cow": "Cattle",
    "cows": "Cattle",
    "buffalo": "Buffalo",
    "buffaloes": "Buffalo",
    "chicken": "Chicken",
    "chickens": "Chicken",
    "monkey": "Monkey",
    "monkeys": "Monkey",
    "goat": "Goat",
    "goats": "Goat",
    "sheep": "Sheep",
    "horse": "Horse",
    "horses": "Horse",
    "pigs": "Pig",
    "pig": "Pig",
}


SYMPTOM_MAPPING = {
    "fevereira": "Fever",
    "fever": "Fever",
    "high temperature": "Fever",

    "diarrhoea": "Diarrhea",
    "diarrhea": "Diarrhea",

    "vomitting": "Vomiting",
    "vomiting": "Vomiting",

    "caughing": "Coughing",
    "coughing": "Coughing",

    "breating": "Breathing Difficulty",
    "breathing difficulty": "Breathing Difficulty",
    "difficulty breathing": "Breathing Difficulty",
    "labored breathing": "Labored Breathing",

    "loss of appetite": "Appetite Loss",
    "appetite loss": "Appetite Loss",
    "lack of appetite": "Appetite Loss",
    "anorexia": "Appetite Loss",

    "tiredness": "Tiredness",
    "lethargy": "Lethargy",

    "dehydration": "Dehydration",

    "weight loss": "Weight Loss",

    "pains": "Pain",
    "pain": "Pain",

    "swellimg": "Swelling",
    "swelling": "Swelling",

    "temperarure": "Temperature Abnormality",
    "temperature": "Temperature Abnormality",

    "moratality": "Mortality",
    "mortality": "Mortality",

    "nasal discharge": "Nasal Discharge",
    "eye discharge": "Eye Discharge",
    "skin lesions": "Skin Lesions",
    "lameness": "Lameness",
}


DATASET1_SYMPTOM_COLUMNS = [
    "symptoms1",
    "symptoms2",
    "symptoms3",
    "symptoms4",
    "symptoms5",
]


DATASET2_TEXT_SYMPTOM_COLUMNS = [
    "Symptom_1",
    "Symptom_2",
    "Symptom_3",
    "Symptom_4",
]


DATASET2_BINARY_SYMPTOM_COLUMNS = [
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


def normalize_text(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))

    value = value.replace("_", " ")
    value = value.replace("-", " ")
    value = " ".join(value.split())

    return value


def normalize_animal(value):
    value = normalize_text(value).lower()

    if value == "":
        return ""

    return ANIMAL_MAPPING.get(value, value.title())


def normalize_symptom(value):
    value = normalize_text(value).lower()

    if value == "":
        return ""

    return SYMPTOM_MAPPING.get(value, value.title())


def normalize_yes_no(value):
    value = normalize_text(value).lower()

    if value in ["yes", "y", "sim", "true", "1"]:
        return "Yes"

    if value in ["no", "n", "nao", "não", "false", "0"]:
        return "No"

    return ""


def clean_dataset1():
    df_raw = pd.read_csv(DATASET1_RAW_PATH)
    df = pd.read_csv(DATASET1_PATH)

    rows_before = len(df)

    df = df[
        [
            "AnimalName",
            "symptoms1",
            "symptoms2",
            "symptoms3",
            "symptoms4",
            "symptoms5",
            "Dangerous",
        ]
    ].copy()

    df["AnimalName"] = df["AnimalName"].apply(normalize_animal)

    for column in DATASET1_SYMPTOM_COLUMNS:
        df[column] = df[column].apply(normalize_symptom)

    df["Dangerous"] = df["Dangerous"].apply(normalize_yes_no)

    rows_without_label = len(df[df["Dangerous"] == ""])

    df = df[df["Dangerous"] != ""].copy()

    df["symptom_signature"] = df[DATASET1_SYMPTOM_COLUMNS].apply(
        lambda row: " | ".join(sorted([symptom for symptom in row if symptom != ""])),
        axis=1,
    )

    rows_before_duplicates = len(df)

    df = df.drop_duplicates(
        subset=["AnimalName", "symptom_signature", "Dangerous"]
    ).copy()

    duplicates_removed = rows_before_duplicates - len(df)

    df["Source"] = "original"

    df = df.drop(columns=["symptom_signature"])
    rows_after = len(df)
    df.to_csv(DATASET1_CLEAN_PATH, index=False)

    print("=== Dataset 1 ===")
    print(f"linhas_dataset1_raw: {len(df_raw)}")
    print(f"linhas_antes_limpeza: {rows_before}")
    print(f"linhas_sem_rotulo_removidas: {rows_without_label}")
    print(f"duplicatas_removidas: {duplicates_removed}")
    print(f"linhas_depois_limpeza: {rows_after}")
    print(f"distribuicao_dangerous_depois: {df['Dangerous'].value_counts().to_dict()}")
    print(f"animais_depois_limpeza: {df['AnimalName'].value_counts().to_dict()}")
    print()

    return df


def clean_dataset2():
    df = pd.read_csv(DATASET2_PATH)

    rows_before = len(df)

    df["Animal_Type"] = df["Animal_Type"].apply(normalize_animal)

    for column in DATASET2_TEXT_SYMPTOM_COLUMNS:
        df[column] = df[column].apply(normalize_symptom)

    for column in DATASET2_BINARY_SYMPTOM_COLUMNS:
        df[column] = df[column].apply(normalize_yes_no)

    df["Breed"] = df["Breed"].apply(normalize_text)
    df["Gender"] = df["Gender"].apply(normalize_text)
    df["Duration"] = df["Duration"].apply(normalize_text)
    df["Disease_Prediction"] = df["Disease_Prediction"].apply(normalize_text)

    rows_before_duplicates = len(df)
    df = df.drop_duplicates().copy()
    duplicates_removed = rows_before_duplicates - len(df)

    rows_after = len(df)

    df.to_csv(DATASET2_CLEAN_PATH, index=False)

    vocabulary_rows = []

    for column in DATASET2_TEXT_SYMPTOM_COLUMNS:
        for symptom in df[column]:
            if symptom != "":
                vocabulary_rows.append(
                    {
                        "symptom": symptom,
                        "source_column": column,
                    }
                )

    for column in DATASET2_BINARY_SYMPTOM_COLUMNS:
        symptom_name = normalize_symptom(column)

        positive_rows = df[df[column] == "Yes"]

        for _ in range(len(positive_rows)):
            vocabulary_rows.append(
                {
                    "symptom": symptom_name,
                    "source_column": column,
                }
            )

    vocabulary_df = pd.DataFrame(vocabulary_rows)

    symptom_vocabulary = (
        vocabulary_df
        .groupby("symptom")
        .agg(
            count=("symptom", "count"),
            source_columns=("source_column", lambda values: ", ".join(sorted(set(values))))
        )
        .reset_index()
        .sort_values(by=["count", "symptom"], ascending=[False, True])
    )

    symptom_vocabulary.to_csv(SYMPTOM_VOCABULARY_PATH, index=False)

    print("=== Dataset 2 ===")
    print(f"linhas_antes_limpeza: {rows_before}")
    print(f"duplicatas_removidas: {duplicates_removed}")
    print(f"linhas_depois_limpeza: {rows_after}")
    print(f"animais_depois_limpeza: {df['Animal_Type'].value_counts().to_dict()}")
    print(f"quantidade_doencas_distintas: {df['Disease_Prediction'].nunique()}")
    print(f"quantidade_sintomas_vocabulario: {len(symptom_vocabulary)}")
    print(f"top_10_sintomas: {symptom_vocabulary.head(10).to_dict(orient='records')}")
    print()

    return df, symptom_vocabulary


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Iniciando limpeza dos datasets...")
    print()

    clean_dataset1()
    clean_dataset2()

    print("Limpeza concluída.")
    print(f"dataset1_limpo: {DATASET1_CLEAN_PATH}")
    print(f"dataset2_limpo: {DATASET2_CLEAN_PATH}")
    print(f"vocabulario_sintomas: {SYMPTOM_VOCABULARY_PATH}")


if __name__ == "__main__":
    main()