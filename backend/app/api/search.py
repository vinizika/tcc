from fastapi import APIRouter

from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.post("/", response_model=SearchResponse)
def search_documents(request: SearchRequest):

    return SearchService.search(request.question)