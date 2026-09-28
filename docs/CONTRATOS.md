# Contratos entre os trilhos

Este documento descreve **o que atravessa a fronteira entre os trilhos**. É o
que permite os três trabalharem em paralelo: cada um só precisa respeitar o
formato dos dados que entrega ao próximo, sem depender do código alheio.

Mudança em qualquer contrato daqui vai em commit separado, avisando o dono do
outro lado. A divisão de trabalho e as fronteiras de cada trilho estão em
[`divisao-de-trabalho.md`](divisao-de-trabalho.md).

---

## 1. Consulta pronta para busca — B1 → A

O que a etapa de consulta entrega à busca vetorial: uma **lista de textos**.

Desde 17/09 (decisão do B-10), o pipeline monta essa lista assim:

1. a consulta reescrita (ou o relato original, se a reescrita estiver
   desligada) — **sempre** entra, é a primeira da lista;
2. as variações geradas pelo multi-query, **se** ligado, sem duplicar a
   reescrita;
3. o documento hipotético do HyDE, **se** ligado.

**Desde 25/09 as três etapas vêm desligadas por padrão** (rodada 24 do João):
nas fichas de triagem, toda técnica piora a busca, e o relato vai cru. Elas
continuam no código como braço da ablação (presets `fichas_tradutor` e
`hoje_academico_llama_tradutor`). Quando ligadas, o `HybridQueryClient` tenta o
Gemini e cai para o Ollama; desde 25/09 a queda deixa de ser invisível: cada
chamada aparece em `provenance.query_stage.calls` na resposta.

"Ligado" é superconjunto de "desligado": multi-query ligado nunca produz uma
lista de natureza diferente da de desligado, só mais itens. Validado contra
três coleções experimentais reais em
[evidencias/ryu/2026-09-17-06-medindo-consulta-nas-candidatas.md](../evidencias/ryu/2026-09-17-06-medindo-consulta-nas-candidatas.md).

## 2. Documento recuperado — A → B2

O que a busca devolve, por trecho:

| Campo | Uso |
|---|---|
| `chunk_id` | Identifica o trecho exato; usado para marcar quais embasaram a resposta. Nas fichas: `ficha__<topic>` |
| `title` | Vai ao prompt. Nas fichas, é o título da **ficha de leitura** ("Ficha de triagem: <quadro>") |
| `content` | Corpo limpo que entra no prompt; não inclui os prefixos de título/seção usados somente no embedding. Nas fichas, é a **ficha de leitura** (o texto vetorizado é a ficha de busca, que o atendente não lê) |
| `source` | Arquivo de origem, exibido junto do título |
| `score` | Similaridade; decide o corte e vai nas métricas |
| `display_title`, `references` | Só nas fichas (desde 25/09): o nome da ficha para o tutor e os documentos aprovados por trás dela (título real, periódico, ano, DOI). Vão à citação, não ao prompt |
| `topic` | **O assunto do documento.** Identificador estável, em inglês e snake_case (`chocolate_toxicosis`, `urethral_obstruction`). Vem do sidecar JSON da fonte. Acrescentado em 12/09 (`74c6dfa`) |
| `source_file` | Caminho do arquivo de origem, relativo à pasta de documentos. Acrescentado no mesmo commit |

**Estável.** Acrescentar campo é seguro; renomear ou remover quebra o
classificador.

### `topic` é um identificador, não um rótulo de exibição

Desde 12/09 o `topic` atravessa três lugares e precisa ser **o mesmo texto**
nos três:

| Onde | O que faz |
|---|---|
| `backend/data/documents/<fonte>.json` | Declara o assunto da fonte |
| `POST /search/`, por trecho | Diz de qual assunto veio cada trecho recuperado |
| `data/curadoria/mapa-de-assuntos.csv`, coluna `id` | A linha do mapa que aquele assunto cobre |

