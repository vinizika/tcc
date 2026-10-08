# Tradutor inteligente: só quando a busca está em dúvida

**Data:** 06/10/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 19 · **Commit:** este

## O que foi feito

O tradutor (reescrita, multi-query e HyDE) está desligado desde 25/09, porque
nas fichas ele piora a busca: o relato cru já fala a língua da ficha
([rodada 17 do João](../joao/2026-09-24-18-tradutor-desligado.md)). O
[B-69](../backlog.md#b-69) registrou a variante que sobrou: **acionar o tradutor
só quando a busca estiver insegura**. Esta rodada é a primeira tentativa, em
três passos:

1. **Diagnóstico** (sem modelo de linguagem, só a busca): a nota de
   semelhança da busca separa os casos em que ela acerta dos casos em que erra?
   Se não separar, não existe "sinal de dúvida" para acionar o tradutor, e a
   ideia para aqui.
2. *(se o passo 1 passar)* O tradutor condicional, com um prompt que **proíbe
   nome de doença, tratamento e urgência** (o defeito que a rodada 17 do João
   mediu nos prompts atuais).
3. *(se o passo 1 passar)* A medição na busca e na decisão.

## Por quê

O Ryu (dono do trilho B1) decidiu, em 06/10, desenvolver as técnicas para
melhorar o retorno do sistema, começando pela do próprio trilho. A medição de
calibração ([rodada 18](2026-10-05-18-calibracao-da-prova-2.md)) mostrou um
erro que é de busca: no q186 (primeiro cio) as 3 fichas eram de outro assunto,
e o Gemini respondeu INCERTO.

## Conjuntos

Nenhum caso do lote `teste` da prova 1 nem da prova 2 entra aqui.

| Papel | Conjuntos |
|---|---|
| **Calibrar** o limiar (como pede o B-69) | prova 2 `calibracao` (61 com quadro), prova 1 `dev` (50) e calibração (18), régua (66) |
| **Conferir** (o critério do B-69 é medido aqui) | relatos independentes (122), piloto da prova 2 (40) |

## Resultado esperado

_Escrito antes de rodar o diagnóstico._

Nos casos em que a ficha certa **não** está entre as 3 primeiras, espero a
nota da 1ª ficha **mais baixa** e a distância entre a 1ª e a 2ª **menor** do que
nos casos em que a busca acerta.

**Critério para seguir ao passo 2:** existir um limiar, escolhido só nos
conjuntos de calibrar, que marque como "em dúvida" **no máximo 30%** dos casos e
capture **pelo menos 60%** dos casos em que a ficha certa ficou fora das 3
primeiras, e que, aplicado sem ajuste aos conjuntos de conferir, mantenha os
dois números a menos de 10 pontos disso.

Se não passar, a conclusão é que a busca não sabe quando erra, o tradutor
condicional não tem gatilho, e o B-69 fecha como "testado, não funciona" — um
resultado que também vai para o TCC.

## Resultado obtido

### Passo 1 — o diagnóstico: o sinal existe, mas não passou no critério

`python scripts/diagnostico_busca.py` contra a API (bge-m3 nas 61 fichas, modo
`vector`), 352 relatos; dados por caso em
[`dados/2026-10-06-diagnostico-busca.jsonl`](dados/2026-10-06-diagnostico-busca.jsonl).

| Conjunto | Relatos | Ficha certa em 1º | Entre as 3 | Entre as 5 | Fora das 3 |
|---|---|---|---|---|---|
| Calibrar (prova 2 calibração, prova 1 dev e calibração, régua) | 190 | 144 | 173 | 178 | 17 |
| Conferir (independentes, piloto) | 162 | 90 | 126 | 142 | 36 |

**A busca "sabe" um pouco quando erra.** Nos relatos em que a ficha certa
ficou fora das 3 primeiras, a nota da 1ª ficha é mais baixa (mediana 0,613
contra 0,654) e a distância para a 2ª é bem menor (0,010 contra 0,035). As duas
medidas separam acerto de erro com a mesma força nos dois grupos (a chance de um
erro ter nota menor que um acerto: 0,75 a 0,76), ou seja, o sinal **não** foi um
acaso do conjunto de calibrar.

**Mas não com a força que o critério pedia:**

| Gatilho (escolhido só no calibrar) | Calibrar: marca · captura | Conferir: marca · captura | Critério |
|---|---|---|---|
| nota da 1ª < 0,6157 | 23% · **59%** | 24% · 56% | ❌ captura abaixo de 60% (por 1 ponto) |
| distância 1ª − 2ª < 0,0155 | 28% · 71% | **36% · 58%** | ❌ no conferir, marca 8 pontos a mais e captura **13 pontos a menos** (limite: 10) |

Pelo critério escrito antes, **o passo 1 não passa**. Não é o "a busca não
sabe quando erra" que eu tinha escrito como conclusão do fracasso: o sinal
existe e é estável, mas é fraco — um gatilho que pega pouco mais da metade dos
erros e marca de um quarto a um terço de todos os relatos.

**Um achado de passagem.** Dos 53 relatos com a ficha certa fora das 3
primeiras, **41 a têm entre a 4ª e a 10ª** (14 de 17 no calibrar, 27 de 36 no
conferir); 12 a deixam além da 10ª. Na maioria das vezes a ficha certa não
some, só fica um pouco atrás.

### Os passos 2 e 3

Não rodaram: o critério do passo 1 não passou, e a decisão de seguir mesmo assim
(ou de mudar de caminho) é do Ryu.

### Adendo (06/10, tarde): o alarme e os "incertos" falsos

Depois do passo 1, o Ryu definiu o objetivo das técnicas: **o sistema só deve
responder INCERTO quando falta informação do tutor, nunca porque a busca se
confundiu**. Relendo as rodadas citadas do Gemini (autópsia 3 e rodada 18),
dos 10 INCERTO errados, **7 vieram com as 3 fichas de outro assunto**, e 6 dos 10
eram emergências: é o principal jeito de o Gemini perder uma emergência hoje.

Nesses 7, o gatilho da distância (< 0,0155) **dispara em 6**. Mas a ficha certa
estava longe: na 5ª, 6ª, 9ª, 18ª, 18ª e 27ª posição, e em um caso nem nas 50.
**"Mostrar 5 fichas em vez de 3" resolveria 1 dos 7**, e foi descartado antes de
virar código.

**Simulação de "na dúvida, decidir sem as fichas"**, sem chamada nova: para cada
caso, a resposta do braço sem busca quando o gatilho dispara, e a do braço com
fichas quando não dispara, em rodadas citadas do mesmo dia.

| Conjunto (rodadas) | Com fichas sempre | Sem fichas sempre | **Sem fichas na dúvida** |
|---|---|---|---|
| Independentes, Gemini, 25/09 (`r2_gemini_indep_conta1` × `r2_gemini_sembusca_indep_conta2`) — perdidas · falsos alarmes · INCERTO falsos | 6 · 3 · 9 | 5 · 10 · 8 | **4 · 6 · 6** |
| Independentes, qwen, 25/09 (`r3_qwen_indep` × `r4_qwen_sembusca_indep`) | 5 · 7 · 1 | 21 · 9 · 0 | **8 · 9 · 0** |
| Calibração da prova 2, Gemini, 05/10 (rodada 18) | 0 · 1 · 1 | 0 · 0 · 0 | **0 · 0 · 0** |

O gatilho disparou em 39 de 122 independentes e em 30 de 61 relatos com quadro
da calibração (49%, bem acima dos 23–28% dos conjuntos do passo 1).

**Leitura:** a regra depende do atendente. No Gemini, troca 2 emergências
perdidas a menos por 3 falsos alarmes a mais nos independentes; no qwen, piora
tudo (o qwen precisa das fichas: sem elas perde 21). As diferenças são de 2 a 3
casos, dentro do ruído do Gemini entre dias (B-77). **Não vira código.** O que
o adendo deixa claro é o tamanho do problema e onde ele está: os INCERTO falsos
vêm de fichas de outro assunto, e a ficha certa costuma estar longe demais para
um ajuste no número de fichas. Sobram dois caminhos, os dois ainda não medidos:
**buscar de novo com outras palavras** (o tradutor, só nos casos de dúvida) ou
**a IA conferir cada ficha** antes de usá-la (o Self-Refine do
[B-70](../backlog.md#b-70), trilho B2).

### Passo 2 (só busca): o tradutor nos casos de dúvida

**O desenho.** Nos relatos em que o gatilho dispara (distância 1ª − 2ª < 0,0155,
o limiar do passo 1), o Gemini escreve **3 paráfrases do relato só com os sinais
observados**, na linguagem do tutor, com proibição explícita de nome de doença,
causa, tratamento e urgência (o defeito da rodada 17 do João). A busca roda com
o relato cru e com cada paráfrase; cada ficha fica com a **maior nota** que
recebeu nas 4 buscas. Nos relatos sem gatilho, nada muda. Sem modelo de decisão
nesta etapa: mede só se a ficha certa entra nas 3 primeiras.

**Resultado esperado** (_escrito antes de rodar_). Critério para levar à
decisão (passo 3):

1. nos relatos marcados, a ficha certa entre as 3 primeiras sobe **≥ 10 pontos**
   sobre o relato cru, nos dois grupos (calibrar e conferir);
2. os relatos que **perdem** a ficha certa das 3 primeiras são no máximo um terço
   dos que ganham;
3. no conjunto inteiro dos relatos independentes, o "entre as 3" sobe **≥ 3
   pontos** (o critério do B-69).

A rodada 17 do João mediu que paráfrases parecidas (o conserto E2) **perdem**
para o relato cru quando aplicadas a todos os relatos (0,81 → 0,71 no 1º lugar);
a aposta aqui é que, restritas aos casos em que o relato cru já está perdido, elas
ajudem mais do que atrapalham. Espero passar no 1 e no 2 e ficar no limite do 3.

**Resultado obtido.** `python scripts/experimento_tradutor_duvida.py` (fase
`preparar` no host, `rodar` no container), 112 relatos marcados, 334
paráfrases do `gemini-3.5-flash-lite` (111 de 112 casos com as 3); dados por
caso em [`dados/2026-10-06-tradutor-na-duvida.jsonl`](dados/2026-10-06-tradutor-na-duvida.jsonl).

| Grupo | Marcados | Ficha certa entre as 3: cru → tradutor | Em 1º: cru → tradutor | Ganha · perde |
|---|---|---|---|---|
| Calibrar | 54 | 42 (78%) → **39 (72%)** | 21 → 20 | 1 · **4** |
| Conferir | 58 | 37 (64%) → 38 (66%) | 14 → 23 | 3 · 2 |

| Conjunto inteiro (tradutor só nos marcados) | Entre as 3: antes → depois |
|---|---|
| Independentes (122) | 94 (77,0%) → **93 (76,2%)** |
| Piloto (40) | 32 (80,0%) → 34 (85,0%) |
| Calibração da prova 2 (61) | 50 (82,0%) → 48 (78,7%) |

**Os três critérios falham:** (1) nos marcados, −6 pontos no calibrar e +2 no
conferir (pedia ≥ +10 nos dois); (2) no calibrar perde 4 para cada 1 que ganha;
(3) nos independentes inteiros, −0,8 ponto (pedia ≥ +3). E nos 6 INCERTO falsos
que motivaram o passo, a ficha certa **se afastou** em 5 (q186: 27ª → 21ª; i05:
18ª → 25ª; j12: 6ª → 8ª; j33: 9ª → 16ª; j48: 5ª → 13ª; i55: fora das 50 → 56ª).
O único sinal positivo é o 1º lugar no conferir (14 → 23), que não se repete no
calibrar e não muda o "entre as 3" que chega ao atendente.

**As paráfrases não são o problema.** São fiéis: das 334, só 4 têm palavra da
lista proibida, e as 4 repetem palavras do próprio tutor ("toma remédio desde
março", "levantou imediatamente"). O q186 reescrito diz "região íntima inchada",
"gotas de sangue", "comendo e brincando normal", "os cães da rua no portão" — e a
ficha do cio continua na 21ª posição, embora o texto de busca dela diga quase o
mesmo ("Tá saindo sangue pela vulva… A vulva tá inchada… Os machos da rua não
saem do portão; Ela tá ativa, comendo e brincando normal"). **Quando a busca erra
nesses casos, não é por falta de palavras certas no relato**: é a ordenação da
busca vetorial que não reconhece uma ficha que repete as frases do tutor. É
assunto do trilho A (como a ficha vira vetor, ou uma busca que também conte
palavras em comum), não da etapa de consulta.

## Conclusão da rodada

**O B-69 está testado e não funciona** nas fichas: nem o gatilho é forte (passo
1), nem o tradutor, acionado só nos casos de dúvida e proibido de diagnosticar,
traz a ficha certa (passo 2). O passo 3 (decisão) não roda. Junto com a rodada
17 do João, isso fecha a pergunta do tradutor para a arquitetura das fichas: ele
fica no código só como braço da ablação. É um resultado negativo medido, com o
critério escrito antes, e vai para o TCC assim.

Para o objetivo do Ryu ("INCERTO só quando falta informação do tutor"), sobram
dois caminhos, fora da etapa de consulta:

- **a IA conferir se cada ficha é do assunto** antes de usá-la (Self-Refine,
  [B-70](../backlog.md#b-70), trilho B2) — o q186 sem fichas foi acertado pelo
  Gemini, então tirar a ficha errada basta nesse caso;
- **a busca reconhecer a ficha que repete as palavras do tutor** (trilho A).

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `scripts/diagnostico_busca.py` | **novo** — notas e posição da ficha certa pela `/search/`, nos conjuntos de desenvolvimento |
| `scripts/experimento_tradutor_duvida.py` | **novo** — o tradutor só nos casos de dúvida, medido na busca |
| `evidencias/ryu/dados/2026-10-06-diagnostico-busca.jsonl`, `…-tradutor-na-duvida.jsonl` | **novos** — os dados por caso |
| `evidencias/backlog.md` | B-69 com o resultado |

Os dois scripts são instrumentos de experimento, sem teste automatizado: não
entram no caminho do sistema.

## Próximo passo

Levar ao time a conclusão do B-69 e o caso q186 como argumento para o B-70 e
para o trilho A. No trilho B1, seguir para o ponto 1 da lista combinada: medir se
o cadastro do pet melhora a decisão.
