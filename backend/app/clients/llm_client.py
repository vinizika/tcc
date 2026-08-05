from app.models.retrieved_document import RetrievedDocument
from app.core.logger import setup_logger

logger = setup_logger("LLMClient")


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
    def self_correct(answer: str) -> str:

        logger.info("Executando Self Correction")

        return answer