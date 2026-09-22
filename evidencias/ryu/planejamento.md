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

**Desde 12/09, o trilho também é dono da frente prova por inteiro** —
desenho, casos, gabarito e adaptação do runner para ler relatos em
português —, por decisão registrada em
[`docs/plano-base-e-prova.md`](../../docs/plano-base-e-prova.md): quem
escreveu os prompts do classificador (B2) não deve escrever a prova que os
mede. É a prioridade do trilho até a matriz de ablação de outubro.

A régua de recuperação (Precision@1/MRR), que faltava para medir
reescrita/multi-query/HyDE isoladamente, **existe desde 12/09** — construída
pelo João em nome do trilho A ([rodada 11](../joao/2026-09-12-11-regua-de-recuperacao.md)),
reaproveitando os 18 relatos PT-BR que este trilho escreveu para o
benchmark de voz.

## Onde estou

| # | Entrega | Situação | O que entregou / entrega |
|---|---|---|---|
| — | Query Rewriting, Multi-Query, HyDE (implementação inicial) | ✅ (antes desta pasta existir) | As três técnicas existem em `query_client.py`, plugadas via flags no `chat_pipeline.py` |
| 1 | Reprodutibilidade das chamadas (B-04) | ✅ 04/09 | `options=default_options()` nas três chamadas; 3 testes novos. Critério numérico do backlog (`rag_query --repeat 2`, zero linhas instáveis) ainda não confirmado — precisa de Ollama rodando |
| 2 | Endurecimento do upload de voz (B-32) | ✅ 08/09 | `POST /voice/` grava com nome do servidor, valida tipo (415) e tamanho (413), apaga o arquivo em `finally`; 7 testes novos |
| 3 | Whisper único com WER medido (B-13) | ✅ 08/09 | 2 órfãos apagados; `VoiceService` sozinho, tamanho do modelo em setting; benchmark de WER com 18 relatos PT-BR sintéticos (edge-tts) — limite otimista |
| 4 | **Frente prova — lote de calibração** | ✅ 13/09 | Formato definido em `data/prova/`, referência de triagem (MSD, mesma do mapa de assuntos), 18 casos com 7 pares de confusão. Rodado contra a API: 15/18, as 3 falhas são falsos não urgentes — inclusive o par de maior letalidade do mapa |
| 5 | **Frente prova — lote oficial (~150 casos, dev/teste)** | ✅ 22/09, falta só congelar | 150 casos completos em `data/prova/casos_oficiais.csv` (50 dev + 100 teste), 61/61 tópicos cobertos, 23 pares de confusão, balanço 77/70/3. Verificador de sobreposição contra a base criado e limpo. Falta decisão de congelar o `teste` por hash |
| 6 | **Frente prova — adaptar o runner** para ler `text` livre | ✅ 21/09 | Reaproveitado `scripts/run_map_triage_eval.py` (Vinicius já lia `text`/`expected_class` em PT-BR) em vez de escrever um runner paralelo — ganhou `--cases`, `--split` e `--runs-dir`. Rodado como fumaça contra o lote de calibração. Baselines triviais novos (seção 5.4 do plano) ficam para quando o lote oficial existir, com volume suficiente para calibrá-los |
| 7 | **Medir consulta nas coleções experimentais (B-09, B-10)** | ✅ 17/09 | Instrumento novo (`measure_query_techniques.py`) contra as 3 candidatas do trilho A. HyDE nunca ajudou → `HYDE_ENABLED=False` por padrão. Fusão reescrita+multi-query (B-10) nunca perde → implementada. Achado colateral: [B-57](../backlog.md#b-57) |
| 8 | Conter julgamento clínico na reescrita (B-08) | ✅ 17/09 | Exemplo negativo no prompt + guarda-corpo determinístico (`_contains_unwarranted_urgency`) que descarta a reescrita quando ela injeta urgência ausente do relato. 2 testes novos |
| 9 | Cadastro de tutor/pet sem autenticação real (B-56) | ⏳ (adiado para o deploy, decisão de 17/09) | Política aberta no Supabase, sem auth — risco baixo enquanto o sistema roda só local/dev |
| 10 | Paralelizar Multi-Query e HyDE (B-07) | 🔶 em andamento, 21/09 | Paralelas desde 17/09; medido em 21/09 contra a coleção real (3.481 chunks) — economiza 13-39%, nunca piora. Falta GPU disponível para confirmar o número absoluto (`query_s` < 1,5s); ambiente atual roda 100% CPU |
| 11 | Benchmark de WER com áudio real | ⏳ | Substitui o número otimista da fala sintética (B-13) |

## Próxima entrega: lote oficial da prova (~150 casos)

**O problema que resolve.** A prova atual mede vocabulário, não triagem — é
a causa raiz do fracasso do Chain-of-Thought medido pelo João (autópsia,
12/09) e o motivo de nenhum número do projeto, até agora, dizer o que o
sistema sabe fazer de verdade.

**O que vai fazer.** Depois de validar o formato do lote de calibração com o
time (7 pares de confusão, referência MSD, gabarito rastreável), escrever o
restante até a casa de 150 relatos, dividido em desenvolvimento (~50) e
teste (~100, o que congela). Regras fixas: nunca ler os documentos da base
enquanto escrevo (a muralha), nunca copiar a coluna de sinais do mapa, e
casos "fora da base" vindos de fora do mapa inteiro — não só de quadros
ainda não indexados.

**Como será medido.** O runner adaptado (entrega seguinte) roda o lote de
desenvolvimento a qualquer momento; o de teste, só em marcos, com hash
registrado. Antes de fechar, um passo automático confere que os casos não
têm sobreposição de texto com os documentos da base.

Em paralelo, sem depender da prova: conter julgamento clínico na reescrita
(B-08, agora com as candidatas reais do trilho A para medir contra) e o
benchmark de WER com áudio real.

## Marcos

| Quando | Marco |
|---|---|
| 8–19 set | **Marco 1** do time — já medido pelo B2. Do lado do B1: reprodutibilidade (rodada 1) e o formato + lote de calibração da prova nova (rodada 4) |
| 20–26 set | Lote oficial da prova (~150 casos), validado pelo time; runner adaptado |
| 27 set–03 out | Prova congelada por hash (dev/teste); iteração guiada pela régua de recuperação |
| Outubro | **Marco 2** — matriz de ablação completa, com as flags de B1 e a prova nova |
| Novembro | **Marco 3** — números congelados, escrita final |

## O que está travando

Esta seção **só cresce**. Um bloqueio entra com a data em que foi visto e
permanece até ser resolvido — então vai para "Resolvidos", com a data.

### Aberto

| # | Bloqueio | De quem depende | Visto em | Efeito | Detalhe |
|---|---|---|---|---|---|
| 2 | **A etapa de consulta custa ~60% da latência** (3,5s de 5,7s), com as três chamadas sequenciais | — (interno ao trilho) | 04/09 (backlog, achado do B2) | Relevante para o requisito de *golden hour* do artigo | [B-07](../backlog.md#b-07) |
| 4 | **O formato do lote de calibração da prova ainda não foi validado pelo time.** Escrever os ~150 casos oficiais antes disso arrisca ter que reescrever tudo | Trilho A + B2 (revisão) | 13/09 (rodada 4) | Represa o lote oficial e a adaptação do runner | — |

### Resolvidos

| # | Bloqueio | Resolvido em | Como |
|---|---|---|---|
| 1 | **Régua de recuperação do trilho A não existia.** Sem ela, nenhuma das três técnicas de consulta podia ser medida isoladamente | 12/09 | O João construiu em nome do trilho A ([rodada 11](../joao/2026-09-12-11-regua-de-recuperacao.md)), reaproveitando os 18 relatos PT-BR do benchmark de voz deste trilho. Destrava o [B-09](../backlog.md#b-09) |
| 3 | **Whisper com três implementações órfãs, sem benchmark de qualidade** | 08/09 | [Rodada 3](2026-09-08-03-whisper-unico-e-wer.md): consolidado em `VoiceService`, WER de 5,2% medido (fala sintética) |
| 5 | **Nenhuma base tinha conteúdo real para medir consulta contra** | 17/09 | Os três lotes experimentais do trilho A (14–16/09) deixaram coleções candidatas em staging. Medido em [rodada 6](2026-09-17-06-medindo-consulta-nas-candidatas.md); no caminho, achado o [B-57](../backlog.md#b-57) (o snapshot está num caminho que o backend real não lê) |

## Fora do escopo deste trilho

Prompt de triagem, geração, orquestração do pipeline e Chain-of-Thought/
Self-Refine são do B2. Chunking, embeddings, ordenação da busca e
re-ranking são do trilho A.
