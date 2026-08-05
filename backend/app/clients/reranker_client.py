from app.models.retrieved_document import RetrievedDocument
from app.core.logger import setup_logger

logger = setup_logger("RerankerClient")


class RerankerClient:

    @staticmethod
    def rerank(
        documents: list[RetrievedDocument]
    ) -> list[RetrievedDocument]:

        logger.info("Executando Re-ranking")

        return sorted(
            documents,
            key=lambda doc: doc.score,
            reverse=True
        )