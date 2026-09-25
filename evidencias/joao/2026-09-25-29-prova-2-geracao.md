# Prova 2: a geração dos 330 relatos

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2, para o instrumento do time ·
**Rodada:** 28 · **Commits:** este

> Rodada de **construção de instrumento**, feita em paralelo com as rodadas 23
> a 26 por nove agentes de IA isolados. Gera a prova 2 especificada na
> [rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md). Os rótulos saem
> **provisórios**: a prova só vale depois da validação dos veterinários, da
> divisão por assunto e do congelamento, que ficam para depois desta rodada.

## O que foi feito

1. **Os pedidos**, gerados por script a partir do mapa
   ([`scripts/prova2_pedidos.py`](../../scripts/prova2_pedidos.py)): um pedido
   por relato, com o quadro em linguagem leiga, a espécie, a gravidade (o
   rótulo), o tom, a persona do tutor e as marcas de estilo controladas. O
   script é o único que vê o mapa; cada autor recebe só o seu lote, sem o
   tópico do mapa nem a urgência codificada.
2. **Nove autores isolados** (instâncias do Claude): oito com 7 ou 8 quadros
   cada (35 ou 40 relatos) e um com os 25 casos especiais. Cada autor pesquisa
   na internet como tutores descrevem cada quadro, grava um caderno de
   linguagem com as fontes e escreve os relatos do zero. Não abre nada do
   projeto.
3. **A montagem** em `data/prova2/casos.csv` e uma conferência mínima:
   composição, ids, duplicatas, a palavra "mas" por classe e os palpites.

## Por quê

A prova 1 não pode dar o número final do TCC: foi escrita com o mapa na mão,
entrega a classe pelas palavras e tem 74 emergências, que só enxergam
diferenças grandes ([rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md)).
O piloto de 40 relatos mostrou que dá para escrever a prova 2 assim, e ensinou
quatro correções, que agora estão nos pedidos.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| **Composição exata da rodada 20**: 5 relatos por quadro (38 × 5 = 190 emergências, 23 × 5 = 115 leves) e 25 especiais (10 com informação insuficiente, 8 quadros reais fora do mapa, 7 perguntas não clínicas) | Poder para comparar atendentes bons entre si; com 190 emergências, "0 perdidas" limita o erro real a 1,6% |
| **Tons por quadro**: emergência = 2 calmos, 1 aflito, 1 neutro, 1 parecido com a gêmea leve; leve = 2 aflitos, 2 neutros, 1 parecido com a gêmea grave | O tom é variável controlada; é o risco real de uso que a prova 1 quase não tem |
| **"mas" em 2 de cada 5 relatos**, nas duas classes, marcado no pedido | No piloto, "mas" marcava o caso leve (a regra "tem 'mas' ⇒ leve" acertava 67,5%) |
| **Palpite de diagnóstico só no relato "gêmea"** (1 em 5) | Correção do piloto: no máximo 1 palpite em cada 5 |
| **Cinco jeitos de contar com calma**, em rodízio: minimização, adiamento, bem-estar, "mas come normal" e sem frase pronta | As quatro frases de tom da [rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md), mais a calma sem fórmula |
| **Neutro não é "de livro"**, na instrução | Correção do piloto (frequência respiratória contada, "almofadinhas ásperas") |
| O quadro leigo é **texto do script**, não do mapa nem das fichas | Se o pedido carregasse a coluna de sinais do mapa ou o nome leigo das fichas de busca, a busca acertaria por eco |
| Os **8 quadros fora do mapa** têm rótulo do orquestrador (4 emergências, 4 leves), provisório como os outros | Não há linha do mapa para derivar o rótulo; a validação dos veterinários vale para todos |
| Autoria: **só IA, sem âncora humana** | Decisão do João, 25/09 ([rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md), decisão 6) |
| `split` fica vazio | A divisão por assunto (66 de calibração, 264 de teste) é feita depois da validação, antes do congelamento |

## Resultado esperado

_Escrito antes de os autores começarem._

- **Composição exata:** 330 relatos; 190 emergências e 115 leves de 61
  quadros (5 cada), mais 25 especiais. Contando os especiais, 194 emergências,
  126 leves e 10 INCERTO.
- **"mas":** em 40% ± 5 pontos de cada classe (o pedido marca 78 de 194 e 50
  de 126).
- **Palpites:** no máximo 1 em cada 5 relatos (61 pedidos permitem).
- **Duplicatas:** nenhum texto repetido; nenhum relato com mais de 5 palavras
  seguidas em comum com outro relato do mesmo quadro.
- **Cadernos:** um por quadro, com pelo menos 3 fontes, das quais pelo menos
  uma em português, na maioria dos quadros.

A conferência completa (palavras em comum com as fichas, Naive Bayes entre
lotes, a medida de "mesmo autor") fica para depois, com a validação.

## Resultado obtido

_(preenchido ao montar)_

## O que mudou no repositório

_(preenchido ao montar)_

## Observações

_(preenchido ao montar)_

## Deixado para depois

_(preenchido ao montar)_

## Próximo passo

_(preenchido ao montar)_
