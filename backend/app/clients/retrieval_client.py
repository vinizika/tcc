from app.models.retrieved_document import RetrievedDocument


class RetrievalClient:

    @staticmethod
    def retrieve(queries: list[str]) -> list[RetrievedDocument]:

        return [
            RetrievedDocument(
                title="Intoxicação",
                content="O tratamento depende da substância ingerida.",
                score=0.95
            )
        ]