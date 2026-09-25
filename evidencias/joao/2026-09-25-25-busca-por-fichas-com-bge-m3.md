# A busca nas fichas, com o bge-m3 e as 3 mais próximas

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2, olhando o sistema inteiro
(o embedding, a ingestão e a busca são do trilho A; o tradutor, do B1) ·
**Rodada:** 24 · **Commits:** este

> Segunda rodada de código. Leva ao sistema a busca da
> [rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md): o relato cru vai
> ao bge-m3, que compara com as 61 fichas de busca, e as 3 mais próximas
> entram no prompt, **sempre**, sem porta, sem roteador e sem reranker. A
> coleção acadêmica continua abrindo com o MiniLM, como braço "hoje" da
> ablação. O portão é a busca da API devolver as mesmas 3 fichas que a autópsia
> mediu, caso a caso.

## O que foi feito

1. **Receitas de embedding** (`embedding_config.py`): cada coleção guarda no
   manifesto qual receita a construiu — `minilm-academic-v1` (a de hoje, com o
   mesmo hash `1a93e1e7…`) ou `bge-m3-fichas-v1` (bge-m3 na revisão fixada
   `5617a9f6…`, 1024 dimensões, até 512 tokens, sem recorte em trechos).
2. **O cliente do Chroma escolhe o embedding pelo manifesto** da coleção ativa,
   antes de abri-la, e confere a coleção contra a receita que o manifesto
   declara. Voltar para a coleção acadêmica (`--rollback`) volta a abrir com o
   MiniLM, sem tocar em código.
3. **O perfil `fichas` na ingestão**: 61 registros, id `ficha__<topic>`, o
   texto de busca como documento vetorizado (sem prefixo) e o texto de leitura
   no `metadata.body` (é ele que chega ao prompt), com título de leitura,
   título para o tutor, espécie, urgência e referências. Recusa texto acima de
   512 tokens.
