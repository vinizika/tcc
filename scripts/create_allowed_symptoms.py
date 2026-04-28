from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_PATH = PROCESSED_DIR / "allowed_symptoms_for_synthetic_no.csv"


ALLOWED_SYMPTOMS = [
    "Eye Discharge",
    "Nasal Discharge",
    "Skin Lesions",
    "Sneezing",
    "Lameness",
]


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame({
        "symptom": ALLOWED_SYMPTOMS,
        "allowed_for_synthetic_no": ["Yes"] * len(ALLOWED_SYMPTOMS),
        "reason": [
            "Sintoma considerado leve para geração controlada de casos não urgentes",
            "Sintoma considerado leve para geração controlada de casos não urgentes",
            "Sintoma considerado leve para geração controlada de casos não urgentes",
            "Sintoma considerado leve para geração controlada de casos não urgentes",
            "Sintoma aceito para geração controlada, considerando ausência de sinais críticos associados",
        ],
    })

    df.to_csv(OUTPUT_PATH, index=False)

    print("Arquivo de sintomas permitidos criado.")
    print(f"arquivo_saida: {OUTPUT_PATH}")
    print(f"quantidade_sintomas_permitidos: {len(df)}")
    print(f"sintomas_permitidos: {df['symptom'].tolist()}")


if __name__ == "__main__":
    main()