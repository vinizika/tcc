# Pré-triagem veterinária com RAG

Trabalho de conclusão de curso (Ciência da Computação, FEI, 2026) de Julian
Ryu Takeda, João Pedro Peterutto e Vinicius de Castro Duarte, orientado por
Rafael Gomes Alves.

O sistema recebe o relato de um tutor sobre seu cão ou gato — por texto ou
voz — e indica se o caso deve ser tratado como **emergência**, **não
emergência** ou **incerto**, com justificativa ancorada em protocolos
veterinários recuperados de uma base local. Roda inteiro na máquina, com um
modelo de linguagem pequeno (`llama3.2:3b` via Ollama). Não diagnostica nem
prescreve, e não substitui a avaliação de um médico-veterinário.

---

## Como o sistema funciona

```
relato do tutor (texto, ou voz transcrita pelo Whisper)
   │
   ├─ etapa de consulta ......... reescrita clínica → multi-query → HyDE
   ├─ busca vetorial ............ ChromaDB, embeddings multilíngues
   ├─ re-ranking ................ (hoje só reordena pelo score)
   └─ classificação ancorada .... o modelo lê o relato original + os trechos
                                  recuperados e devolve JSON estruturado
                                  (classificação, justificativa, sinais,
                                  recomendação, fontes citadas)
```

**Cada etapa pode ser ligada ou desligada por requisição**, sem reiniciar o
serviço. Com a busca desligada o sistema roda como "LLM puro", que é a linha
de base contra a qual o RAG é medido. As chaves e seus donos estão em
[`docs/CONTRATOS.md`](docs/CONTRATOS.md).

**Estado medido em 04/09/2026**, sobre 98 relatos: a melhor configuração é
o prompt atual **sem** RAG (0,893 de acurácia balanceada); com a base de
conhecimento atual, ligar o RAG **piora** o resultado em 20 pontos. O porquê
e os dados estão na
[rodada 4 do trilho B2](evidencias/joao/2026-09-04-05-runner-de-avaliacao.md).

---

## Subindo o sistema

Padrão do time: Docker Compose sobe backend, frontend e Ollama juntos, com a
mesma configuração em todas as máquinas.

**1. Configuração local** (uma vez por máquina, opcional):

```bash
cp .env.example .env
```

O `.env` não vai para o Git. O projeto sobe sem ele, com os padrões do
código; é onde você sobrescreve o que for específico da sua máquina. As
opções estão comentadas no [`.env.example`](.env.example).

**2. Suba os serviços:**

```bash
docker compose up -d
```

Com **GPU NVIDIA**, use o override — o modelo passa a rodar na placa e cada
resposta cai de minutos para segundos:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

**3. Baixe o modelo dentro do container** (uma vez; fica no volume):

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

**4. Indexe a base de conhecimento** (uma vez por máquina — o banco vetorial
não é versionado, e sem este passo o RAG não recupera nada):

```bash
docker compose exec backend python -m app.database.ingest_documents
```

Confira que funcionou: `curl localhost:8000/health/fingerprint` deve mostrar
`chunk_count` maior que zero (hoje, 18 trechos de 7 protocolos). Para
reindexar do zero, acrescente `--reset`.

**5. Acesse:**

| O quê | Onde |
|---|---|
| Interface | <http://localhost:8501> |
| API | <http://localhost:8000> |
| Saúde | <http://localhost:8000/health/> |
| Identidade da versão (modelo, base, prompts) | <http://localhost:8000/health/fingerprint> |

Logs: `docker compose logs -f backend`. Derrubar: `docker compose down`.

> **Ollama nativo na máquina?** Ele ocupa a porta 11434 e conflita com o
> container. O override de GPU já resolve (não publica a porta); sem ele,
> encerre o Ollama nativo antes de subir o compose.

### Rodando o backend fora do Docker

Útil para iterar rápido em prompts. O código é o mesmo; só a configuração
muda (o padrão de `OLLAMA_HOST` é `localhost:11434`, o do Ollama nativo).

