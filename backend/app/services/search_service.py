from app.clients.retrieval_client import RetrievalClient
from app.schemas.search import SearchResponse


class SearchService:

    @staticmethod
    def search(question: str) -> SearchResponse:

        retrieved_documents = RetrievalClient.retrieve(
            [question]
        )

        return SearchResponse(
            documents=[
                document.content
                for document in retrieved_documents
            ]
        )