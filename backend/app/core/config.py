from pydantic_settings import BaseSettings, SettingsConfigDict


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
    # Pipeline
    # ==========================
    TOP_K: int = 5
    RERANK_TOP_K: int = 3

    # Flags de liga/desliga das etapas de consulta,
    # usadas no estudo de ablação.
    QUERY_REWRITING_ENABLED: bool = True
    MULTI_QUERY_ENABLED: bool = True
    HYDE_ENABLED: bool = True

    # ==========================
    # Configuração do .env
    # ==========================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()