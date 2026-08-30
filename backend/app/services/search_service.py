from app.clients.retrieval_client import RetrievalClient
from app.schemas.search import (
    SearchDocument,
    SearchResponse,
)


class SearchService:

    @staticmethod
    def search(question: str) -> SearchResponse:

        retrieved_documents = RetrievalClient.retrieve(
            [question]
        )

        return SearchResponse(
            documents=[
                SearchDocument(
                    id=document.id,
                    title=document.title,
                    content=document.content,
                    source=document.source,
                    score=round(document.score, 4),
                )
                for document in retrieved_documents
            ]
        )