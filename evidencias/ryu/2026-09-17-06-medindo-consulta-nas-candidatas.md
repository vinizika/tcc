# Medindo consulta nas candidatas experimentais (B-09, B-10)

**Data:** 17/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 6 · **Commit:** este

> As três técnicas de consulta (reescrita, multi-query, HyDE) nunca puderam
> ser medidas isoladamente: a régua de recuperação sempre rodou contra
> `POST /search/`, que só enxerga a coleção **ativa** — e até 16/09 a ativa
> sempre teve 0 chunks. Os três lotes experimentais do trilho A (14–16/09)
> deixaram coleções candidatas em staging, com conteúdo real, prontas para
> consulta direta. Esta rodada usa isso pela primeira vez.

## O que foi feito

Um instrumento novo,
[`backend/app/database/measure_query_techniques.py`](../../backend/app/database/measure_query_techniques.py),
que aponta o `RetrievalClient` de produção para uma coleção candidata — sem
tocar o ponteiro ativo, sem alterar `POST /search/` — e roda cinco arranjos
de consulta sobre um conjunto de casos:

| Arranjo | O que é |
|---|---|
| `sem_consulta` | o relato cru, sem nenhuma transformação — a linha de base |
| `reescrita` | só `QueryClient.rewrite()` |
| `multi_query` | reescrita + Multi-Query, **do jeito que o pipeline roda hoje** — a reescrita some da lista quando há variações (é o B-10) |
| `fundido` | `[reescrita] + variações`, sem duplicatas — o candidato a correção do B-10 |
| `pipeline_completo` | multi-query + HyDE, a configuração padrão do `.env` até esta rodada |

Rodado contra as três coleções experimentais do trilho A, nos 9 casos da
régua que cobrem os tópicos de cada lote (b19–b21, b22–b24, b14/b16/b17).

## Por quê

B-09 está aberto desde 04/09 pedindo exatamente isto: medir cada técnica de
consulta ligada e desligada, e desligar por padrão a que não ajudar. B-10
pede uma decisão sobre fundir reescrita e multi-query. Os dois estavam
bloqueados pela mesma coisa — nunca houve base real para medir contra.

## Um obstáculo encontrado no caminho: o snapshot estava no lugar errado

