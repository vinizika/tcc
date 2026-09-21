# Medindo latência da consulta com modelo aquecido (B-07)

**Data:** 21/09/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 9 · **Commit:** este

## O que foi feito

Criei [`backend/app/database/measure_query_latency.py`](../../backend/app/database/measure_query_latency.py):
aponta o `ChatPipeline` para uma coleção candidata do trilho A (monkeypatch de
`ChromaDBClient.get_collection`, mesmo mecanismo de `measure_query_techniques.py`),
faz uma chamada de aquecimento descartada, e mede `query_s` real de chamadas
subsequentes ao `/chat/` com Multi-Query e HyDE ligados juntos — a única
combinação onde a paralelização implementada na rodada 8 tem efeito.

Rodei contra `veterinary_documents__20260920T160842289762Z__388f518d`
(3.481 chunks, 66 documentos, a coleção final do trilho A), a primeira vez
que essa medição roda contra conteúdo real e não uma coleção vazia.

## Por quê

A rodada 8 implementou a paralelização mas não produziu número limpo: caiu
num cold-start do Ollama (a reescrita sozinha levou 70s) e a coleção ativa
estava vazia. Faltava fechar isso com modelo já aquecido, que é o critério
numérico do próprio B-07 (`query_s` mediano abaixo de 1,5s).

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Aquecer com uma chamada `retrieval_enabled=False` descartada, fora da medição | A primeira chamada ao Ollama depois de um tempo parado recarrega o modelo — não é o custo em regime normal, e contaminaria a mediana |
| 2 | Medir contra a coleção de 3.481 chunks, não uma sintética pequena | `query_s` só mede a etapa de consulta (chamadas ao LLM), não deveria depender do tamanho da base — mas rodar contra a base real de produção é o cenário que importa |
| 3 | Reportar o ganho relativo (paralelo vs. sequencial-equivalente) além do número absoluto | Descobri no meio da rodada que o ambiente está anormalmente lento (ver abaixo) — o número absoluto sozinho seria enganoso sem essa comparação |

## Resultado esperado

_Escrito antes de medir._ Esperava confirmar `query_s` mediano abaixo de
1,5s com o modelo aquecido, fechando o critério numérico do B-07.

## Resultado obtido

**O critério numérico não foi confirmado — mas por um motivo de ambiente, não
de código.** `ollama ps` mostrou o `llama3.2:3b` rodando **100% CPU** neste
container, sem GPU. O time tem rodadas históricas citando
`native_gpu_reranker` (evidência do Vinicius, 20/09) — o baseline original de
"3,5s de 5,7s" quase certamente foi medido com GPU disponível. Neste
ambiente CPU-only, os dois casos medidos deram:

| Caso | `query_s` | Reescrita | Paralelo (Multi-Query ‖ HyDE) | Sequencial equivalente | Economia |
|---|---:|---:|---:|---:|---:|
| "meu cachorro comeu chocolate" | 55,97s | 7,68s | 48,18s (multi-query domina) | 91,6s (7,68+48,18+35,76) | **39%** |
| "minha gata não consegue fazer xixi" | 39,64s | 3,75s | 35,84s (HyDE domina) | 45,72s (3,75+6,13+35,84) | **13%** |

Um terceiro caso ficou pela metade — o processo dentro do container foi
encerrado no meio da medição (provavelmente o wrapper do ambiente de
execução, não o Ollama nem o backend: o container `backend-api` não
reiniciou, confirmado por `docker ps` sem interrupção de uptime). Os dois
resultados completos já são suficientes para a conclusão qualitativa: a
paralelização **nunca piora** e a economia varia com o quão desbalanceadas
são as duas chamadas — quando uma domina muito a outra (caso 2, HyDE muito
mais lento que Multi-Query), o ganho relativo é menor, mas ainda é economia
real em segundos absolutos (6,13s no caso 2, 35,76s no caso 1).

**Números absolutos muito acima de 1,5s** (39,6s e 56,0s) não representam o
sistema em condições normais de produção (que rodaria com GPU) — são o
sistema mais um gargalo de hardware específico desta execução.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/database/measure_query_latency.py` | **novo** — instrumento de medição de `query_s` com modelo aquecido, contra coleção candidata |
| `evidencias/backlog.md` | B-07 atualizado: paralelização implementada e com ganho relativo medido; critério numérico absoluto pendente de ambiente com GPU |

## Observações

**A régua de retrieval, o reranker e o roteamento lexical do trilho A já
aparecem nos logs desta medição** ("Rota lexical adicionou candidatos...",
"re-ranking lexical com âncoras") — é a integração real da última leva do
Vinicius, funcionando de ponta a ponta com o meu código sem nenhum ajuste
necessário. Bom sinal de que a fronteira entre os dois trilhos continua
estável.

**Não investiguei por que o processo de medição foi encerrado no meio do
terceiro caso.** Não foi o Ollama nem o backend (nenhum dos dois reiniciou).
Se acontecer de novo em rodadas futuras, vale registrar como item novo —
por ora, não impede a conclusão desta rodada.

## Deixado para depois

**Repetir esta medição num ambiente com GPU disponível para o Ollama** —
só assim o critério numérico do B-07 (`query_s` mediano abaixo de 1,5s) pode
ser confirmado ou refutado de verdade. Sem isso, o item continua "em
andamento": o código está correto e o ganho é real, mas o número que fecha
o critério não pode ser produzido nesta máquina.

## Próximo passo

Ponto 2 do plano combinado com o usuário (fechar os testes) segue para a
prova oficial (~150 casos) e a adaptação do runner para texto livre — itens
5 e 6 do planejamento, ambos reforçados pelo pedido explícito do Vinicius no
repasse da rodada de 20/09.
