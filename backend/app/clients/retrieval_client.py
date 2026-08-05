from app.models.retrieved_document import RetrievedDocument
from app.core.logger import setup_logger

logger = setup_logger("RetrievalClient")


class RetrievalClient:

    @staticmethod
    def retrieve(queries: list[str]):

        logger.info("Consultando banco vetorial (simulado)")

        return [

            RetrievedDocument(

                id="doc_001",

                chunk_id="chunk_001",

                title="Intoxicação por chocolate",

                content=(
                    "A ingestão de chocolate pode causar intoxicação "
                    "em cães devido à presença de teobromina."
                ),

                source="Manual Veterinário",

                score=0.95

            )

        ]