from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants.pipeline import DEFAULT_CONTEXT_MIN_SCORE


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
    CHROMA_PATH: str = "data/chroma"
    CHROMA_COLLECTION: str = "veterinary_documents"

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

    # ==========================
    # Gemini (experimental — comparação com Ollama na etapa de consulta)
    # ==========================
    # Nada no pipeline de produção lê estas duas. Existem só para
    # backend/app/clients/gemini_query_client.py e o script de comparação
    # em backend/app/database/compare_query_providers.py — o teste pedido
    # pelo grupo em 22/09 para ver se um modelo maior ajuda a reescrita, o
    # multi-query e o HyDE. Sem chave configurada, o cliente recusa a
    # chamada com uma mensagem clara em vez de falhar tarde, na API do
    # Google.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"

    LLM_TIMEOUT_S: int = 600
    LLM_KEEP_ALIVE: str = "10m"

    # "schema" restringe a decodificação ao formato esperado, e com isso os
    # nomes de campo e os valores de classificação saem exatos; "json"
    # garante apenas que a saída é um JSON válido. Existe como opção para
    # comparar as duas estratégias.
    STRUCTURED_OUTPUT_MODE: str = "schema"

    # ==========================
    # Persistência: tutores, pets e histórico de conversa
    # ==========================
    # Supabase (Postgres) guarda tutores e pets — dados estruturados, com
    # relação clara entre as duas tabelas. Vazio por padrão: em
    # desenvolvimento, sem um projeto criado ainda, as rotas de tutor/pet
    # devolvem 503 em vez de derrubar o resto da API.
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # MongoDB guarda o histórico de conversa — formato varia por turno
    # (texto ou voz, com ou sem triagem anexada), então não força um schema
    # relacional. O padrão atende quem roda o backend fora do container; o
    # compose injeta o endereço do serviço "mongo" (mesmo desenho do
    # OLLAMA_HOST).
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "vetai"

    # ==========================
    # Transcrição de voz (Whisper)
    # ==========================
    # Teto do áudio aceito na transcrição. O relato de um tutor em emergência
    # é curto; 25 MB cobrem com folga qualquer gravação real e limitam o
    # consumo de disco em uploads repetidos ou maliciosos (evidencias/
    # backlog.md#b-32).
    MAX_AUDIO_UPLOAD_MB: int = 25

    # Tamanho do modelo faster-whisper. Fica explícito porque o número de WER
    # medido depende dele, e o artigo cita uma taxa de acerto sem dizer qual
    # modelo a produziu (evidencias/backlog.md#b-13). "small" é o que roda
    # hoje na CPU do container.
    WHISPER_MODEL_SIZE: str = "small"

    # ==========================
    # Pipeline
    # ==========================
    TOP_K: int = 5
    RERANK_TOP_K: int = 3

    # Flags de liga/desliga das etapas de consulta,
    # usadas no estudo de ablação. Dono: trilho B1 (docs/CONTRATOS.md, item 4).
    QUERY_REWRITING_ENABLED: bool = True
    MULTI_QUERY_ENABLED: bool = True

    # Ligado de novo em 23/09 (estava desligado desde 17/09). O motivo do
    # desligamento original (evidencias/backlog.md#b-09) era o Ollama: em
    # três coleções reais, nunca melhorou Precision@1/MRR e alucinava
    # diagnóstico sem âncora. Com o HybridQueryClient (Gemini com fallback
    # para Ollama, evidencias/ryu/2026-09-23-16-integracao-gemini-com-
    # fallback.md), o HyDE roda via Gemini — 25 casos revisados sem
    # nenhuma alucinação — e, se o Gemini falhar, o HyDE simplesmente não
    # gera documento nesta consulta em vez de cair para o Ollama: cair
    # reintroduziria em silêncio o problema que este flag resolveu.
    HYDE_ENABLED: bool = True

    # Flags de liga/desliga das etapas de decisão, também usadas no estudo
    # de ablação. Com RETRIEVAL_ENABLED desligado o sistema roda como LLM
    # puro, que é a linha de base contra a qual o RAG é medido.
    RETRIEVAL_ENABLED: bool = True
    CONTEXT_TOP_K: int = 3
    COT_ENABLED: bool = False
    SELF_REFINE_ENABLED: bool = False

    # Score minimo para um trecho recuperado entrar no prompt.
    #
    # Ficou em 0.0 de 04/09 a 12/09, de proposito: naquele momento nenhum
    # documento atingia o limiar de relevancia, e descartar todos faria o
    # braco com RAG ficar identico ao braco sem RAG, impedindo medir. A
    # decisao mandava registrar o score de cada trecho para que virasse
    # evidencia depois -- e virou: a rodada 9 mediu que, nas 98 linhas do
    # conjunto, NENHUM trecho passou de 0.70 e mesmo assim tres entravam em
    # todos os prompts. Os bracos com RAG mediram injecao de ruido, nao
    # recuperacao.
    #
    # A avaliação completa de 20/09/2026 comparou 0.70 e 0.72 na mesma base.
    # O corte 0.72 eliminou os três erros novos causados por trechos
    # limítrofes e deixou o RAG a um acerto da linha de base sem RAG. Ele é
    # conservador de propósito: sem evidência suficientemente próxima, o
    # classificador recebe o relato sem contexto em vez de receber ruído.
    #
    # Para reproduzir as rodadas anteriores a 12/09, passe
    # context_min_score=0.0 na requisicao ou use o preset
    # naive_rag_sem_corte.
    CONTEXT_MIN_SCORE: float = DEFAULT_CONTEXT_MIN_SCORE

    # Passa tambem a pergunta reescrita ao classificador. Desligado porque a
    # reescrita adiciona interpretacao clinica ("requer avaliacao imediata"),
    # o que misturaria a etapa de consulta na decisao.
    REWRITTEN_HINT_ENABLED: bool = False

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