4. **A coleção das fichas versionada** em `backend/chroma_db/` (61 × 1024), com
   manifesto e ponteiro ativo, e `CHROMA_PATH = "chroma_db"`: um clone limpo
   sobe com a busca nova, sem passo manual ([B-57](../backlog.md#b-57)). O
   compose ganha um volume para o cache do Hugging Face.
5. **`retrieval_mode`**: `vector` (novo padrão: busca vetorial pura, as mais
   próximas em ordem de similaridade) ou `routed_rerank` (o caminho de hoje:
   roteador lexical, reranker, âncoras, veto de espécie). Nas settings, nas
   opções da requisição, na configuração efetiva, no `/search`, no runner da
   régua e no runner de avaliação.
6. **Os padrões mudam**: `vector`, corte de relevância 0,0 (as 3 mais
   próximas, sempre), top 3, e o tradutor (reescrita, multi-query e HyDE)
   desligado. O corte de 0,72 continua existindo como constante do braço
   acadêmico e num preset (`fichas_com_porta_0_72`); os presets antigos passam
   a dizer explicitamente o modo e o corte que sempre usaram.

## Por quê

- A autópsia mediu que, nas fichas, o bge-m3 põe a ficha certa em 1º em ~80%
  dos casos da prova + régua, contra ~20% do MiniLM, e que as 3 mais próximas
  sem porta ganham da porta nos relatos de quem não viu o mapa (qwen: 21 → 7
  emergências perdidas, p = 0,0005)
  ([rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md)). O tradutor
  piora a busca nas fichas ([rodada 17](2026-09-24-18-tradutor-desligado.md)).
- **Trocar só as constantes do embedding quebraria a coleção acadêmica**, que
  foi indexada com o MiniLM e passaria a ser consultada com vetores de outro
  modelo. Guardar a receita no manifesto e escolher o embedding por ela é o que
  deixa os dois braços da ablação abrirem com o próprio modelo.
- **Um clone limpo hoje não reproduz nenhum número com RAG** sem passos
  manuais ([B-57](../backlog.md#b-57)).

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| As constantes antigas (`EMBEDDING_MODEL_NAME` etc.) continuam sendo a receita acadêmica | O recorte em trechos da coleção acadêmica usa o tokenizer do MiniLM; uma reindexação dela tem de continuar produzindo os mesmos trechos |
| Manifesto sem `recipe_key` (os antigos) resolve para a receita pelo par modelo + revisão | As 13 coleções já versionadas não têm o campo; elas continuam abrindo como antes |
| No modo `vector`, sem roteador **e sem veto de espécie** | É o que a autópsia mediu. O veto de espécie mora no reranker e só vale no braço roteado |
| A coleção entra no repositório (o `chroma.sqlite3` versionado) | É o que o time já faz com as candidatas, e o critério do B-57 é o clone limpo subir sem passo manual. O custo é mais uma versão do arquivo binário (~73 MB) no histórico — registrado para o João decidir de manhã |
| O `/search` passa a obedecer o `retrieval_mode` (padrão `vector`) | A régua mede a busca que o sistema usa; o modo roteado continua disponível por parâmetro |
| Corte padrão 0,0, e não "sem corte" como caso especial | O pipeline já tem o corte; com 0,0 ele deixa passar as 3 mais próximas, que é a decisão |

## Resultado esperado

_Escrito antes de rodar._

- **R0 (funcional):**
  - o retrato da API mostra a coleção de fichas: 61 registros, bge-m3, receita
    `bge-m3-fichas-v1`;
  - `--rollback` para `…388f518d` abre com 3.481 trechos e o MiniLM, e volta;
  - `/search` com "meu cachorro comeu chocolate e está tremendo" traz
    `chocolate_toxicosis` em 1º.
- **R1 (réplica da busca):** `/search` em modo `vector`, as 3 primeiras, nos
  lotes da autópsia (dev, calibração, régua, as duas metades dos relatos
  independentes e o piloto: 296 casos), reproduz os trios de
  `_trabalho/ctx/bgecl_leitura_mapa_top3.json` em **pelo menos 99% dos casos**
  (na ordem), e os agregados medidos (ficha certa em 1º / entre as 3):
  prova + régua 107/129 e 123/129; independentes 74/122 e 94/122; piloto 16/40
  e 32/40 — com tolerância de ±1 caso.
- **Suíte** verde, com os testes que mudam de padrão atualizados e os novos
  (receitas, perfil de fichas, modo vetorial).
- **Sem R1 dentro da tolerância, a rodada 26 (a réplica da decisão) não roda.**

## Resultado obtido

**A busca do código reproduz a da autópsia, exata.**

**R0, funcional** (API local, `uvicorn`, 03h16):

| Checagem | Resultado |
|---|---|
| `/health/fingerprint` | coleção `veterinary_documents__20260925T061349534255Z__280baf13`, **61 registros**, `BAAI/bge-m3` na revisão `5617a9f6…`, receita `bge-m3-fichas-v1` (`3bfd745d…`), perfil `fichas`, conteúdo `9274aff4…`, manifesto `82992d43…`; padrões `vector`, corte 0,0, top 3, tradutor desligado |
| `--rollback` para `…388f518d` | abre com **3.481 trechos e o MiniLM**, escolhido pelo manifesto; "meu cachorro comeu chocolate e está tremendo" → 3 trechos de `chocolate_toxicosis` |
| rollback de volta | 61 fichas, bge-m3 |
| `/search` "meu cachorro comeu chocolate e está tremendo" | **`chocolate_toxicosis` em 1º** (0,761), depois `hypoglycemia_toy_puppy` e `grape_xylitol_toxicosis` |
| clone limpo da branch, sem passo manual | abre a coleção das fichas pelo ponteiro versionado; "minha gata não consegue fazer xixi…" → `urethral_obstruction` em 1º ([B-57](../backlog.md#b-57)) |

**R1, a réplica da busca** (`POST /search/`, modo `vector`, as 3 primeiras,
296 casos; `rodada_noturna/scripts/r1_busca.py` do diário):

| | Esperado (autópsia) | Obtido |
|---|---|---|
| Trios iguais, na ordem | ≥ 99% | **296 de 296** |
| Prova + régua: ficha certa em 1º / entre as 3 (129) | 107 / 123 | **107 / 123** |
| Relatos independentes (122) | 74 / 94 | **74 / 94** |
| Piloto da prova 2 (40) | 16 / 32 | **16 / 32** |
| Maior diferença de nota nos trios | — | 0,0001 |

A régua do repositório, em modo `vector` (66 casos,
[`data/retrieval/cited/20260925-031753_fichas_bge_m3_vector`](../../data/retrieval/cited/20260925-031753_fichas_bge_m3_vector/report.md)):

```
$ python scripts/run_retrieval_eval.py --name fichas_bge_m3_vector --mode vector
  protocolo certo em 1º : 0.8788
  MRR                   : 0.9315
  acima do limiar       : 0.2576
  1º lugar mais comum   : urethral_obstruction (3/66)
```

O "acima do limiar" (0,70) de 26% é o motivo de não haver porta: com o bge-m3
nas fichas, três quartos das fichas certas ficam abaixo de 0,70 e mesmo assim
estão em 1º.

**Suíte:** backend 242 → **262** (20 novos: receitas, perfil de fichas numa
coleção Chroma real, modo vetorial, padrões novos, `/search` com modo);
scripts 209.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/database/embedding_config.py` | `EmbeddingRecipe`, `RECIPES`, `PROFILE_RECIPES`, `recipe_for`, `recipe_for_profile`, `recipe_from_manifest`; as constantes antigas continuam sendo a receita acadêmica |
| `backend/app/database/chroma_client.py` | uma função de embedding por receita; `get_collection()` lê o manifesto antes de abrir; integridade conferida contra a receita do manifesto; `create_staging_collection(..., recipe=)`; `active_recipe()` |
| `backend/app/database/ingest_documents.py` | perfil `fichas`: `prepare_fichas_ingestion`, `stage_fichas`, manifesto com `recipe_key`; `recipe_key` também no manifesto acadêmico |
| `scripts/run_ingestion_cycle.py` | `fichas` nas opções |
| `backend/app/core/config.py`, `backend/app/constants/pipeline.py` | `CHROMA_PATH = "chroma_db"`, `RETRIEVAL_MODE = "vector"`, corte padrão 0,0 (`ACADEMIC_CONTEXT_MIN_SCORE = 0.72`), tradutor desligado |
| `backend/app/schemas/triage.py`, `backend/app/pipeline/config_resolver.py` | `retrieval_mode` nas opções e na configuração efetiva |
| `backend/app/pipeline/chat_pipeline.py` | `_retrieve` em modo `vector`: sem rota, sem reranker, ordem por similaridade |
| `backend/app/schemas/search.py`, `backend/app/services/search_service.py`, `backend/app/api/search.py` | `/search` com `mode` |
| `backend/app/services/fingerprint_service.py` | receita, modelo e revisão lidos do manifesto ativo; `retrieval_mode` e as três flags do tradutor nos padrões |
| `scripts/run_retrieval_eval.py`, `scripts/run_evaluation.py` | `--mode`; `retrieval_mode` nas opções válidas |
| `scripts/presets.json` | `fichas_com_porta_0_72`; os presets antigos com modo e corte explícitos |
| `docker-compose.yml` | volume `hf_cache` e `HF_HOME` |
| `backend/chroma_db/` | a coleção das fichas, o manifesto, o recibo e o **ponteiro ativo** |
| `backend/tests/` | `test_embedding_config.py` e `test_fichas_ingestion.py` (novos); `test_chat_pipeline.py`, `test_api_search.py`, `test_config_resolver.py`, `test_api_chat.py`, `conftest.py` |
| `data/retrieval/cited/20260925-031753_fichas_bge_m3_vector/` | a rodada da régua em modo `vector` |

Commits: `67e666a` (abre a rodada: receitas e perfil, trilho A), `a00ff88`
(modo vetorial e padrões, trilhos A e B1), `cd15c3d` (a coleção versionada) e
este.

## Observações

**1. Abrir o Chroma versionado altera os arquivos versionados**
([B-73](../backlog.md#b-73)). Num clone limpo, a primeira consulta muda o
`chroma.sqlite3` (e, na coleção nova, o `length.bin` do índice), sem mudar o
conteúdo da coleção. Não é desta rodada: em `2d37a5e`, consultar a coleção
acadêmica faz o mesmo. Quem roda o backend e dá `git add -A` commita um banco
alterado sem querer.

**2. O `chroma.sqlite3` versionado cresce de 72,5 para 73,0 MB.** É mais uma
versão do arquivo binário no histórico do Git. Alternativa, se o time
preferir: não versionar a coleção e gerá-la na subida do backend a partir do
`fichas.json` (61 fichas, ~1,5 min de CPU). Fica para decisão.

**3. O `atomic_write_json` grava CRLF no Windows** (manifesto, recibo e
ponteiro saíram assim). Normalizados para LF, como os manifestos antigos;
anotado no [B-71](../backlog.md#b-71).

**4. O Ollama desta máquina é o 0.34.4** (o registro da autópsia fala em
0.34.3). Não afeta a busca; entra na conferência da réplica do atendente
(rodadas 25 e 26), na ordem de depuração do plano.

**5. O veto de espécie saiu do caminho padrão junto com o reranker.** Um relato
de cachorro pode trazer uma ficha só de gato entre as 3 (ex.: permetrina em
gato). É o que a autópsia mediu, e a ficha de leitura diz a espécie; fica
anotado para a ablação.

## Deixado para depois

- **Decidir se a coleção fica versionada** ou é gerada na subida
  ([B-73](../backlog.md#b-73)).
- **A régua nas fichas como instrumento oficial**, com linha de base citada e
  `--recall-k 3` (a rodada citada aqui mede o 1º lugar e o MRR).
- **O `benchmark_retrieval_variants.py`** ainda abre a coleção com a função de
  embedding padrão (a acadêmica); precisa ler a receita do manifesto antes de
  ser usado nas fichas.

## Próximo passo

A [rodada 25](2026-09-25-26-resposta-com-ficha-e-fonte.md): a resposta cita a
ficha e o documento com o título real, o corte de 4.000 caracteres para de
listar como fonte o que o modelo não viu, e a procedência vai na resposta.
