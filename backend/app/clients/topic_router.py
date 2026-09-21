"""Ponte lexical entre relatos PT-BR e os tópicos estáveis da curadoria."""

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

from app.core.logger import setup_logger


logger = setup_logger("TopicRouter")
TERMS_PATH = Path(__file__).resolve().parents[2] / "data" / "retrieval_terms.json"
TOKEN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "animal", "dog", "cat", "cao", "cachorro", "gata", "gato",
    "com", "the", "and", "with", "para", "uma", "meu", "minha",
}


def normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).casefold()
    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )


def tokens(text: str) -> set[str]:
    return {
        token for token in TOKEN.findall(normalize(text))
        if len(token) >= 3 and token not in STOPWORDS
    }


def concept_tokens(text: str) -> set[str]:
    return {token[:5] if len(token) >= 6 else token for token in tokens(text)}


def load_topic_terms() -> dict[str, tuple[str, ...]]:
    try:
        payload = json.loads(TERMS_PATH.read_text(encoding="utf-8"))
        topics = payload.get("topics") or {}
        return {
            str(topic): tuple(str(term) for term in terms)
            for topic, terms in topics.items()
            if isinstance(terms, list)
        }
    except (OSError, TypeError, ValueError) as error:
        logger.warning("Vocabulário de assuntos indisponível: %s", error)
        return {}


TOPIC_TERMS = load_topic_terms()


def topic_scores(query: str) -> dict[str, float]:
    profiles = {
        topic: set().union(*(concept_tokens(term) for term in terms))
        for topic, terms in TOPIC_TERMS.items()
    }
    if not profiles:
        return {}

    document_frequency = Counter(
        token for profile_tokens in profiles.values() for token in profile_tokens
    )
    known_query_tokens = {
        token for token in concept_tokens(query) if token in document_frequency
    }
    if not known_query_tokens:
        return {}

    topic_count = len(profiles)

    def weight(token: str) -> float:
        return math.log(
            (topic_count + 1) / (document_frequency[token] + 1)
        ) + 1.0

    denominator = sum(weight(token) for token in known_query_tokens)
    return {
        topic: sum(weight(token) for token in known_query_tokens & profile_tokens)
        / denominator
        for topic, profile_tokens in profiles.items()
    }


def likely_topics(query: str, *, limit: int = 3, minimum: float = 0.20) -> list[str]:
    ordered = sorted(topic_scores(query).items(), key=lambda item: item[1], reverse=True)
    return [topic for topic, score in ordered[:limit] if score >= minimum]
