# Pré-triagem veterinária com RAG

Trabalho de conclusão de curso (Ciência da Computação, FEI, 2026) de Julian
Ryu Takeda, João Pedro Peterutto e Vinicius de Castro Duarte, orientado por
Rafael Gomes Alves.

O sistema recebe o relato de um tutor sobre seu cão ou gato — por texto ou
voz — e indica se o caso deve ser tratado como **emergência**, **não
emergência** ou **incerto**, com justificativa ancorada em **fichas de
triagem** escritas a partir do mapa de assuntos e de documentos veterinários
aprovados. O atendente padrão é o Gemini (`gemini-3.5-flash-lite`); o
`qwen3:8b` (local, via Ollama, com GPU) e o `llama3.2:3b` ficam como opções, e
o sistema nunca troca de modelo em silêncio. Não diagnostica nem prescreve, e
não substitui a avaliação de um médico-veterinário.

---

## Como o sistema funciona

A interface React de tutor/clínica está integrada a este backend. Para executar
login, animais, histórico, chat, mapa e encaminhamentos em `localhost:3000`,
siga [POC utilizável — operação e limites](docs/poc-utilizavel.md). O workspace
usa a coleção ativa do João e permite selecionar Gemini ou Ollama; não é uma
implantação pública em produção.

```
relato do tutor (texto, ou voz transcrita pelo Whisper), cru
   │
   ├─ busca vetorial ............ bge-m3 nas 61 fichas de BUSCA (uma por quadro
   │                              do mapa, escrita para casar com o jeito do
   │                              tutor contar); as 3 mais próximas, sempre
   └─ classificação ancorada .... o atendente lê o relato + as 3 fichas de
                                  LEITURA dos mesmos quadros (a ficha do mapa,
                                  com a conduta fixa pela urgência) e devolve
                                  JSON estruturado (classificação, justificativa,
                                  sinais, recomendação, fontes citadas)
```

A resposta cita a ficha usada e o documento aprovado por trás dela, com o
título real, e diz quem respondeu (provedor, modelo, versão). A arquitetura e
o porquê de cada peça estão nas rodadas 14 a 21 do João (a
[rodada 21](evidencias/joao/2026-09-24-22-arquitetura-proposta-contra-a-de-hoje.md)
resume); a implementação, nas rodadas 22 a 26. A etapa de consulta (reescrita,
multi-query, HyDE), o roteador lexical, o reranker e a base acadêmica de 3.481
trechos continuam no código, desligados por padrão, como braços da ablação.

**Cada etapa pode ser ligada ou desligada por requisição**, sem reiniciar o
serviço. Com a busca desligada o sistema roda como "LLM puro", que é a linha
de base contra a qual o RAG é medido. As chaves e seus donos estão em
[`docs/CONTRATOS.md`](docs/CONTRATOS.md).

**Estado medido em 25/09/2026**, pela API, com o runner do time
([rodada 26 do João](evidencias/joao/2026-09-25-27-atendente-gemini-e-replica.md)),
em emergências perdidas · falsos alarmes:

| | Prova 1 + régua (74 emergências · 58 leves) | Relatos de quem não viu o mapa (76 · 46) |
|---|---|---|
| **Sistema atual, Gemini** | **2 · 1** | **6 · 3** |
| Sistema atual, qwen3:8b local | 2 · 1 | 5 · 7 |
| O de 24/09 (artigos, MiniLM, porta 0,72, llama) | 15 · 4 | 40 · 22 (medido na autópsia) |

A prova 1 é fácil para os sistemas bons (entrega a classe pelas palavras): o
número final sai da **prova 2**, com rótulos validados por veterinários, ainda
por fazer. O porquê de cada peça está nas rodadas 14 a 21 do João; o histórico
de 04/09 (o RAG com a base antiga piorava o resultado em 20 pontos), na
[rodada 4](evidencias/joao/2026-09-04-05-runner-de-avaliacao.md).

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

**3. O atendente.** O padrão é o Gemini: ponha a sua `GEMINI_API_KEY` no
`.env` (nunca no `.env.example`). Sem chave, o `/chat/` responde **503**
(`attendant_unavailable`) em vez de trocar de modelo escondido. Para rodar só
local, use `ATTENDANT_PROVIDER=ollama` no `.env` (ou o preset `local_qwen` no
runner) e baixe o modelo (uma vez; fica no volume). O qwen precisa de GPU:

```bash
docker compose exec ollama ollama pull qwen3:8b
```

**4. A base de conhecimento já vem pronta**: a coleção das 61 fichas de
triagem está versionada em `backend/chroma_db/`, com o ponteiro ativo, e o
bge-m3 é baixado no primeiro uso (~2,2 GB; fica no volume `hf_cache`). Para
regerar as fichas depois de mudar o mapa ou os rascunhos, e reindexar:

