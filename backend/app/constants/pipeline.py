DEFAULT_TOP_K = 5

DEFAULT_RERANK_K = 3

DEFAULT_SCORE_THRESHOLD = 0.70

# Corte de entrada no prompt da base acadêmica. Medido em 20/09/2026 contra as
# 98 linhas da avaliação: 0.72 impediu três contextos limítrofes que pioravam a
# decisão e levou o RAG de 80 para 84 acertos, a um caso da linha de base sem
# RAG. O limiar 0.70 continua sendo exibido nas métricas históricas. Desde
# 25/09 vale só para o braço acadêmico (preset hoje_academico_*) e para o braço
# "fichas com porta" da ablação.
ACADEMIC_CONTEXT_MIN_SCORE = 0.72

# Padrão desde 25/09 (rodada 24 do João): com as fichas de triagem, as 3 mais
# próximas entram sempre, sem porta. Na autópsia 2, a porta de 0,72 calibrada
# no MiniLM fechava 98 de 129 prompts com o bge-m3, e as 3 fichas sem porta
# levaram o qwen de 21 para 7 emergências perdidas nos relatos de quem não viu
# o mapa (rodada 16).
DEFAULT_CONTEXT_MIN_SCORE = 0.0
