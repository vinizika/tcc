from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from app.core.logger import setup_logger


logger = setup_logger("ChromaDB")


class ChromaDBClient:

    _backend_directory = Path(__file__).resolve().parents[2]
    _chroma_directory = _backend_directory / "data" / "chroma"

    _chroma_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    _embedding_function = (
        embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
    )

    _client = chromadb.PersistentClient(
        path=str(_chroma_directory)
    )

    _collection = _client.get_or_create_collection(
        name="veterinary_documents",
        embedding_function=_embedding_function,
        metadata={
            "description": (
                "Documentos usados pelo sistema RAG veterinário"
            )
        },
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        }
    )

    @staticmethod
    def get_collection():
        return ChromaDBClient._collection