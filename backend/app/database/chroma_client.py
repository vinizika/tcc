import chromadb
from chromadb.utils import embedding_functions

from app.core.logger import setup_logger


logger = setup_logger("ChromaDB")


class ChromaDBClient:

    _client = chromadb.PersistentClient(
        path="/app/data/chroma"
    )

    _embedding_function = (
        embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    )

    _collection = _client.get_or_create_collection(
        name="veterinary_documents",
        embedding_function=_embedding_function
    )

    @staticmethod
    def get_collection():
        return ChromaDBClient._collection