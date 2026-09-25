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

**A prova 2 está escrita, com a composição exata.** Os nove autores
trabalharam das 03h10 às 03h40, em paralelo, cada um numa pasta isolada.

| Checagem (`python scripts/prova2_montar.py`) | Esperado | Obtido |
|---|---|---|
| Relatos | 330 | **330** (ids iguais aos pedidos, um por pedido) |
| Do mapa: emergências · leves | 190 · 115, em 61 quadros | **190 · 115, em 61 quadros** |
| Especiais | 10 · 8 · 7 | **10 · 8 · 7** |
| Com os especiais: emergências · leves · INCERTO | 194 · 126 · 10 | **194 · 126 · 10** |
| "mas", por classe | 40% ± 5 | **78 de 194 (40%) · 50 de 126 (40%)** |
| Textos repetidos | 0 | **0** |
| Relato que diz "é emergência" ou "não é emergência" | 0 | **0** |
| Pares do mesmo quadro com 6+ palavras seguidas em comum | 0 | **9** (ver Observações) |
| Tamanho | — | 18 a 117 palavras, mediana 68,5 |
| Cadernos de linguagem | um por quadro | **86** (61 quadros + 25 especiais) |

Os tons saíram como pedidos: nas emergências, 77 calmos (76 dos quadros e 1
especial), 39 aflitos, 40 neutros e 38 parecidos com a gêmea; nas leves, 48
aflitos, 53 neutros e 23 parecidos com a gêmea.

**Os autores conferiram, cada um no seu lote:** o JSON abre, um relato por
pedido, a regra do "mas" bate nos 330, nenhum relato repete 6 palavras de
uma citação anotada no caderno (seis autores acharam e reescreveram de 1 a 6
relatos na primeira conferência), e, nos pedidos sem palpite, o tutor não dá
nome de doença.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `scripts/prova2_pedidos.py` | **novo**: os 330 pedidos a partir do mapa (commit anterior) |
| `scripts/prova2_montar.py` | **novo**: monta o `casos.csv` e faz a conferência mínima; `--check` |
| `scripts/tests/test_prova2_pedidos.py` | **novo**: 5 testes (composição, tons, "mas" e palpite por quadro, o que o autor não vê, arquivos em dia) |
| `data/prova2/geracao/pedidos/` | os 9 lotes, completos e na versão do autor |
| `data/prova2/geracao/autores/lote_<n>/` | o que cada autor devolveu (`relatos.json`, `RESUMO.md`) |
| `data/prova2/geracao/cadernos/` | os 86 cadernos de linguagem |
| `data/prova2/casos.csv` | a prova 2, com rótulo provisório e `split` vazio |
| `data/prova2/README.md` | **novo**: o que é, a composição, a autoria e o que falta antes de usar |
| `.gitignore` | `data/prova2/geracao/bruto/` |

Commits: `7778f9e` (abre a rodada: os pedidos) e este.

## Observações

**1. A pesquisa foi mais fraca que a do piloto.** A ferramenta de busca na web
tem um limite de 200 buscas por sessão, **dividido entre todos os agentes da
noite** (os 9 autores e os 4 pesquisadores da
[rodada 27](2026-09-25-28-fontes-para-tutor-etapa-2.md)), e ele acabou cedo:
vários autores fizeram de 4 a 20 buscas e seguiram abrindo páginas por
endereço e pelos índices dos sites. Resultado: as fontes se concentram em
poucos sites brasileiros de tutor (comentários de leitores do Perito Animal e
do blog da Cobasi) e em páginas de orientação de clínicas; fala de tutor em
primeira pessoa quase não apareceu em vários quadros (cardíaco, queda, parto,
trombo, lírio, leptospirose), e nesses a linguagem é mais do autor. Não
contornaram bloqueios (JustAnswer, Reddit, Petz e Petlove recusaram).

**2. Nove pares de relatos do mesmo quadro repetem 6 ou mais palavras
seguidas** (ex.: "o xixi que ele fez no", "a cabeça dele fica dando uns",
"vomitou duas vezes, fez cocô mole"). São fórmulas do mesmo autor dentro do
mesmo quadro, não cópia de fonte. Não editei: texto de autor só muda na
revisão.

**3. Rótulos que os próprios autores estranharam** (estão nos `RESUMO.md`, e
nenhum foi mudado): convulsão única curta em cão epiléptico rotulada
imediata (L1Q03, o autor pôs um critério de urgência em cada relato);
"mas come normal" na torção (q046) e no filhote hipoglicêmico (q287);
otite com dor e cheiro como rotina (q302, q304); picada na bochecha como
rotina (q155); gata não castrada bebendo muito um mês depois do cio como 24 h
(q080); "desde ontem" num pedido de informação insuficiente (L9Q03). São
exatamente os casos para os veterinários olharem primeiro.

**4. O isolamento se manteve.** Cada autor recebeu só o próprio
`pedidos.json`, numa pasta fora do repositório, sem o tópico do mapa nem a
urgência codificada; nenhum relatou ter aberto outro arquivo. O quadro
leigo que eles viram é texto do script, e a gêmea, o nome leigo da outra
linha do mapa (sem a coluna de sinais).

## Deixado para depois

- **A prova 2 até o uso** ([B-63](../backlog.md#b-63)): a conferência completa
  (palavras em comum com as fichas, Naive Bayes entre lotes, o "mesmo autor"
  no top 3 contra os relatos independentes), a planilha cega para os
  veterinários, a validação, a divisão por assunto (66/264) e o congelamento.
- **Os 9 pares com fórmula repetida** e os rótulos estranhados pelos autores:
  para a revisão junto com a validação.
- **Uma segunda passada de pesquisa** nos quadros com pouca fala de tutor, se
  a conferência mostrar vocabulário muito próximo das fichas.

## Próximo passo

A conferência completa, antes da planilha dos veterinários:

```
python scripts/prova2_montar.py --check
```
