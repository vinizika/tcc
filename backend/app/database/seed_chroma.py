from app.database.chroma_client import ChromaDBClient
from app.core.logger import setup_logger


logger = setup_logger("SeedChroma")


documents = [
    {
        "id": "doc_001",
        "title": "Intoxicação por chocolate",
        "content": (
            "A ingestão de chocolate pode causar intoxicação "
            "em cães devido à presença de teobromina e cafeína. "
            "A gravidade depende da quantidade ingerida, do tipo "
            "de chocolate e do peso do animal."
        ),
        "source": "Manual Veterinário",
    },
    {
        "id": "doc_002",
        "title": "Sintomas de intoxicação por chocolate",
        "content": (
            "Os sinais de intoxicação por chocolate em cães podem "
            "incluir vômitos, diarreia, agitação, tremores, aumento "
            "da frequência cardíaca, convulsões e, em casos graves, "
            "alterações cardíacas importantes."
        ),
        "source": "Manual Veterinário",
    },
    {
        "id": "doc_003",
        "title": "Atendimento em casos de intoxicação",
        "content": (
            "Em casos de suspeita de intoxicação, o animal deve ser "
            "avaliado por um médico veterinário. A avaliação deve "
            "considerar o peso do animal, a substância ingerida, "
            "a quantidade e o tempo desde a ingestão."
        ),
        "source": "Manual Veterinário",
    },
    {
        "id": "doc_004",
        "title": "Chocolate e teobromina",
        "content": (
            "A teobromina presente no chocolate é metabolizada "
            "mais lentamente pelos cães. Chocolates com maior "
            "concentração de cacau apresentam maior risco de "
            "intoxicação."
        ),
        "source": "Manual Veterinário",
    },
]


def seed():

    collection = ChromaDBClient.get_collection()

    collection.upsert(
        ids=[document["id"] for document in documents],
        documents=[document["content"] for document in documents],
        metadatas=[
            {
                "title": document["title"],
                "source": document["source"],
            }
            for document in documents
        ],
    )

    logger.info(
        f"{len(documents)} documentos inseridos no ChromaDB"
    )


if __name__ == "__main__":
    seed()