```bash
python scripts/sync_fichas.py
docker compose exec backend python -m app.database.ingest_documents \
  --profile fichas --activate
```

A base acadêmica (perfis `curated`, `experimental`) continua disponível para
a ablação. A operação segura cria uma coleção versionada em staging; não troca
a base ativa por acidente:

```bash
docker compose exec backend python -m app.database.ingest_documents \
  --profile curated --stage-only
```

O perfil `curated` recusa toda fonte sem aprovação clínica, direitos e
procedência completos e falha antes de criar o Chroma se nenhuma for elegível.
Use `experimental` apenas para candidatas e `legacy_rechunk` apenas para os
protocolos sintéticos antigos. A ativação requer `--activate` explícito e
ocorre após contagem, manifesto e hashes serem validados. Consulte o
[`estado atual da ingestão`](docs/estado-atual.md) antes de operar a base.

> **Atenção à base de referência.** As rodadas citadas até 05/09 usaram a
> coleção legada de 18 trechos. Os números posteriores dependem da coleção e
> dos hashes registrados em cada fingerprint. Staging não muda essa base, e o
> rollback preserva o caminho de volta ([B-37](evidencias/backlog.md#b-37)).
> Como preparar e inspecionar um documento novo está em
> [`backend/data/documents/README.md`](backend/data/documents/README.md).

**5. Persistência e identidade.** O compose já sobe o MongoDB usado pelo
histórico, encaminhamentos, eventos e mensagens. No modo demonstrativo isso é
suficiente. Contas e dados reais de tutor/pet usam Supabase: crie um projeto em
[supabase.com](https://supabase.com), rode
[`backend/supabase_schema.sql`](backend/supabase_schema.sql) no SQL Editor
dele, preencha `SUPABASE_URL`/`SUPABASE_KEY` e mude `WORKFLOW_MODE=real`.
Sem isso, `/chat/` e a demonstração funcionam; o modo real falha
explicitamente. Detalhes em [`docs/segunda-etapa.md`](docs/segunda-etapa.md).

**6. Acesse:**

| O quê | Onde |
|---|---|
| Interface React principal | <http://localhost:3000> |
| Streamlit legado (`--profile legacy`) | <http://localhost:8501> |
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

O React pode rodar fora do Compose, em `frontend-react/`, com
`VITE_API_URL=http://localhost:8000 npm run dev`; o Nginx do Compose usa
`/api` e proxy interno.

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

A resposta traz também `provenance` (quem respondeu). Para escolher o
atendente na requisição: `"options": {"attendant_provider": "ollama",
"llm_model": "qwen3:8b"}`.

Outras rotas: `POST /search/` (só a busca), `POST /voice/` (transcrição de
áudio), `GET /health/`, `GET /health/fingerprint`.

**API de tutor, pet e histórico de pré-triagem** (precisa do Supabase
configurado — passo 5 acima; o histórico usa só o Mongo, que já vem no
compose). No modo real, envie `Authorization: Bearer <token>` em todas estas
operações; os exemplos curtos abaixo destinam-se ao modo demonstrativo legado:

```bash
# cadastra o tutor e o pet
tutor_id=$(curl -s -X POST localhost:8000/tutors/ -d '{"name": "Ana"}' | jq -r .id)
pet_id=$(curl -s -X POST localhost:8000/pets/ \
  -d "{\"tutor_id\": \"$tutor_id\", \"name\": \"Bidu\", \"species\": \"cao\"}" | jq -r .id)

# o pet_id enriquece o prompt com o cadastro; qualquer um dos três ids grava histórico
curl -s -X POST localhost:8000/chat/ \
  -d "{\"question\": \"o Bidu vomitou uma vez hoje\", \"pet_id\": \"$pet_id\"}"
```

A resposta traz `conversation_id` — mande de volta no próximo turno para
continuar a mesma conversa. Detalhe completo em
[`docs/CONTRATOS.md`](docs/CONTRATOS.md).

---

## Testes

Dois conjuntos, porque rodam em lugares diferentes:

```bash
# backend: dentro do container; inclui Chroma real em diretório temporário
docker compose exec backend python -m pytest -q

# scripts: no host
python -m pytest scripts/tests -q
```

A contagem é obtida pela própria coleta do pytest e não é mantida manualmente.

No Windows, prefixe os comandos do host com `$env:PYTHONUTF8=1;` (PowerShell)
para os acentos dos arquivos serem lidos corretamente. O CI também confere
que os arquivos gerados estão em dia:

```bash
python scripts/sync_retrieval_terms.py --check
python scripts/sync_fichas.py --check
```

---

## Medindo o sistema

O runner roda um lote de relatos contra a API e grava uma rodada
versionável, com manifesto do que executou (inclusive quem respondeu cada
linha) e teste estatístico para comparar duas rodadas. Passo a passo em
[`data/evaluation/README.md`](data/evaluation/README.md).

```bash
# um lote no formato da prova (id, text, expected_class), com um preset
python scripts/run_evaluation.py --cases data/prova/casos_oficiais.csv --split dev \
    --preset producao --name minha_rodada
```

Presets principais em [`scripts/presets.json`](scripts/presets.json):
`producao` (Gemini), `local_qwen`, `local_llama`, e os braços da ablação
(`fichas_com_porta_0_72`, `fichas_tradutor`, `hoje_academico_llama`,
`hoje_academico_llama_tradutor`). Sem `--cases`, o runner roda o conjunto
antigo de 98 listas de sintomas em inglês, como antes. O lote `teste` da
prova 1 está congelado ([`data/prova/README.md`](data/prova/README.md)); a
prova 2, com os 330 relatos que vão dar o número final, está em
[`data/prova2/`](data/prova2/README.md), aguardando a validação dos
veterinários.

---

## Estrutura do repositório

```
backend/
  app/
    api/          rotas HTTP (chat, search, voice, health, tutors, pets, conversations)
    services/     tradução entre a API e o pipeline; tutor/pet/conversation (Supabase e Mongo)
    pipeline/     orquestração da triagem, chaves de liga/desliga, renderização
    clients/      etapa de consulta (B1), busca (A), classificação (B2), supabase/mongo (B1)
    prompts/      os prompts, versionados (v0_legacy, v1_grounded)
    schemas/      contratos de entrada e saída (Pydantic)
    core/         configuração, cliente Ollama, logger
    database/     ChromaDB e ingestão dos documentos (A)
  supabase_schema.sql  DDL de tutors/pets — rodar uma vez no projeto Supabase
  data/documents/ os documentos aprovados: PDFs/TXT + metadados em JSON (com o título real)
  data/fichas.json as 61 fichas de triagem (busca + leitura), geradas por scripts/sync_fichas.py
  chroma_db/      a coleção ativa (as fichas no bge-m3), versionada, com o ponteiro
  tests/          testes do backend
frontend/         interface Streamlit legada (perfil opcional `legacy`)
frontend-react/   interface React/TypeScript principal da segunda etapa
scripts/          limpeza de dados, data augmentation, avaliação → README próprio
data/             datasets, processados e rodadas de avaliação → README próprio
docs/             divisão de trabalho, contratos, diário inicial → README próprio
evidencias/       o que cada um fez, mediu e concluiu, rodada a rodada → README próprio
mock/             protótipo oficial de demonstração (independente do frontend real)
```

### Protótipo de localização e painel de clínicas

O fluxo navegável com clínicas fictícias, consentimento antes do encaminhamento
e dashboard isolado por clínica vive em [`mock/`](mock/README.md). Ele é uma
demonstração independente, executada na porta 8502, e não substitui nem chama o
frontend/backend reais do Compose.

### Segunda etapa integrada

O fluxo funcional tutor → clínica usa o frontend React, autenticação por papel,
descoberta de clínicas, consentimento, encaminhamento idempotente, dashboard,
máquina de estados e chat humano persistente. A POC atual também oferece
contas próprias locais, animais e chat RAG persistentes, Google real e
acessos acadêmicos independentes do provedor de mapas. Veja
[`docs/poc-utilizavel.md`](docs/poc-utilizavel.md) para executar e testar e
[`docs/brand-book.md`](docs/brand-book.md) para marca, fontes e decisões de UX.
Não se trata de uma implantação pública de serviço veterinário. Configuração anterior,
custos, verificação institucional, estados e limitações estão em
[`docs/segunda-etapa.md`](docs/segunda-etapa.md).

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

### Pré-triagem conversacional

Casos `INCERTO` no workspace agora podem receber uma pergunta objetiva e,
quando necessário, um formulário curto persistente. Veja a
[operação e máquina de estados](docs/pre-triagem-conversacional.md) e a
[evidência da rodada](evidencias/vini/2026-09-28-pre-triagem-conversacional.md).

A [correção e reavaliação de 02/10](evidencias/vini/2026-10-02-20-correcao-regressoes-conversacionais.md)
separa o texto da busca dos metadados, usa entradas clínicas iguais para texto e
formulário e fixa perguntas/opções por observação. O fluxo atual é versionado como
`conversational_v2`.
