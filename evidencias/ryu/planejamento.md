# Planejamento do trilho B1 — Consulta

Roteiro do trilho: o que já foi entregue, o que vem a seguir e o que está
travando. O registro detalhado de cada entrega está nas
[rodadas](README.md). O escopo do trilho e as fronteiras com os outros
estão em [`docs/divisao-de-trabalho.md`](../../docs/divisao-de-trabalho.md).

---

## Objetivo do trilho

Maximizar a chance de a busca encontrar o documento certo a partir de um
relato leigo do tutor, por texto ou por voz: Query Rewriting como "tradutor
clínico", Multi-Query, HyDE, e Whisper consolidado numa única implementação.

A régua do trilho é a régua de recuperação do trilho A (Precision@1/MRR) —
**ainda não existe**. Até ela existir, "ligado vs. desligado" das três
técnicas de consulta não tem onde ser medido; o runner do B2 mede o sistema
inteiro (classificação final), não a qualidade da consulta isoladamente.

## Onde estou

| # | Entrega | Situação | O que entregou / entrega |
|---|---|---|---|
| — | Query Rewriting, Multi-Query, HyDE (implementação inicial) | ✅ (antes desta pasta existir) | As três técnicas existem em `query_client.py`, plugadas via flags no `chat_pipeline.py` |
| 1 | Reprodutibilidade das chamadas (B-04) | ✅ 04/09 | `options=default_options()` nas três chamadas; 3 testes novos. Critério numérico do backlog (`rag_query --repeat 2`, zero linhas instáveis) ainda não confirmado — precisa de Ollama rodando |
| 2 | Endurecimento do upload de voz (B-32) | ✅ 08/09 | `POST /voice/` grava com nome do servidor, valida tipo (415) e tamanho (413), apaga o arquivo em `finally`; 7 testes novos |
| 3 | Whisper único com WER medido (B-13) | ✅ 08/09 | 2 órfãos apagados; `VoiceService` sozinho, tamanho do modelo em setting; benchmark de WER com 18 relatos PT-BR sintéticos (edge-tts) — limite otimista |
| 4 | Decisão de fusão reescrita+variações (B-10) | 🔜 próxima | `[reescrita] + variações` sem duplicatas em `_build_queries` |
| 5 | Conter julgamento clínico na reescrita (B-08) | ⏳ | Exemplos negativos no prompt ou verificação pós-reescrita |
| 6 | Medir HyDE/Multi-Query/Rewriting ligado×desligado (B-09) | ⏳ bloqueado | Depende da régua de recuperação do trilho A |
| 7 | Paralelizar/fundir as 3 chamadas de consulta (B-07) | ⏳ | Reduzir os ~3,5s que a etapa custa hoje |

## Próxima entrega: decisão B-10 (fusão reescrita + variações)

**O problema que resolve.** Hoje, com multi-query ligado, a busca recebe só
as 3 variações + HyDE — a consulta reescrita em si não vai ao índice. Os
dois braços da ablação ("multi-query ligado" vs. "desligado") diferem em
natureza, não em grau, o que complica a leitura do estudo de ablação
formal de outubro.

**O que vai fazer:** em `_build_queries` (`chat_pipeline.py`), montar
`[reescrita] + variações`, sem duplicatas, quando o multi-query estiver
ligado. É o ponto único já preparado pelo B2 (`docs/CONTRATOS.md`, item 1).

**Como será medido:** quando a régua de recuperação do trilho A existir,
comparando Precision@1/MRR antes e depois. Até lá, teste de unidade
garantindo que a lista final inclui a reescrita e não tem duplicatas.

Depois dela: conter julgamento clínico na reescrita (B-08) e, quando a régua
de recuperação do trilho A existir, medir HyDE/Multi-Query/Rewriting
ligado×desligado (B-09). O benchmark de WER de voz também pede uma segunda
rodada com **áudio real** para substituir o número otimista da fala
sintética (B-13).

## Marcos

| Quando | Marco |
|---|---|
| 8–19 set | **Marco 1** do time — já medido pelo B2. Do lado do B1, entra aqui a reprodutibilidade (rodada 1) |
| 20–30 set | Iteração guiada pela régua de recuperação do trilho A, assim que existir |
| Outubro | **Marco 2** — matriz de ablação completa, com as flags de B1 medidas ligado×desligado |
| Novembro | **Marco 3** — números congelados, escrita final |

## O que está travando

Esta seção **só cresce**. Um bloqueio entra com a data em que foi visto e
permanece até ser resolvido — então vai para "Resolvidos", com a data.

### Aberto

| # | Bloqueio | De quem depende | Visto em | Efeito | Detalhe |
|---|---|---|---|---|---|
| 1 | **Régua de recuperação do trilho A não existe.** Sem ela, nenhuma das três técnicas de consulta (rewriting, multi-query, HyDE) pode ser medida isoladamente — hoje é fé, como o próprio João registrou | Trilho A | 04/09 (backlog) | Bloqueia B-09 por completo e limita B-10 a verificação estrutural, sem número de qualidade de recuperação | [B-09](../backlog.md#b-09) |
| 2 | **A etapa de consulta custa ~60% da latência** (3,5s de 5,7s), com as três chamadas sequenciais | — (interno ao trilho) | 04/09 (backlog, achado do B2) | Relevante para o requisito de *golden hour* do artigo | [B-07](../backlog.md#b-07) |
| 3 | **Whisper com três implementações órfãs, sem benchmark de qualidade** | — (interno ao trilho) | 31/08 (backlog, diagnóstico da divisão) | O artigo cita ~97,5% de precisão sem medição real | [B-13](../backlog.md#b-13) |

### Resolvidos

*(nenhum ainda)*

## Fora do escopo deste trilho

Prompt de triagem, geração, orquestração do pipeline e Chain-of-Thought/
Self-Refine são do B2. Chunking, embeddings, ordenação da busca e
re-ranking são do trilho A.