Antes de medir qualquer coisa, `ChromaDBClient._get_strict_collection`
recusou abrir as três candidatas: `ActiveCollectionUnavailableError`. O
motivo não era falta de conteúdo — é que `settings.CHROMA_PATH` (`data/chroma`,
resolvido para `backend/data/chroma/`) e o caminho onde os três lotes
gravaram o snapshot versionado (`backend/chroma_db/`) são **pastas
diferentes**. Um `docker compose up` normal nunca veria as candidatas.
Contornei com `ChromaDBClient.configure(path="/app/chroma_db")` só para
este script de medição — não mudei a configuração do sistema, porque não é
decisão minha qual dos dois caminhos é o certo. Registrado como
[B-57](../backlog.md#b-57), prioridade Alta, para o trilho A decidir.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Reaproveitar `RetrievalClient.retrieve()` de produção, via monkeypatch de `ChromaDBClient.get_collection` só no processo do script | É o único jeito de herdar o merge de multi-query e o corte de relevância exatamente como o sistema real aplica, sem reimplementar essa lógica num script separado que poderia divergir |
| 2 | Cinco arranjos, não três | `fundido` isola o efeito da fusão (B-10) do efeito do HyDE; sem ele, não dava para saber se `pipeline_completo` ganha ou perde por causa do multi-query ou do HyDE |
| 3 | Medir por lote, não só agregado | Uma média sobre 9 casos heterogêneos esconderia se o efeito é uniforme ou vem de um lote só — e veio |
| 4 | Não alterar o ponteiro ativo nem ativar nenhuma candidata | Não é o objetivo desta rodada, e a porta de decisão dos lotes já reprovou as três (encontrabilidade abaixo de 70%) |

## Resultado esperado

_Escrito antes de rodar, com base no que a literatura de RAG e o próprio
B-09 já suspeitavam._

Esperava que multi-query e HyDE aumentassem a nota de similaridade (é o que
a rodada 4 do B2 já tinha visto: "a etapa de consulta elevou o score de
0,574 para 0,680"), e que ao menos uma das três técnicas melhorasse
Precision@1/MRR sobre o relato cru — não tinha hipótese sobre qual.

## Resultado obtido

### Agregado (9 casos)

| Arranjo | Precision@1 | MRR | Recall@5 | Nota média | % casos ≥ 0,70 |
|---|---:|---:|---:|---:|---:|
| `sem_consulta` | 0,667 | 0,744 | 0,889 | 0,515 | 0% |
| `reescrita` | 0,556 | 0,657 | 0,889 | 0,590 | 22% |
| `multi_query` (hoje) | 0,667 | 0,704 | 0,778 | 0,676 | 44% |
| `fundido` (B-10) | 0,667 | 0,704 | 0,778 | **0,686** | **56%** |
| `pipeline_completo` (.env até hoje) | 0,556 | 0,648 | 0,778 | 0,697 | 56% |

**O padrão que se repete em toda coluna:** cada técnica adicionada aumenta a
nota de similaridade, mas nenhuma supera o relato cru em Precision@1/MRR —
o relato cru tem a melhor colocação de todos os arranjos. É a mesma
assinatura que a rodada 4 do B2 já via em outro ângulo (score sobe,
qualidade da resposta final não acompanha).

### Por lote — para não deixar a média esconder o que importa

| Lote | `sem_consulta` P@1/MRR | `reescrita` | `multi_query` | `fundido` | `pipeline_completo` |
|---|---:|---:|---:|---:|---:|
| 1 — intoxicações (b19-b21) | 0,0 / 0,233 | 0,0 / 0,306 | 0,0 / 0,111 | 0,0 / 0,111 | 0,0 / 0,111 |
| 2 — curadoria (b22-b24) | **1,0 / 1,0** | 0,667 / 0,667 | **1,0 / 1,0** | **1,0 / 1,0** | 0,667 / 0,833 |
| 3 — emergências (b14,16,17) | **1,0 / 1,0** | 1,0 / 1,0 | 1,0 / 1,0 | 1,0 / 1,0 | 1,0 / 1,0 |

Três leituras diferentes, uma por lote:

- **Lote 1 é ruim para todo mundo.** Nenhum arranjo acerta o top-1 — nem o
  relato cru. Consistente com o que a própria evidência do lote 1 já
  registrou: as fontes de medicamento humano e organofosforado são gerais
  demais para o relato específico. Não é um problema de consulta; é
  cobertura, e nenhuma técnica de consulta resolve fonte fraca.
- **Lote 3 é bom para todo mundo.** Os quatro arranjos com transformação
  empatam em 1,0/1,0 com o relato cru — a distância aumenta, a ordem não
  piora. Nenhum dano aqui.
- **Lote 2 é onde a diferença aparece.** `sem_consulta`, `multi_query` e
  `fundido` empatam no topo (1,0/1,0). `reescrita` sozinha e
  `pipeline_completo` (que soma HyDE) **caem para 0,667/0,833** — as duas
  únicas variações que incluem uma etapa sem contrapeso do multi-query.

### O que isso decide

**B-09 — HyDE não se paga.** Em nenhum dos três lotes o HyDE melhorou
Precision@1 ou MRR sobre `fundido` (sem HyDE); no lote 2, piorou. Ele
segue sendo a chamada mais lenta da etapa de consulta (rodada 3 do B2:
"HyDE... 66 a 154 palavras... 30% de instabilidade") e já era conhecido por
inventar diagnóstico sem âncora. `HYDE_ENABLED` passou a `False` por
padrão — decisão do dono, contrato item 4 do `CONTRATOS.md`. Continua
implementado e mensurável: liga por requisição ou pelo preset `rag_query`.

**B-10 — fundir reescrita e multi-query é seguro, e nunca fica pior.**
`fundido` empata ou bate `multi_query` (comportamento atual) em toda
métrica, em todos os lotes, e tem a maior taxa de casos acima do corte de
relevância do conjunto inteiro (56%, empatado com `pipeline_completo` — mas
sem precisar do HyDE para chegar lá). Implementado em `_build_queries`
(`chat_pipeline.py`): a lista de consultas agora sempre começa pela
reescrita, com as variações do multi-query entrando depois sem duplicar.

**Reescrita sozinha é a única técnica isolada que perde do relato cru em
dois dos três lotes.** Não vira mudança de configuração nesta rodada — o
B-08 (reescrita adiciona julgamento clínico) já documentava um sintoma
parecido, e vale investigar junto quando houver mais casos.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/database/measure_query_techniques.py` | **novo** — instrumento de medição contra coleção candidata |
| `backend/app/pipeline/chat_pipeline.py` | `_build_queries` funde reescrita + variações (B-10) |
| `backend/app/core/config.py` | `HYDE_ENABLED` padrão `False` (B-09) |
| `.env.example` | mesma mudança, documentada |
| `docs/CONTRATOS.md` | contrato 1 atualizado: "ligado" agora é superconjunto de "desligado" |
| `backend/tests/test_chat_pipeline.py` | 2 testes novos travando a fusão (com e sem duplicata) |
| `evidencias/backlog.md` | B-09 e B-10 resolvidos; [B-57](../backlog.md#b-57) aberto (caminho do Chroma) |

Testes: backend 203 → **205**.

## Observações

**1. A amostra é pequena, e isso limita o que se pode afirmar.** 9 casos, 3
por lote — o mesmo aviso que a régua já carrega desde a rodada 11 do João
(B-49). O que sustento com confiança é a **direção** (nenhuma técnica supera
o relato cru; HyDE nunca ajuda; fundir nunca piora), não o tamanho exato do
efeito. Vale repetir quando o B-51/ingestão liberar mais casos por tópico.

**2. O achado do lote 1 é sobre cobertura, não sobre consulta.** Nenhuma
técnica de consulta conserta uma fonte geral demais — é o mesmo limite que
a régua de recuperação já mostrou em setembro: a busca separa assunto
quando o documento é específico o bastante, e nenhuma reformulação de
pergunta substitui isso.

**3. O B-57 (caminho do Chroma) é mais urgente do que parece.** Enquanto
`CHROMA_PATH` e o caminho do snapshot divergirem, qualquer ativação futura
de candidata por um comando padrão (`docker compose up`, sem passo manual)
vai continuar batendo numa coleção vazia — e ninguém vai notar até medir de
novo, como eu quase não notei aqui.

## Deixado para depois

**Investigar por que `reescrita` sozinha perde do relato cru** — pode ser o
mesmo mecanismo do B-08 (juízo clínico inserido na reescrita mudando o
vocabulário de um jeito que afasta da base, não aproxima).

**Repetir esta medição quando a base crescer** (mais candidatas, mais casos
por tópico) — 9 casos não sustentam número de artigo, só direção.

**Resolver o B-57** antes de qualquer ativação de candidata — é do trilho A.

## Próximo passo

Com B-09 e B-10 fechados, meus itens abertos que restam são B-07 (latência
da etapa de consulta) e B-08 (juízo clínico na reescrita) — e agora com um
instrumento pronto para medir os dois contra conteúdo real, em vez de
opinião.
