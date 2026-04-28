from pathlib import Path
import json

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

DATASET1_CLEAN_PATH = PROCESSED_DIR / "dataset1_clean.csv"
SYNTHETIC_INPUT_PATH = PROCESSED_DIR / "dataset1_synthetic_no_cases.csv"

APPROVED_SYNTHETIC_OUTPUT_PATH = PROCESSED_DIR / "dataset1_synthetic_no_cases_llm_approved.csv"
FINAL_OUTPUT_PATH = PROCESSED_DIR / "dataset1_augmented_llm_validated.csv"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:3b"

SYMPTOM_COLUMNS = [
    "symptoms1",
    "symptoms2",
    "symptoms3",
    "symptoms4",
    "symptoms5",
]


def get_symptoms_from_row(row):
    symptoms = []

    for column in SYMPTOM_COLUMNS:
        value = row[column]

        if pd.notna(value) and str(value).strip() != "":
            symptoms.append(str(value).strip())

    return symptoms


def validate_with_llm(animal, symptoms):
    prompt = f"""
Você é um avaliador de dados sintéticos para um dataset de triagem veterinária.

Sua tarefa é decidir se a combinação abaixo pode ser usada como um exemplo sintético de NÃO EMERGÊNCIA.

Animal:
{animal}

Sintomas:
{", ".join(symptoms)}

Regras:
- Aprove apenas combinações leves e plausíveis para casos não urgentes.
- Rejeite se a combinação sugerir risco clínico importante.
- Rejeite se houver sinais de emergência, sofrimento intenso ou instabilidade.
- Não faça diagnóstico.
- Responda apenas em JSON válido.

Formato obrigatório:
{{
  "decision": "APPROVED"
}}

Ou:

{{
  "decision": "REJECTED"
}}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )

    response.raise_for_status()

    content = response.json()["message"]["content"]
    result = json.loads(content)

    return result["decision"]


def main():
    original_df = pd.read_csv(DATASET1_CLEAN_PATH)
    synthetic_df = pd.read_csv(SYNTHETIC_INPUT_PATH)

    approved_rows = []
    rejected_count = 0

    print("Iniciando validação das linhas sintéticas com LLM...")
    print(f"modelo_utilizado: {MODEL_NAME}")
    print(f"linhas_sinteticas_para_validar: {len(synthetic_df)}")
    print()

    for index, row in synthetic_df.iterrows():
        animal = row["AnimalName"]
        symptoms = get_symptoms_from_row(row)

        decision = validate_with_llm(animal, symptoms)

        print(f"linha: {index + 1}")
        print(f"animal: {animal}")
        print(f"sintomas: {symptoms}")
        print(f"decisao_llm: {decision}")
        print()

        if decision == "APPROVED":
            approved_rows.append(row)
        else:
            rejected_count += 1

    approved_synthetic_df = pd.DataFrame(approved_rows)

    final_df = pd.concat(
        [original_df, approved_synthetic_df],
        ignore_index=True,
    )

    approved_synthetic_df.to_csv(APPROVED_SYNTHETIC_OUTPUT_PATH, index=False)
    final_df.to_csv(FINAL_OUTPUT_PATH, index=False)

    print("Validação concluída.")
    print(f"linhas_originais: {len(original_df)}")
    print(f"linhas_sinteticas_avaliadas: {len(synthetic_df)}")
    print(f"linhas_sinteticas_aprovadas: {len(approved_synthetic_df)}")
    print(f"linhas_sinteticas_rejeitadas: {rejected_count}")
    print(f"linhas_dataset_final: {len(final_df)}")
    print(f"distribuicao_dangerous_final: {final_df['Dangerous'].value_counts().to_dict()}")
    print(f"distribuicao_source_final: {final_df['Source'].value_counts().to_dict()}")
    print(f"arquivo_sintetico_aprovado: {APPROVED_SYNTHETIC_OUTPUT_PATH}")
    print(f"arquivo_final_validado: {FINAL_OUTPUT_PATH}")


if __name__ == "__main__":
    main()