É por igualdade exata entre os três que a régua de recuperação julga a busca
(`expected_topics` em `data/retrieval/cases.csv`) e que o `compare` do agente
de ingestão mede **cobertura**: quais quadros do mapa passaram a ter documento
e quais faltam ([B-51](../evidencias/backlog.md#b-51)).

**Consequência prática, para o trilho A:** renomear um `topic`, ou indexar uma
fonte com `topic` que não existe no mapa, faz a cobertura parar de bater **sem
erro visível** — a busca continua funcionando e o número fica errado. As duas
coisas são permitidas; o que não pode é acontecer sozinho. Documento novo entra
com o `topic` de uma linha do mapa; assunto novo ganha linha no mapa antes de
ser indexado. O teste `scripts/tests/test_mapa_de_assuntos.py` recusa as duas
situações, e é a rede de segurança disso.

`species` é persistido no metadado vetorial e no fingerprint por tópico. O
vocabulário fechado é `dog`, `cat` e `dog_and_cat`. O compare só considera um
tópico coberto quando o inventário daquela rodada cobre a espécie esperada e
o tópico é devolvido num caso que realmente o espera ([B-53](../evidencias/backlog.md#b-53)).

Cada rodada deve preservar o fingerprint da sua própria coleção. Ler sidecars
atuais para explicar uma rodada antiga é proibido: eles podem ter mudado.

## 3. Resposta de triagem — B2 → runner e frontend

O que `POST /chat/` devolve. **`answer` continua sendo texto** para o frontend
atual não quebrar; quem consome por programa deve ler de `triage`.

```
{
  "answer": str,                    // markdown pronto para exibir
  "sources": [                      // apenas os trechos que o classificador viu
    { "title", "source", "score", "chunk_id", "cited",
      "topic", "display_title", "references": [ { "title", "journal", "year", "doi", "url" } ] }
  ],
  "triage": {
    "classificacao": "EMERGENCIA" | "NAO_EMERGENCIA" | "INCERTO",
    "justificativa": str,
    "sinais_de_alerta": [str],
    "recomendacao": str,
    "fontes": [ { "index", "chunk_id", "title", "source", "display_title", "references" } ],
    "raciocinio": str | null,       // preenchido com o Chain-of-Thought ligado
    "json_parsed": bool,            // o modelo devolveu um JSON
    "schema_valid": bool,           // o JSON tinha o formato esperado
    "attempts": int,
    "done_reason": str | null,      // "length" indica resposta truncada
    "invalid_source_indices": [int] // fontes citadas que não existiam
  },
  "retrieval": {
    "returned_count", "used_count", "above_threshold_count",
    "max_score", "threshold"
  },
  "config": { ... },                // todas as chaves efetivas da requisição
  "timings": {
    "query_s", "retrieval_s", "generation_s", "total_s",
    "prompt_tokens", "completion_tokens", "tokens_per_s", "load_duration_s"
  },
  "debug": { ... } | null,          // só quando pedido
  "provenance": {                   // quem respondeu, desta vez (desde 25/09)
    "attendant": { "provider", "model", "model_version", "thinking", "fallback_from" },
    "query_stage": { "rewriting", "multi_query", "hyde", "calls": [ { "step", "provider", "fallback_from" } ] }
  }
}
```

"Apenas os trechos que o classificador viu" vale ao pé da letra desde 25/09:
um trecho que não coube no teto de 4.000 caracteres do bloco de contexto não
é fonte nem conta em `used_count`.

**Quando o atendente não responde**, a API devolve **503** com
`{"code": "attendant_unavailable" | "quota_exhausted", "details": {"provider",
"model", "reason"}}`. O sistema nunca troca de modelo em silêncio: com
`ATTENDANT_FALLBACK=ollama`, a resposta vem pelo modelo local e diz isso em
`provenance.attendant.fallback_from` e no texto.

Três campos merecem explicação:

- **`json_parsed` e `schema_valid` são separados** de propósito. Na medição de
  04/05, 97 das 98 respostas não eram JSON; depois da correção, passaram a ser
  JSON mas com campos errados. São dois problemas diferentes e viram duas
  métricas diferentes.
- **`invalid_source_indices`** guarda citações que o modelo inventou. Elas não
  aparecem para o tutor, mas precisam ser contadas: é a métrica de ancoragem.
- **`config`** é o manifesto da requisição. O runner grava isso em cada linha,
  então uma rodada registra o que **de fato** rodou, e não o que foi pedido.

## 4. Chaves de liga/desliga — todos → runner

Enviadas em `options` na requisição, ou definidas no `.env` como padrão. O que
vier na requisição vence; o que vier vazio usa o padrão.

| Chave | Dono | Efeito |
|---|---|---|
| `query_rewriting_enabled` | B1 | Reescreve o relato antes de buscar |
| `multi_query_enabled` | B1 | Gera variações da consulta |
| `hyde_enabled` | B1 | Gera um documento hipotético como consulta extra |
| `retrieval_enabled` | B2 | Desligado = **LLM puro**, a linha de base da ablação |
| `retrieval_mode` | A | `vector` (padrão desde 25/09: similaridade pura, sem rota, reranker, âncoras nem veto de espécie) ou `routed_rerank` (o caminho até 24/09) |
| `context_top_k` | B2 | Quantos trechos vão ao prompt (padrão 3) |
| `context_min_score` | B2 | Score mínimo para um trecho entrar no prompt. **Padrão 0,0 desde 25/09**: com as fichas, as 3 mais próximas entram sempre. A porta de 0,72 é a da base acadêmica (`ACADEMIC_CONTEXT_MIN_SCORE`, presets `hoje_academico_*` e `fichas_com_porta_0_72`). `RetrievalInfo` ecoa o corte aplicado e a trava `used_below_min_score` |
| `rewritten_hint_enabled` | B2 | Passa também a versão reescrita ao classificador |
| `attendant_provider` | B2 | `gemini` (padrão desde 25/09) ou `ollama` |
| `llm_model` | B2 | O modelo local desta requisição (com `attendant_provider=ollama`) |
| `think` | B2 | Se o modelo local "pensa" antes de responder (padrão falso) |
| `prompt_version` | B2 | `v1_grounded` ou `v0_legacy` |
| `structured_output_mode` | B2 | `schema` ou `json` |
| `temperature`, `seed`, `num_predict` | B2 | Parâmetros de geração |
| `cot_enabled`, `cot_position` | B2 | Chain-of-Thought (rodada 7 do João): o raciocínio antes (`first`) ou depois (`last`) da classificação |
| `self_refine_enabled` | B2 | **Ainda não implementado**: erro 400 |

Duas regras de comportamento:

- **Chave desconhecida devolve 422**, e chave não implementada devolve 400. Um
  erro de digitação no runner precisa falhar alto: aceito em silêncio,
  produziria uma rodada que mediu a configuração padrão sem ninguém notar.
- **Sem busca, as chaves do B1 são desligadas automaticamente** e a resposta
  ecoa isso. Não há consulta a otimizar sem recuperação.

## 5. Endpoints

| Rota | Dono | Situação |
|---|---|---|
| `POST /chat/` | B2 | Triagem completa |
| `POST /search/` | A | Busca pura, sem classificação e sem corte. Aceita `mode` (`vector`, o padrão, ou `routed_rerank`) |
| `POST /voice/` | B1 | Transcrição de áudio. Campo `audio` (multipart). Recusa o que não é áudio (415) e acima de `MAX_AUDIO_UPLOAD_MB` (413); o arquivo é gravado com nome gerado no servidor e apagado após a resposta |
| `GET /health/` | — | Verificação de saúde |
| `GET /health/fingerprint` | B2 | Identidade da versão que respondeu: modelo com digest, hash dos prompts e do molde do bloco de contexto, o atendente (provedor, troca permitida, modelos, se a chave do Gemini está configurada — nunca a chave), os padrões (incluindo `retrieval_mode`, `think` e as flags do tradutor), os nomes das configurações vindas do ambiente e, da base vetorial, a contagem, o hash dos ids (**recorte**), o hash do conteúdo (**texto e metadados**), a **receita** do embedding lida do manifesto da coleção ativa e os parâmetros de chunking. O runner grava no manifesto de cada rodada e o `compare` avisa quando algo difere |
| `POST /tutors/`, `GET /tutors/{id}`, `GET /tutors/{id}/pets` | B1 | Cadastro do tutor (Supabase). Em `real`, exige sessão tutor e vínculo `tutors.user_id`; em `demo`, preserva a compatibilidade legada |
| `POST /pets/`, `GET /pets/{id}`, `PATCH /pets/{id}` | B1 | Cadastro do pet (Supabase). Em `real`, valida o titular pelo tutor vinculado. `pet_id` em `POST /chat/` injeta o cadastro no prompt |
| `GET /conversations/{id}` | B1 | Histórico no MongoDB; em `real`, somente o tutor titular |
| ~~`POST /triagem`~~ | — | **Removida.** Era o classificador antigo, sem RAG |

### Segunda etapa (contrato v1)

As rotas abaixo usam `Authorization: Bearer <token>`, exceto descoberta e
geocodificação. Em `demo`, o token é emitido por `POST /auth/demo` e só
representa personas fictícias. Em `real`, `POST /auth/login` valida Supabase
Auth. Um ID no corpo ou na URL nunca substitui a sessão.

| Rota | Acesso | Função |
|---|---|---|
| `POST /auth/demo` | público, só demo | sessão fictícia explícita |
| `POST /auth/signup`, `POST /auth/login` | público, só real | Supabase Auth |
| `POST /clinics/search` | público | lista pública por localização |
| `POST /clinics/geocode` | público | alternativa manual à geolocalização |
| `POST /clinics/register` | conta clínica | cria cadastro institucional pendente |
| `POST /referrals/` | tutor | snapshot `triage_snapshot.v1`, consentimento e idempotência |
| `GET /referrals/`, `GET /referrals/{id}` | proprietário | lista/detalhe filtrado por tutor ou clínica |
| `POST /referrals/{id}/status` | conforme transição | máquina de estados e evento auditável |
| `POST /referrals/{id}/messages` | proprietário | mensagem humana persistente |
| `POST /referrals/{id}/close-chat` | proprietário | encerra o canal |
| `GET /referrals/dashboard` | clínica verificada | indicadores e fila da própria unidade |

O snapshot preserva relato original, classificação, justificativa, sinais,
recomendação, resumo revisado, pet e somente o contato consentido. A resposta
de descoberta informa `source`, `participant`, `verified` e
`digital_referral_enabled`; somente o último habilita envio.

**Sobre `POST /chat/`:** três campos opcionais e independentes —
`tutor_id`, `pet_id`, `conversation_id`. `pet_id` busca o cadastro do pet e
acrescenta um bloco "Dados cadastrais do animal" ao prompt, separado do
relato do tutor. Qualquer um dos três presentes já grava o turno no
histórico de conversa e a resposta devolve `conversation_id` para o
próximo turno reaproveitar. Sem nenhum dos três (o caso do runner de
avaliação), nada disso roda — comportamento idêntico a antes desta
extensão existir. Em modo `real`, usar qualquer um desses identificadores
exige Bearer de tutor e prova de titularidade; a pré-triagem anônima sem IDs
continua pública. Sem Supabase configurado, `pet_id` devolve 503; sem
MongoDB, o histórico simplesmente não é gravado (`conversation_id` volta
`null`), sem quebrar a triagem.

---

## Pendências

### Complemento: workspace da POC (25/09/2026)

O contrato científico `POST /chat/` permanece. A interface nova usa:

| Rota | Acesso / contrato |
| --- | --- |
| `GET /auth/config` | Configuração pública e chave web Maps; nunca chave servidor |
| `GET /auth/me`, `POST /auth/logout` | Validar/revogar sessão |
| `GET/POST /workspace/pets`, `PUT /workspace/pets/{id}` | Tutor proprietário; nome/espécie obrigatórios |
| `GET/POST /workspace/conversations` | Lista paginada/criação; `pet_id` opcional |
| `GET/PATCH /workspace/conversations/{id}` | Histórico/troca de animal do titular |
| `POST /workspace/conversations/{id}/messages` | `content` + `request_id`; 202, persistência antes da análise |
| `GET /clinics/participants` | Unidades habilitadas apropriadas ao tipo de conta |
| `PUT /referrals/{id}/location` | Tutor proprietário; consentimento; só a caminho |

`WORKFLOW_MODE=poc` protege também recursos pessoais legados. Identidade local
ou Supabase por `AUTH_PROVIDER`; acesso acadêmico é opt-in separado, com tokens
opacos/revogáveis no modo POC, não `demo:ID`.

Fora do modo legado demo, envio exige `conversation_id` do titular; conteúdo
automático vem do servidor. `pet` pode ser null; `share_full_conversation=false`
por padrão. Quando true, envia cópia autorizada no instante do encaminhamento.
Posição é ocultada após 120 s sem atualização. Dashboard aceita `offset`,
`limit`, `active_only`; indicadores abrangem todos os casos da unidade.
Detalhes no [guia](poc-utilizavel.md).

### Backlog entre trilhos

As pendências entre trilhos vivem no [backlog do projeto](../evidencias/backlog.md),
com detalhe, responsável, prioridade e status — este documento trata só das
interfaces. Os itens que tocam estes contratos, hoje:
[B-04](../evidencias/backlog.md#b-04) (seed na etapa de consulta),
[B-10](../evidencias/backlog.md#b-10) (a consulta reescrita não vai ao
índice), [B-12](../evidencias/backlog.md#b-12) (ingestão em máquina nova),
[B-17](../evidencias/backlog.md#b-17) (`RERANK_TOP_K` × `CONTEXT_TOP_K`),
[B-19](../evidencias/backlog.md#b-19) (arquivos que ainda apontam para a
rota removida) e [B-53](../evidencias/backlog.md#b-53) (o vocabulário de
`species` nos sidecars não é fechado).
