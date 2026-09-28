from app.clients.retrieval_client import RetrievalClient
from app.clients.reranker_client import RerankerClient
from app.core.config import settings
from app.schemas.search import (
    SearchDocument,
    SearchResponse,
)


class SearchService:

    @staticmethod
    def search(question: str, mode: str | None = None) -> SearchResponse:
        """Busca pura, sem a etapa de consulta e sem o corte de relevância.

        Obedece ao mesmo `retrieval_mode` do pipeline, para a régua medir a
        busca que o sistema usa.
        """

        mode = mode or settings.RETRIEVAL_MODE

        if mode == "vector":
            retrieved_documents = sorted(
                RetrievalClient.retrieve([question], routing_query=None),
                key=lambda document: document.score,
                reverse=True,
            )
        else:
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
