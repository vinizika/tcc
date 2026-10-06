# A busca passa a enxergar o cadastro do pet

**Data:** 06/10/2026 · **Trilho:** B1 (Consulta) · **Rodada:** 22 · **Commit:** este

## O que foi feito

A [rodada 20](2026-10-06-20-o-cadastro-do-pet-ajuda.md) mostrou que o cadastro
do pet chega à IA que decide, mas **não chega à busca**: o app monta a consulta
só com o texto do tutor (`clinical_query`). Quando o fato decisivo está no
cadastro ("diabética, toma insulina"), a ficha do quadro grave nunca vem, e a
gata diabética ficou INCERTO nas duas repetições.

Esta rodada põe os **fatos clínicos do cadastro na frente do texto do tutor**,
só na consulta à busca, em linguagem simples e sem nenhuma instrução — por
exemplo, `Gato, 11 anos. Diabética, toma insulina duas vezes por dia.` seguido
do relato. O que a IA de decisão recebe não muda (o cadastro já ia no bloco
"Dados cadastrais").

Primeiro **mede só na busca** (sem modelo de linguagem, sem cota do Gemini);
depois, se passar, muda o app.

## Por quê

Melhoria 1 da lista que o Ryu aprovou em 06/10, depois das rodadas de teste.
Montar a consulta é a etapa de consulta, trilho B1.

**O cuidado que o Vinicius registrou** (rodada 20 dele): quando regras e texto de
orquestração do fluxo conversacional foram parar na busca, duas classificações
regrediram, e ele fixou a regra "só observações do tutor chegam à busca". O
cadastro é informação do tutor sobre o animal, não instrução; a medição abaixo
inclui uma checagem de que nada piora onde o cadastro não ajuda.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Entram espécie, idade e histórico; nome nunca | O nome não diz nada clínico e só polui o vetor |
| 2 | Raça e peso medidos à parte (variante V2) | Podem ajudar no filhote de raça pequena e atrapalhar no resto; decidir pelo dado |
| 3 | Os fatos vão **antes** do relato, numa frase curta | É como as fichas começam ("Ficha de triagem: … — cão") |

## Resultado esperado

_Escrito antes de rodar._ Consultas:

- **V0** — só o relato (o app hoje);
- **V1** — `<Espécie>, <idade>. <histórico>` + relato;
- **V2** — V1 com raça e peso.

| Medida | Esperado | Critério |
|---|---|---|
| Os 8 casos "A" dos pares da rodada 20 (o cadastro aponta para o quadro grave): ficha certa entre as 3 | V0: 5 de 8 (p4a, p5a, p8a de fora) → **V1: ≥ 7 de 8** | ≥ 7 |
| Os 8 casos "B" (o cadastro aponta para o quadro leve) | não perder nenhum que V0 já acerta | 0 perdas |
| **Não piorar** onde o cadastro só tem a espécie: calibração da prova 2 (61) e relatos independentes (122), com `Cão.`/`Gato.` na frente | queda ≤ 2 pontos no "entre as 3" | ≤ 2 pontos |

Se V1 passar, ele vira o padrão do app. V2 só entra se ganhar de V1 sem perder
nada.

## Resultado obtido

### Passo 1 — só a busca

`python scripts/experimento_busca_com_cadastro.py`, 206 relatos × 3 consultas;
dados em [`dados/2026-10-06-busca-com-cadastro.jsonl`](dados/2026-10-06-busca-com-cadastro.jsonl).

| Grupo | Ficha certa entre as 3: V0 → V1 → V2 | Em 1º: V0 → V1 → V2 |
|---|---|---|
| Pares "A" (8) | 5 → **6** → **7** | 4 → 5 → 5 |
| Pares "B" (7 com quadro) | 4 → 4 → 3 | 2 → 2 → 2 |
| Calibração da prova 2 (61) | 50 → 51 → 51 | 37 → 33 → 33 |
| Independentes (122) | 94 → 94 → 94 | 74 → 72 → 72 |

Caso a caso, nos pares "A" (posição da ficha certa, V0 → V1 → V2): a **gata
diabética** sobe de 5º para **1º** nas duas variantes; o **filhote** de 16º para
5º (V1) e 2º (V2, por causa da raça e do peso); a **piometra** de 38º para 5º.
A obstrução uretral desce de 1º para 2º (V1) e 3º (V2), ainda dentro.

**Contra o critério:**

| Parte | V1 | V2 |
|---|---|---|
| Pares "A" ≥ 7 de 8 | 6 ❌ (por um caso) | 7 ✅ |
| Pares "B": nenhuma perda | 0 perdas ✅ | 1 perda ❌ (p5b, vômito isolado: 2º → 5º) |
| Calibração e independentes: queda ≤ 2 pontos no "entre as 3" | +1,6 e 0 ✅ | +1,6 e 0 ✅ |

