from dataclasses import dataclass


@dataclass
class RetrievedDocument:

    id: str

    chunk_id: str

    title: str

    content: str

    source: str

    score: float