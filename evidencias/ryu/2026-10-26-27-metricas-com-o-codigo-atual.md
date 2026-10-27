# Métricas do sistema medidas de novo, com o código atual

**Data:** 26/10/2026 · **Trilho:** B1 (frente prova) · **Rodada:** 27 · **Commit:** este

## O que foi feito

As métricas da [rodada 26](2026-10-26-26-metricas-de-classificacao.md) foram
calculadas das previsões registradas entre 23/09 e 07/10. A pedido do Ryu, a
configuração do sistema foi **rodada de novo**, pela API, com o código da
`main` de hoje (`1cb7ea4`, que inclui o deploy e a troca de chave do Gemini;
segundo o João, nenhum dos dois mexe no caminho de decisão), nos seis lotes de
desenvolvimento: prova 1 `dev` (50) e calibração (18), régua (66), relatos
independentes (122), piloto da prova 2 (40) e calibração da prova 2 (66).
Preset `producao` (fichas, BGE-M3, três fichas sem limiar, Gemini
3.5 Flash-Lite, tradutor desligado, `v1_grounded`). Nenhum lote lacrado foi
usado (teste da prova 1 e da prova 2).

## Resultado esperado

_Escrito antes de rodar._ Métricas próximas às da rodada 26 (diferença de
poucos casos), com as mudanças concentradas nos casos em que a autópsia 3 já
tinha visto o Gemini mudar de decisão entre dias ([B-77](../backlog.md#b-77)).

## Resultado obtido

362 de 362 linhas com status `ok`. Classe positiva: emergência (semântica da
rodada 26).

| Conjunto | Acurácia | Ac. balanceada | Sensibilidade | Especificidade | Precisão | F1 | Perdidas | Falsos alarmes |
|---|---|---|---|---|---|---|---|---|
| Prova 1 e régua (134) | 0,948 | 0,962 | 0,959 | 0,966 | 0,973 | 0,966 | 3 | 2 |
| Relatos independentes (122) | 0,877 | 0,900 | 0,908 | 0,891 | 0,932 | 0,920 | 7 | 5 |
| Piloto da prova 2 (40) | 0,950 | 0,938 | 1,000 | 0,875 | 0,923 | 0,960 | 0 | 2 |
| Calibração da prova 2 (66) | 0,970 | 0,975 | 0,950 | 1,000 | 1,000 | 0,974 | 2 | 0 |

**Comparação caso a caso com as previsões registradas** (autópsia 2, 25/09;
calibração da prova 2, 05/10): **352 de 362 iguais (97,2%)**.

| Conjunto | Iguais | O que mudou |
|---|---|---|
| Prova 1 e régua | 132/134 | p26 EMERGENCIA → INCERTO (emergência perdida); p44 NAO → EMERGENCIA |
| Independentes | 119/122 | i40 NAO → EMERGENCIA; i58 INCERTO → EMERGENCIA; j12 (leptospirose) EMERGENCIA → INCERTO |
| Piloto | 39/40 | pB05 EMERGENCIA → NAO_EMERGENCIA (certo; era falso alarme) |
| Calibração da prova 2 | 62/66 | q118 EMERGENCIA → NAO (certo); q186 INCERTO → NAO (certo); q220 e q318 EMERGENCIA → INCERTO (emergências perdidas) |

**Como esperado nos independentes:** as três mudanças (i40, i58, j12) são
exatamente as que a autópsia 3 do João registrou em 05/10. A mudança do
Gemini entre 25/09 e 05/10 persiste três semanas depois, com a mesma versão
informada pela API.

**Diferente do esperado na calibração da prova 2:** duas emergências que o
Gemini reconhecia em 05 e 07/10 viraram INCERTO hoje (q220, q318), e os dois
erros antigos (q118, q186) se corrigiram sozinhos. Sensibilidade de 1,000
para 0,950; especificidade de 0,958 para 1,000.

**Leitura:** com o código atual, o sistema segue com sensibilidade entre
0,908 e 1,000 e F1 entre 0,920 e 0,974 nos quatro conjuntos. Em relação aos
números registrados, os valores oscilam de 1 a 3 casos por conjunto, sempre
por decisões do Gemini (as fichas e a busca são determinísticas). Toda perda
nova é uma resposta INCERTO, o "não sei" falso que as rodadas 19 e 21 já
apontavam como o principal erro restante. Para o relatório, essas oscilações
reforçam o que o B-77 pede: reportar o número com repetições em dias
diferentes.

Rodadas citadas: `data/evaluation/cited/20261026-*_r27_*` (seis), conferido
que a chave do Gemini não aparece em nenhum arquivo.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `data/evaluation/cited/20261026-*_r27_*` | **novas** — as seis rodadas |
| esta evidência | — |

## Próximo passo

Atualizar a subseção de métricas do relatório com estes números (código
atual) e a nota sobre a variação entre dias.
