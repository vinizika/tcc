# Prova 2

O conjunto que vai dar os números finais do TCC
([rodada 20 do João](../../evidencias/joao/2026-09-24-21-prova-2-desenho-e-piloto.md),
gerado na [rodada 28](../../evidencias/joao/2026-09-25-29-prova-2-geracao.md)).
São 330 relatos de tutor, escritos por nove agentes de IA isolados (instâncias
do Claude) que não viram o mapa, as fichas nem a prova 1. **Os rótulos foram
validados** pelos veterinários da ASAVET em 26/09/2026, sem ver o rótulo, e
nenhum mudou (`validacao.json`). A prova só é usada depois da divisão por
assunto e do congelamento por hash.

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `casos.csv` | os 330 relatos, no formato da prova 1 mais `tone`, `persona`, `author` e `confusion_pair_topic`. Gerado por `python scripts/prova2_montar.py` |
| `validacao.json` | o registro da validação dos rótulos (quem, quando, como, e o sha256 do `casos.csv` validado); o `prova2_montar.py` escreve o `marked_by` a partir dele |
| `geracao/pedidos/lote_<n>.json` | o pedido de cada relato, completo (com o tópico do mapa e o rótulo), gerado por `python scripts/prova2_pedidos.py` |
| `geracao/pedidos/lote_<n>.instancia.json` | só o que o autor do lote viu: o quadro em linguagem leiga, a espécie, a gravidade, o tom, a persona e as marcas de estilo |
| `geracao/autores/lote_<n>/` | o que cada autor devolveu: `relatos.json` e o `RESUMO.md` (fontes, dificuldades e os pedidos em que o rótulo lhe pareceu estranho) |
| `geracao/cadernos/<topic>.md` | o caderno de linguagem de cada quadro (e `especial_<ref>.md` para os 25 especiais): como tutores descrevem o quadro, com as fontes consultadas. As expressões são sínteses dos autores, não citações longas |

`geracao/bruto/` fica fora do Git (rascunhos).

## Composição

| Parte | Quantos | Rótulo |
|---|---|---|
| Emergências, 5 por quadro de emergência do mapa (38 × 5) | 190 | a urgência do mapa (`imediato` → EMERGENCIA) |
| Não emergências, 5 por quadro leve (23 × 5) | 115 | a urgência do mapa (`ate_24h` e `rotina` → NAO_EMERGENCIA) |
| Informação insuficiente | 10 | INCERTO |
| Quadros clínicos reais que o mapa não cobre | 8 | 4 EMERGENCIA, 4 NAO_EMERGENCIA, dados pelo orquestrador |
| Perguntas não clínicas | 7 | NAO_EMERGENCIA |

Tons por quadro: emergência = 2 calmos, 1 aflito, 1 neutro, 1 parecido com a
gêmea leve; leve = 2 aflitos, 2 neutros, 1 parecido com a gêmea grave. A
palavra "mas" aparece em 40% de cada classe (78 de 194, 50 de 126), como os
pedidos marcaram.

## O que faltava antes de usar

1. ~~A conferência completa~~: o vazamento pelas palavras medido em 05/10
   ([rodada 17 do Ryu](../../evidencias/ryu/2026-10-05-17-prova-2-divisao-e-congelamento.md),
   `python scripts/prova2_conferir.py`); o "mesmo autor" no top 3 tinha sido
   medido na rodada 30 do João (79% contra 77% dos relatos independentes).
2. ~~A validação dos rótulos pelos veterinários, sem ver o rótulo~~: feita em
   26/09, sem nenhuma discordância do mapa
   ([rodada 30](../../evidencias/joao/2026-09-26-31-validacao-dos-especialistas.md)).
3. ~~A divisão por assunto e o congelamento~~: feitos em 05/10 (seção abaixo).

## Divisão e congelamento (05/10)

Pela regra da rodada 20 do João (decisão 4), na
[rodada 17 do Ryu](../../evidencias/ryu/2026-10-05-17-prova-2-divisao-e-congelamento.md):
um relato de cada um dos 61 quadros na `calibracao` e os outros quatro no
`teste`; dos especiais, 2 de informação insuficiente, 2 fora do mapa e 1 não
clínico na `calibracao`. Qual relato vai é sorteio reproduzível pela semente
`prova2-divisao-2026-10-05` do `prova2_montar.py`, fixada antes de qualquer
medição. Os rótulos não mudaram: em relação ao arquivo validado
(`validacao.json`), só mudaram as colunas `marked_by` (rodada 30) e `split`.

| Lote | Linhas | Classes (E · N · I) | sha256 (linhas inteiras) | Uso |
|---|---|---|---|---|
| `calibracao` | 66 | 40 · 24 · 2 | `44fa0edd515afdbaae4c73149c1b0fdf32c7a106f326de3ea411f3bad5cfd0f8` | à vontade, para desenvolver e conferir |
| `teste` | 264 | 154 · 102 · 8 | `b21b4648c9205dac8df9b29a58bcdd2b2c2fad1faed71533fb79c92da08c5e93` | **uma vez, pela configuração final** |

Conferir: `python scripts/prova_freeze.py --cases data/prova2/casos.csv --split teste`
(e `--split calibracao`). O runner (`run_evaluation.py --cases … --split …`)
recusa rodar se o hash não bater.

**Vezes que o lote `teste` foi usado numa medição: 0.** Quem rodar uma
medição nele soma 1 aqui, no mesmo commit, com o link da rodada. Pelo
[B-77](../../evidencias/backlog.md#b-77), a medição final com o Gemini repete
em dias diferentes e declara a variação entre dias.

O acompanhamento está no [B-63](../../evidencias/backlog.md#b-63).
