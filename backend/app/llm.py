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

Responda obrigatoriamente em JSON válido.
Não escreva nada antes ou depois do JSON.

O JSON deve ter exatamente estes campos:
- classificacao
- justificativa
- sinais_de_alerta
- recomendacao

A classificação deve ser exatamente uma destas opções:
- EMERGENCIA
- NAO_EMERGENCIA
- INCERTO

Não use acentos nos nomes dos campos.
Não use "recomendação". Use "recomendacao".
Não use "NAO EMERGENCIA". Use "NAO_EMERGENCIA".

Dados do caso:
Espécie: {especie or "não informado"}
Idade: {idade or "não informado"}
Relato do tutor: {relato}
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
            "format": "json",
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["message"]["content"]