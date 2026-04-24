import os
import requests


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")


def chamar_llm_triagem(relato: str, especie: str | None = None, idade: str | None = None) -> str:
    prompt = f"""
Você é um assistente de apoio à triagem veterinária.

Sua tarefa não é diagnosticar.
Sua tarefa é analisar o relato do tutor e classificar o caso como:
- EMERGENCIA
- NAO_EMERGENCIA
- INCERTO

Responda de forma objetiva, cuidadosa e sem inventar informações clínicas.

Dados do caso:
Espécie: {especie or "não informado"}
Idade: {idade or "não informado"}
Relato do tutor: {relato}

Responda em JSON com os campos:
classificacao, justificativa, sinais_de_alerta, recomendacao.
"""

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": LLM_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    return data["message"]["content"]