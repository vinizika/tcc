from app.clients.retrieval_client import RetrievalClient
from app.clients.reranker_client import RerankerClient
from app.schemas.search import (
    SearchDocument,
    SearchResponse,
)


class SearchService:

    @staticmethod
    def search(question: str) -> SearchResponse:

        retrieved_documents = RetrievalClient.retrieve(
            [question],
            routing_query=question,
        )
        retrieved_documents = RerankerClient.rerank(
            [question],
            retrieved_documents,
            eligibility_query=question,
        )

        return SearchResponse(
            documents=[
                SearchDocument(
                    id=document.id,
                    title=document.title,
                    content=document.content,
                    source=document.source,
                    score=round(document.score, 4),
                    ranking_score=(
                        round(document.ranking_score, 4)
                        if document.ranking_score is not None
                        else None
                    ),
                    topic=document.topic,
                    source_file=document.source_file,
                )
                for document in retrieved_documents
            ]
        )
