from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants.pipeline import DEFAULT_CONTEXT_MIN_SCORE


# A raiz do repositorio, para que um unico .env sirva tanto ao docker compose
# quanto ao backend rodando fora do container.
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):

    # ==========================
    # Informações da API
    # ==========================
    FOLLOWUP_NO_PROGRESS_LIMIT: int = Field(default=2, ge=1, le=5)
    WORKSPACE_NUM_CTX: int = Field(default=32768, ge=4096, le=131072)
    # Prompt de triagem do app (workspace). "v2_suficiencia" acrescenta a
    # regra contra decidir a partir de frase vaga (rodada 23 do Ryu); fica no
    # v1_grounded até ser medido e aceito pelo trilho B2.
    WORKSPACE_PROMPT_VERSION: Literal["v1_grounded", "v2_suficiencia"] = "v1_grounded"
    FOLLOWUP_MAX_QUESTIONS: int = Field(default=4, ge=1, le=10)

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
    # A pasta versionada no repositório (backend/chroma_db), com o ponteiro da
    # coleção ativa. Até 25/09 o padrão era data/chroma, uma pasta fora do Git:
    # um clone limpo subia com a coleção vazia (evidencias/backlog.md#b-57).
    CHROMA_PATH: str = "chroma_db"
    CHROMA_COLLECTION: str = "veterinary_documents"

    # ==========================
    # Modelo de linguagem (Ollama)
    # ==========================
    # Dentro do docker compose o backend fala com o container "ollama", e o
    # proprio compose injeta esse valor. O padrao abaixo atende quem roda o
    # backend fora do container.
    OLLAMA_HOST: str = "http://localhost:11434"

    # O modelo local (Ollama). Desde 25/09 é o qwen3:8b, a alternativa local
    # medida na autópsia 2; o llama3.2:3b (o sistema até 24/09) continua pelo
    # preset local_llama ou por llm_model na requisição.
    LLM_MODEL: str = "qwen3:8b"

    # Quem classifica a urgência (rodada 26 do João). "gemini" é a decisão de
    # produto do João de 25/09; "ollama" usa o LLM_MODEL local. Sem troca
    # silenciosa: com ATTENDANT_FALLBACK="none" (o padrão), se o provedor
    # escolhido falhar a API responde 503 dizendo qual e por quê; com
    # "ollama", responde pelo modelo local e registra a troca na procedência
    # e no texto da resposta.
    ATTENDANT_PROVIDER: str = "gemini"
    ATTENDANT_FALLBACK: str = "none"

    # Temperatura zero e seed fixa deixam as rodadas de avaliação
    # reproduzíveis: a mesma entrada devolve a mesma classificação.
    LLM_TEMPERATURE: float = 0.0
    LLM_SEED: int = 42

    # O Ollama trunca o prompt em silêncio quando ele passa de num_ctx, e o
    # que se perde são justamente as instruções iniciais. Por isso o valor é
    # explícito, e não o padrão implícito da biblioteca.
    LLM_NUM_CTX: int = 4096
    LLM_NUM_PREDICT: int = 600

    # O qwen3 "pensa" (escreve um raciocínio oculto) antes de responder, a
    # menos que a chamada diga que não. A autópsia 2 mediu o qwen sem pensar
    # (rodada 18 do João), e pensar custa dezenas de segundos por caso. O
    # llama ignora o parâmetro. None = não mandar nada ao Ollama.
    LLM_THINK: bool | None = False

    # ==========================
    # Gemini
    # ==========================
    # Desde 25/09 o Gemini é o atendente padrão (ATTENDANT_PROVIDER acima) e
    # continua sendo o primeiro provedor da etapa de consulta quando ela está
    # ligada (HybridQueryClient). A chave vem só do ambiente (.env local,
    # nunca o .env.example) e nunca é registrada em log nem no retrato.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    GEMINI_TIMEOUT_S: float = 60.0
    # Espaço mínimo entre chamadas: a cota gratuita tem limite por minuto.
    GEMINI_MIN_INTERVAL_S: float = 4.0
    GEMINI_MAX_RETRIES_429: int = 8
    GEMINI_MAX_RETRIES_503: int = 6

    LLM_TIMEOUT_S: int = 600
    LLM_KEEP_ALIVE: str = "10m"

    # "schema" restringe a decodificação ao formato esperado, e com isso os
    # nomes de campo e os valores de classificação saem exatos; "json"
    # garante apenas que a saída é um JSON válido. Existe como opção para
    # comparar as duas estratégias.
    STRUCTURED_OUTPUT_MODE: str = "schema"

    # ==========================
    # Persistência: contas do modo real e histórico de conversa
    # ==========================
    # Supabase (Postgres) guarda só os perfis de login do modo real
    # (supabase_schema.sql). O cadastro de tutor/pet que morava aqui saiu em
    # 06/10 (rodada 25 do Ryu): pets e conversas ficam no MongoDB do app.
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # MongoDB guarda o histórico de conversa — formato varia por turno
    # (texto ou voz, com ou sem triagem anexada), então não força um schema
    # relacional. O padrão atende quem roda o backend fora do container; o
    # compose injeta o endereço do serviço "mongo" (mesmo desenho do
    # OLLAMA_HOST).
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "vetai"

    # Segunda etapa. ``demo`` usa apenas identidades e clínicas fictícias;
    # ``real`` exige Supabase Auth e nunca cai silenciosamente no demo.
    WORKFLOW_MODE: str = "demo"
    AUTH_PROVIDER: str = "supabase"
    POC_QUICK_LOGIN_ENABLED: bool = False
    MAPS_PROVIDER: str = "auto"
    MAPS_KEY_KIND: str = "demo"
    POC_RAG_PATH: str = ""
    POC_RAG_COLLECTION: str = ""
    SESSION_TTL_HOURS: int = 24
    FRONTEND_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    WORKFLOW_POLL_INTERVAL_S: int = 8

    # Chaves separadas por finalidade. A chave web é injetada no frontend e
    # deve ter restrição de domínio; a chave de servidor chama Places/
    # Geocoding e não é enviada ao navegador.
    GOOGLE_MAPS_SERVER_KEY: str = ""
    GOOGLE_MAPS_WEB_KEY: str = ""
    GOOGLE_MAP_ID: str = "DEMO_MAP_ID"
    GOOGLE_MAPS_LANGUAGE: str = "pt-BR"
    GOOGLE_MAPS_REGION: str = "BR"

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

    # Flags de liga/desliga das etapas de consulta (o "tradutor"), usadas no
    # estudo de ablação. Dono: trilho B1 (docs/CONTRATOS.md, item 4).
    #
    # Desligadas por padrão desde 25/09 (rodada 24 do João). A autópsia 2
    # mediu que, nas fichas de triagem, toda técnica piora a busca (a ficha
    # certa em 1º cai de 107 para 84 em 129 casos) e que, com o qwen, fichas
    # sem tradutor é a melhor célula da 2×2 (rodada 17). Os presets
    # `fichas_tradutor` e `hoje_academico_*` religam as três.
    #
    # Histórico do HyDE: ligado de novo em 23/09 (estava desligado desde
    # 17/09, evidencias/backlog.md#b-09) com o HybridQueryClient
    # (evidencias/ryu/2026-09-23-16-integracao-gemini-com-fallback.md).
    QUERY_REWRITING_ENABLED: bool = False
    MULTI_QUERY_ENABLED: bool = False
    HYDE_ENABLED: bool = False

    # Flags de liga/desliga das etapas de decisão, também usadas no estudo
    # de ablação. Com RETRIEVAL_ENABLED desligado o sistema roda como LLM
    # puro, que é a linha de base contra a qual o RAG é medido.
    RETRIEVAL_ENABLED: bool = True

    # Como a busca ordena o que achou (rodada 24 do João):
    # - "vector": só a similaridade do embedding, em ordem. É o padrão, e é a
    #   busca medida na autópsia 2 sobre as fichas de triagem;
    # - "routed_rerank": o caminho até 24/09 — rota lexical pelo vocabulário do
    #   mapa, reranker lexical, âncoras e veto de espécie. Fica para o braço
    #   acadêmico da ablação.
    RETRIEVAL_MODE: str = "vector"
    CONTEXT_TOP_K: int = 3
    COT_ENABLED: bool = False
    SELF_REFINE_ENABLED: bool = False

    # Score minimo para um trecho recuperado entrar no prompt.
    #
    # Desde 25/09 o padrão é 0.0: com as fichas de triagem entram sempre as 3
    # mais próximas (ver app/constants/pipeline.py). O histórico abaixo é da
    # base acadêmica, onde o corte continua valendo pelos presets.
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
