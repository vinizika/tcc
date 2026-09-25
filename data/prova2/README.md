# Prova 2

O conjunto que vai dar os números finais do TCC
([rodada 20 do João](../../evidencias/joao/2026-09-24-21-prova-2-desenho-e-piloto.md),
gerado na [rodada 28](../../evidencias/joao/2026-09-25-29-prova-2-geracao.md)).
São 330 relatos de tutor, escritos por nove agentes de IA isolados (instâncias
do Claude) que não viram o mapa, as fichas nem a prova 1. **Os rótulos ainda
não foram validados**: a prova só é usada depois da validação dos
veterinários, da divisão por assunto e do congelamento por hash.

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `casos.csv` | os 330 relatos, no formato da prova 1 mais `tone`, `persona`, `author` e `confusion_pair_topic`. Gerado por `python scripts/prova2_montar.py` |
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

## O que falta antes de usar

1. A conferência completa: palavras em comum com as fichas, Naive Bayes entre
   lotes, o "mesmo autor" no top 3 contra os relatos independentes.
2. A planilha para os veterinários validarem sem ver o rótulo; onde o
   veterinário discordar do mapa, vale o veterinário (e o mapa é revisto).
3. A divisão por assunto (66 de calibração, 264 de teste) e o congelamento com
   `scripts/prova_freeze.py`.

O acompanhamento está no [B-63](../../evidencias/backlog.md#b-63).