```bash
cd backend
python -m venv .venv
# ative: .venv\Scripts\Activate.ps1 (Windows) ou source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

O frontend, hoje, **só funciona pelo compose**: ele tem o hostname `backend`
fixo no código (item [B-23](evidencias/backlog.md#b-23) do backlog).

---

## A API

Todas as rotas em [`docs/CONTRATOS.md`](docs/CONTRATOS.md). A principal:

```bash
curl -s -X POST localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "minha gata nao consegue fazer xixi desde ontem"}'
```

A resposta traz `answer` (texto pronto para exibir), `triage` (a
classificação estruturada, com as fontes citadas), `sources` (os trechos que
o classificador viu), `retrieval` (o que a busca encontrou), `config` (o que
de fato rodou) e `timings`. Para ligar ou desligar etapas nesta requisição:

```bash
curl -s -X POST localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "...", "options": {"retrieval_enabled": false}}'
```

Outras rotas: `POST /search/` (só a busca), `POST /voice/` (transcrição de
áudio), `GET /health/`, `GET /health/fingerprint`.

---

## Testes

Dois conjuntos, porque rodam em lugares diferentes:

```bash
# backend: dentro do container (49 testes, sem modelo nem banco — usam dublês)
docker compose exec backend python -m pytest -q

# scripts: no host (48 testes, incluindo o de regressão contra a medição de 04/05)
python -m pytest scripts/tests -q
```

No Windows, prefixe os comandos do host com `$env:PYTHONUTF8=1;` (PowerShell)
para os acentos dos arquivos serem lidos corretamente.

---

## Medindo o sistema

O runner roda os 98 relatos do conjunto de avaliação contra a API e grava
uma rodada versionável, com manifesto do que executou e teste estatístico
para comparar duas rodadas. Passo a passo em
[`data/evaluation/README.md`](data/evaluation/README.md).

```bash
python scripts/run_evaluation.py --preset naive_rag --subset full --name minha_rodada
```

---

## Estrutura do repositório

```
backend/
  app/
    api/          rotas HTTP (chat, search, voice, health)
    services/     tradução entre a API e o pipeline
    pipeline/     orquestração da triagem, chaves de liga/desliga, renderização
    clients/      etapa de consulta (B1), busca (A), classificação (B2)
    prompts/      os prompts, versionados (v0_legacy, v1_grounded)
    schemas/      contratos de entrada e saída (Pydantic)
    core/         configuração, cliente Ollama, logger
    database/     ChromaDB e ingestão dos documentos (A)
    ai/whisper/   transcrição de voz (B1)
  data/documents/ a base de conhecimento: PDFs + metadados em JSON
  tests/          testes do backend
frontend/         interface Streamlit (o compose sobe main.py)
scripts/          limpeza de dados, data augmentation, avaliação → README próprio
data/             datasets, processados e rodadas de avaliação → README próprio
docs/             divisão de trabalho, contratos, diário inicial → README próprio
evidencias/       o que cada um fez, mediu e concluiu, rodada a rodada → README próprio
mock/             protótipo inicial (obsoleto)
```

---

## Documentação: onde está o quê

O projeto é desenvolvido em três trilhos paralelos, e a documentação segue
uma dinâmica combinada. O mapa completo está em
[`docs/README.md`](docs/README.md); em resumo:

| Pergunta | Onde |
|---|---|
| De quem é esta pasta? Qual é o meu escopo e o cronograma? | [`docs/divisao-de-trabalho.md`](docs/divisao-de-trabalho.md) |
| Que formato a API devolve? Que chaves existem? | [`docs/CONTRATOS.md`](docs/CONTRATOS.md) |
| O que foi feito, por quê, e o que se mediu? | [`evidencias/<nome>/`](evidencias/README.md) |
| O que está aberto no projeto, com quem, e quão urgente? | [`evidencias/backlog.md`](evidencias/backlog.md) |
| Onde cada trilho está e para onde vai? | `evidencias/<nome>/planejamento.md` |
| Como medir e ler os números? | [`data/evaluation/README.md`](data/evaluation/README.md) |

## Time

| Trilho | Responsável | Cuida de |
|---|---|---|
| **A** — Recuperação e conhecimento | Vinicius | base de conhecimento, ingestão, embeddings, busca, re-ranking |
| **B1** — Consulta | Ryu | Whisper, reescrita de consulta, multi-query, HyDE |
| **B2** — Decisão | João | classificação ancorada, prompts, régua de avaliação |

Detalhes, fronteiras e acordos em
[`docs/divisao-de-trabalho.md`](docs/divisao-de-trabalho.md).
