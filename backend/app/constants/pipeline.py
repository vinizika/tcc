DEFAULT_TOP_K = 5

DEFAULT_RERANK_K = 3

DEFAULT_SCORE_THRESHOLD = 0.70

# Medido em 20/09/2026 contra as 98 linhas da avaliação: 0.72 impediu três
# contextos limítrofes que pioravam a decisão e levou o RAG de 80 para 84
# acertos, a um caso da linha de base sem RAG. O limiar 0.70 continua sendo
# exibido nas métricas históricas; este é especificamente o corte de entrada
# no prompt.
DEFAULT_CONTEXT_MIN_SCORE = 0.72
