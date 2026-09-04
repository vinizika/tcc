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

Hoje o pipeline monta essa lista assim, na ordem:

1. a consulta reescrita, **se** o multi-query estiver desligado;
2. as variações geradas pelo multi-query, **se** ligado;
3. o documento hipotético do HyDE, **se** ligado.

Se o multi-query devolver lista vazia, a consulta reescrita entra no lugar —
buscar com lista vazia devolveria zero documentos e pareceria falha da
recuperação.

**Ponto em aberto para o B1.** Hoje, com o multi-query ligado, a consulta
reescrita **não** vai ao índice: só as três variações e o HyDE. Proposta: usar
`[reescrita] + variações`, sem duplicatas. Precisa de decisão do dono.

## 2. Documento recuperado — A → B2

O que a busca devolve, por trecho:

| Campo | Uso |
|---|---|
| `chunk_id` | Identifica o trecho exato; usado para marcar quais embasaram a resposta |
| `title` | Vai ao prompt e aparece na resposta ao tutor |
| `content` | O texto que entra no prompt |
| `source` | Arquivo de origem, exibido junto do título |
| `score` | Similaridade; decide o corte e vai nas métricas |

**Estável.** Acrescentar campo é seguro; renomear ou remover quebra o
classificador. Sugestão de melhoria: expor também `topic` e `species`, que já
existem nos metadados dos trechos e permitiriam citações mais precisas.

## 3. Resposta de triagem — B2 → runner e frontend

O que `POST /chat/` devolve. **`answer` continua sendo texto** para o frontend
atual não quebrar; quem consome por programa deve ler de `triage`.

```
{
  "answer": str,                    // markdown pronto para exibir
  "sources": [                      // apenas os trechos que o classificador viu
    { "title", "source", "score", "chunk_id", "cited" }
  ],
  "triage": {
    "classificacao": "EMERGENCIA" | "NAO_EMERGENCIA" | "INCERTO",
    "justificativa": str,
    "sinais_de_alerta": [str],
    "recomendacao": str,
    "fontes": [ { "index", "chunk_id", "title", "source" } ],
    "raciocinio": str | null,       // preenchido quando o CoT existir (E4)
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
  "debug": { ... } | null           // só quando pedido
}
```

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
| `context_top_k` | B2 | Quantos trechos vão ao prompt |
| `context_min_score` | B2 | Score mínimo para um trecho entrar no prompt |
| `rewritten_hint_enabled` | B2 | Passa também a versão reescrita ao classificador |
| `prompt_version` | B2 | `v1_grounded` ou `v0_legacy` |
| `structured_output_mode` | B2 | `schema` ou `json` |
| `temperature`, `seed`, `num_predict` | B2 | Parâmetros de geração |
| `cot_enabled` | B2 | **Ainda não implementado**: erro 400 |
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
| `POST /search/` | A | Busca pura, sem classificação |
| `POST /voice/` | B1 | Transcrição de áudio |
| `GET /health/` | — | Verificação de saúde |
| ~~`POST /triagem`~~ | — | **Removida.** Era o classificador antigo, sem RAG |

---

## Pendências combinadas

Coisas que dependem de decisão ou ação de outro trilho.

1. **Fixar temperatura e seed na etapa de consulta** (B1). As três chamadas
   usam o padrão do Ollama, com seed aleatória, então as consultas mudam a
   cada execução e duas rodadas de avaliação com RAG não são comparáveis. São
   três linhas, com o que já existe em `core/ollama.py`.
2. **Decidir se a consulta reescrita vai ao índice** junto das variações do
   multi-query (B1) — item 1 acima.
3. **`RERANK_TOP_K` × `CONTEXT_TOP_K`.** A primeira é do trilho A e hoje não é
   usada. Quando o re-ranking real entrar e cortar em 3, pedir 5 trechos de
   contexto devolverá 3 em silêncio. Combinar quem manda.
4. **Ingestão em máquina nova** (A). O banco vetorial não é versionado: um
   clone limpo tem a base vazia e o RAG não recupera nada até rodar
   `python -m app.database.ingest_documents` uma vez. Falta no README.
5. **Arquivos que ainda apontam para a rota removida**, fora do backend:
   `frontend/streamlit_app.py` (interface antiga, substituída por `main.py`),
   `mock/streamlit_app_mock.py` e trechos do `README.md`. O runner de
   avaliação (`scripts/evaluate_accuracy.py`) também aponta para lá, e será
   reescrito na próxima entrega do B2.
