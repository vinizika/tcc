from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# A raiz do repositorio, para que um unico .env sirva tanto ao docker compose
# quanto ao backend rodando fora do container.
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):

    # ==========================
    # Informações da API
    # ==========================
    API_NAME: str = "TCC Pré-Triagem Veterinária"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # ==========================
    # OpenAI
    # ==========================
    OPENAI_API_KEY: str = ""

    # ==========================
    # Banco Vetorial
    # ==========================
    VECTOR_DB: str = "chromadb"
    CHROMA_PATH: str = "./chroma_db"

    # ==========================
    # Modelo de linguagem (Ollama)
    # ==========================
    # Dentro do docker compose o backend fala com o container "ollama", e o
    # proprio compose injeta esse valor. O padrao abaixo atende quem roda o
    # backend fora do container.
    OLLAMA_HOST: str = "http://localhost:11434"

    LLM_MODEL: str = "llama3.2:3b"

    # Temperatura zero e seed fixa deixam as rodadas de avaliação
    # reproduzíveis: a mesma entrada devolve a mesma classificação.
    LLM_TEMPERATURE: float = 0.0
    LLM_SEED: int = 42

    # O Ollama trunca o prompt em silêncio quando ele passa de num_ctx, e o
    # que se perde são justamente as instruções iniciais. Por isso o valor é
    # explícito, e não o padrão implícito da biblioteca.
    LLM_NUM_CTX: int = 4096
    LLM_NUM_PREDICT: int = 600

    LLM_TIMEOUT_S: int = 600
    LLM_KEEP_ALIVE: str = "10m"

    # "schema" restringe a decodificação ao formato esperado, e com isso os
    # nomes de campo e os valores de classificação saem exatos; "json"
    # garante apenas que a saída é um JSON válido. Existe como opção para
    # comparar as duas estratégias.
    STRUCTURED_OUTPUT_MODE: str = "schema"

    # ==========================
    # Pipeline
    # ==========================
    TOP_K: int = 5
    RERANK_TOP_K: int = 3

    # Flags de liga/desliga das etapas de consulta,
    # usadas no estudo de ablação.
    QUERY_REWRITING_ENABLED: bool = True
    MULTI_QUERY_ENABLED: bool = True
    HYDE_ENABLED: bool = True

    # Flags de liga/desliga das etapas de decisão, também usadas no estudo
    # de ablação. Com RETRIEVAL_ENABLED desligado o sistema roda como LLM
    # puro, que é a linha de base contra a qual o RAG é medido.
    RETRIEVAL_ENABLED: bool = True
    CONTEXT_TOP_K: int = 3
    COT_ENABLED: bool = False
    SELF_REFINE_ENABLED: bool = False

    TRIAGE_PROMPT_VERSION: str = "v1_grounded"

    # ==========================
    # Configuração do .env
    # ==========================
    model_config = SettingsConfigDict(
        env_file=(
            str(REPOSITORY_ROOT / ".env"),
            ".env",
        ),
        extra="ignore"
    )


settings = Settings()
