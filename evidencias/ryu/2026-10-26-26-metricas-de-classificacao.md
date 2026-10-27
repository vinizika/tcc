# Métricas de classificação para o relatório

**Data:** 26/10/2026 · **Trilho:** B1 (frente prova) · **Rodada:** 26 · **Commit:** este

## O que foi feito

O orientador pediu que o relatório traga as métricas de classificação usuais
(acurácia, precisão, recall/sensibilidade, F1 etc.). As rodadas do time
registravam sobretudo emergências perdidas e falsos alarmes. Nenhum teste novo
foi rodado: as métricas foram **calculadas a partir das previsões caso a caso
já registradas**, com `python scripts/metricas_classificacao.py`:

- `data/evaluation/autopsia2/resultados_por_caso.csv` (autópsia 2 do João:
  prova 1 e régua, relatos independentes, piloto da prova 2);
- as rodadas citadas da calibração da prova 2 (rodadas 18 e 23 do Ryu).

**Semântica** (a das autópsias): classe positiva = EMERGENCIA; emergência
prevista como NAO_EMERGENCIA ou INCERTO é falso negativo; caso leve previsto
como EMERGENCIA é falso positivo. Acurácia = concordância exata nas três
classes, sobre todos os casos; acurácia balanceada = média de sensibilidade e
especificidade.

**O lote teste da prova 2 não foi usado**, por decisão do Ryu em 26/10
(contador segue em 0).

## Resultado

Relatos independentes (122: 76 emergências e 46 leves):

| Configuração | Acurácia | Ac. balanceada | Sensibilidade | Especificidade | Precisão | F1 |
|---|---|---|---|---|---|---|
| **Fichas + Gemini (sistema)** | 0,893 | **0,928** | 0,921 | **0,935** | **0,959** | **0,940** |
| Fichas + Qwen | 0,893 | 0,891 | 0,934 | 0,848 | 0,910 | 0,922 |
| Gemini sem contexto | 0,844 | 0,858 | 0,934 | 0,783 | 0,877 | 0,904 |
| Qwen sem contexto | 0,754 | 0,764 | 0,724 | 0,804 | 0,859 | 0,786 |
| Llama sem contexto | 0,492 | 0,498 | 0,474 | 0,522 | 0,621 | 0,537 |
| Base acadêmica + Llama | 0,492 | 0,498 | 0,474 | 0,522 | 0,621 | 0,537 |
| Base acadêmica + Llama + reformulação | 0,508 | 0,507 | 0,513 | 0,500 | 0,629 | 0,565 |

Configuração do sistema (fichas + Gemini) por conjunto:

| Conjunto | Acurácia | Sensibilidade | Especificidade | Precisão | F1 |
|---|---|---|---|---|---|
| Prova 1 e régua (134) | 0,963 | 0,973 | 0,983 | 0,986 | 0,980 |
| Relatos independentes (122) | 0,893 | 0,921 | 0,935 | 0,959 | 0,940 |
| Piloto da prova 2 (40) | 0,925 | 1,000 | 0,812 | 0,889 | 0,941 |
| Calibração da prova 2 (66) | 0,970 | 1,000 | 0,958 | 0,976 | 0,988 |

Conferência: as contagens de emergências perdidas e falsos alarmes batem com
as reportadas pelo time (ex.: fichas + Gemini nos independentes, 6 e 3).
A base acadêmica + Llama é idêntica ao Llama sem contexto nos independentes
porque o limiar de 0,72 barrava o contexto em 116 de 122 relatos.

## O que mudou

| Arquivo | Mudança |
|---|---|
| `scripts/metricas_classificacao.py` | **novo** — métricas a partir das previsões registradas |
| esta evidência | — |

No Overleaf (fora do repositório): subseção "Métricas de classificação" com as
duas tabelas; e, a pedido do orientador, o texto passou a apresentar o sistema
como está, com os testes que justificam as escolhas, sem o comparativo
"proposta inicial × executado" (saíram o fluxograma do TCC1, o parágrafo de
evolução e a tabela-resumo).

## Próximo passo

A medição no lote teste da prova 2 continua pendente, quando o time decidir.
