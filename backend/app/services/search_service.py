from app.schemas.search import SearchResponse


class SearchService:

    @staticmethod
    def search_documents(question: str) -> SearchResponse:

        return SearchResponse(
            documents=[
                f"Documento relacionado: {question}"
            ]
        )