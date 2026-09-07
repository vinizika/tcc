"""Configuração compartilhada pelo ChromaDB e pelo processamento textual."""

# Este nome é o mesmo já usado pela coleção. Mantê-lo aqui evita que o
# tokenizer do ingestor e o modelo que gera os embeddings divirjam.
EMBEDDING_MODEL_NAME = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# O SentenceTransformer publicado para este modelo usa max_seq_length=128.
# O ingestor ainda confere o model_max_length exposto pelo tokenizer e adota
# sempre o menor dos dois valores.
EMBEDDING_MAX_TOKENS = 128

# Baseline experimental. Não são valores considerados ótimos: devem ser
# comparados posteriormente na régua de recuperação do trilho A.
CHUNK_TARGET_TOKENS = 96
CHUNK_OVERLAP_TOKENS = 16
