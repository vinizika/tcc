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
| 5 | **Frente prova — lote oficial (~150 casos, dev/teste)** | 🔜 próxima | Depende de validar o formato com o time primeiro |
| 6 | **Frente prova — adaptar o runner** para ler `text` livre | ⏳ | Coluna alternativa, `--relato-lang`, caminho por opção, baselines triviais novos (seção 5.4 do plano) |
| 7 | Decisão de fusão reescrita+variações (B-10) | ⏳ | `[reescrita] + variações` sem duplicatas em `_build_queries` — não bloqueado, mas represado atrás da prova |
| 8 | Conter julgamento clínico na reescrita (B-08) | ⏳ | Exemplos negativos no prompt ou verificação pós-reescrita |
| 9 | Medir HyDE/Multi-Query/Rewriting ligado×desligado (B-09) | ⏳ desbloqueado 12/09 | A régua de recuperação existe; falta encaixar na agenda depois da prova |
| 10 | Paralelizar/fundir as 3 chamadas de consulta (B-07) | ⏳ | Reduzir os ~3,5s que a etapa custa hoje |
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

Em paralelo, sem depender da prova: decisão B-10 (fusão reescrita +
variações — agora com a régua de recuperação para medir de verdade),
conter julgamento clínico na reescrita (B-08), e o benchmark de WER com
áudio real.

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

## Fora do escopo deste trilho

Prompt de triagem, geração, orquestração do pipeline e Chain-of-Thought/
Self-Refine são do B2. Chunking, embeddings, ordenação da busca e
re-ranking são do trilho A.
