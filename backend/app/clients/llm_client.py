import requests

from app.models.retrieved_document import RetrievedDocument
from app.core.logger import setup_logger


logger = setup_logger("LLMClient")


OLLAMA_URL = "http://ollama:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"


class LLMClient:

    @staticmethod
    def generate(
        question: str,
        documents: list[RetrievedDocument]
    ) -> str:

        logger.info("Gerando resposta (simulada)")

        contexto = "\n".join(
            doc.content for doc in documents
        )

        return f"""
Pergunta:

{question}

Resposta baseada nos documentos:

{contexto}

Recomendação:
Procure atendimento veterinário o mais rápido possível.
"""

    @staticmethod
    def generate_queries(question: str) -> list[str]:

        logger.info("Gerando Multi-Query com Ollama")

        prompt = f"""
Você é um assistente especializado em pesquisa veterinária.

Sua tarefa é gerar 3 consultas diferentes para buscar informações
relevantes em uma base de conhecimento veterinária.

Pergunta original:
{question}

Gere exatamente 3 consultas.

Cada consulta deve abordar a pergunta por uma perspectiva diferente,
mas continuar relacionada ao problema original.

Não responda à pergunta.
Não explique as consultas.
Retorne apenas uma consulta por linha.
"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Você gera consultas para sistemas de recuperação de informação."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        content = response.json()["message"]["content"]

        queries = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        queries = queries[:3]

        logger.info(f"Consultas geradas pelo Ollama: {queries}")

        return queries

    @staticmethod
    def self_correct(answer: str) -> str:

        logger.info("Executando Self Correction")

        return answer