**Nenhuma das duas passa inteira.** V1 erra por um caso no primeiro critério; V2
acerta esse e perde um caso leve. Nos relatos em que o cadastro só tem a espécie,
nada piora no que chega à IA (as 3 fichas), mas o 1º lugar cai um pouco (37 →
33 e 74 → 72): pôr "Cão."/"Gato." na frente puxa a busca para as fichas da
espécie, às vezes trocando a ordem dentro das 3.

### Passo 2 — a decisão (desvio declarado do plano)

O plano dizia "se V1 passar, vira padrão". Não passou por um caso, e o caso que
motivou a rodada (a gata diabética) foi resolvido na busca pelas duas variantes.
Em vez de decidir só pela busca, meço **a decisão**, que é o que importa ao
tutor: os 20 casos da rodada 20, com o cadastro na IA **e** na busca (V1), duas
repetições, comparados com o braço "com cadastro" da rodada 20 (cadastro só na
IA).

**Resultado esperado** (_escrito antes de rodar_): a gata diabética (p5a) vira
EMERGENCIA nas duas repetições; nenhum outro caso piora em relação ao braço
"com cadastro" da rodada 20; controles iguais. **Critério para virar o padrão
do app:** as três coisas juntas.

**Resultado obtido** (40 decisões; dados em
[`dados/2026-10-06-cadastro-na-busca-decisao.jsonl`](dados/2026-10-06-cadastro-na-busca-decisao.jsonl)),
comparado com o braço "com cadastro" da rodada 20, caso a caso:

| Braço (repetição) | Pares certos (de 16) | Pares resolvidos | Emergências perdidas | Falsos alarmes | INCERTO | Controles |
|---|---|---|---|---|---|---|
| Cadastro só na IA (rodada 20, 1ª · 2ª) | 9 · 10 | 2 · 3 | 1 · 1 | 3 · 3 | 4 · 3 | 4 · 4 |
| **Cadastro na IA e na busca** (1ª · 2ª) | **8 · 8** | **1 · 1** | **2 · 2** | 3 · 3 | 5 · 5 | 4 · 4 |

**Não passa, e piora.** A gata diabética continua INCERTO nas duas repetições,
**mesmo com a ficha da cetoacidose em 1º lugar**; e o filhote (p4a), que a IA
acertava, passou a INCERTO nas duas. O único ganho foi o adulto sem apetite
(p4b), numa das repetições.

**Por quê, caso a caso:**

- **p4a, o filhote:** com "Cão, 2 meses. Filhote recém-chegado em casa" na
  frente, a busca trouxe as fichas de **recém-nascido que não mama** e de
  **parto normal** — assuntos de filhote, mas de outro quadro — e a IA respondeu
  INCERTO pedindo "o tempo sem comer e a temperatura". O cadastro puxou a busca
  para a palavra "filhote", não para o quadro. É o "INCERTO falso por ficha
  errada" da rodada 19, agora causado pelo cadastro.
- **p5a, a gata diabética:** a ficha certa chegou, mas a ficha de leitura da
  cetoacidose é curta e diz que o quadro é "bebe muito e urina muito **somado
  a** vômito e prostração". O relato não fala de sede nem de urina, e a IA,
  lendo a ficha ao pé da letra, não viu o quadro completo. A ficha de leitura
  dela não tem a linha "sinais que o tutor costuma relatar" — é uma das células
  vazias da etapa 2 do mapa que a rodada 32 do João vai preencher
  ([B-61](../backlog.md#b-61)).

## Conclusão da rodada

**A busca com o cadastro não vira o padrão do app.** Melhora a posição da ficha
nos casos em que o cadastro carrega o fato decisivo, mas, na decisão, troca
acertos por INCERTO falsos: o cadastro na consulta puxa fichas do "tipo de
animal" (filhote, recém-nascido) em vez do quadro. Nenhuma linha do backend
mudou nesta rodada; o que fica é o instrumento (`experimento_busca_com_cadastro.py`
e o braço `com_cadastro_e_busca` do `experimento_cadastro_pet.py`) e o
resultado negativo, medido com critério escrito antes.

Os dois achados vão para os donos:

- **Para o João (rodada 32):** a ficha de leitura da cetoacidose exige "sede e
  urina somadas a vômito"; uma diabética em insulina que vomita e não come
  deveria bastar — pergunta para a ASAVET.
- **Para o trilho A:** a busca vetorial é puxada por palavras de "tipo de
  animal" ("filhote", "2 meses") mais do que pelos sinais.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `scripts/experimento_busca_com_cadastro.py` | **novo** — V0/V1/V2 só na busca |
| `scripts/experimento_cadastro_pet.py` | braço `com_cadastro_e_busca` (`--bracos`) |
| `evidencias/ryu/dados/2026-10-06-busca-com-cadastro.jsonl`, `…-cadastro-na-busca-decisao.jsonl` | **novos** |

## Próximo passo

Melhoria 2 da lista: a frase vaga vira pedido de mais informação.
