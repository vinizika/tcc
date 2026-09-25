# Como achar a ficha certa: bge-m3, as 3 mais próximas, sem porta e sem âncoras

**Data:** 24/09/2026 (escrita em 25/09 a partir do registro da autópsia) ·
**Trilho:** B2, olhando o sistema inteiro · **Rodada:** 16 · **Commits:** este

> Rodada de **experimento**, com uma troca de verdade feita numa cópia do
> código. Nada no repositório mudou. Junta **quatro peças da busca**: o
> embedding, a porta de entrada do contexto, as âncoras e os títulos. A regra
> 3 do padrão pede uma mudança por rodada. Aqui as quatro foram medidas
> separadas, mas a decisão só faz sentido em conjunto: trocar só o embedding
> não resolve (resultado 2). O método está na
> [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md#como-medimos-vale-para-as-rodadas-14-a-21).

## O que foi feito

1. **Inventário** do que muda no código numa troca de embedding.
2. **Seis embeddings comparados**, só por vetor, com o relato cru como
   consulta, em duas bases: as 61 fichas do mapa e os 3.481 trechos
   acadêmicos. Os modelos: o MiniLM de hoje, o mpnet multilíngue, e5-small,
   e5-base, e5-large e bge-m3.
3. **A troca de verdade** para o bge-m3, numa cópia de `fceab20`: o diff, as
   suítes e o tempo de indexar.
4. **A porta de entrada.** Na busca e depois na decisão, com os três
   atendentes, cinco jeitos de escolher o que entra no prompt:
   - a porta de hoje (0,72);
   - a porta recalibrada no `dev`;
   - a ficha mais próxima, sempre;
   - a mais próxima só se ganhar da 2ª por uma margem;
   - **as 3 mais próximas, sem porta**.
5. **As âncoras.** Achar por que a obstrução uretral some, e testar três
   consertos.
6. **Os títulos.** Medir se o título genérico das fichas de documento sustenta
   a busca.

## Por quê

A [rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md) mostrou que,
com a ficha certa na mão, qwen e Gemini não perdem emergência. O que falta é
a busca entregar essa ficha. E a busca de hoje não entrega, por três motivos:
- **O MiniLM**, nas fichas, põe a certa em 1º lugar em ~20% dos relatos.
- **A porta de 0,72** foi calibrada na escala de nota dele. Na base acadêmica,
  ela deixa 116 de 122 relatos independentes sem nenhum contexto
  ([rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md)).
- **As âncoras** escondem justamente o quadro mais letal do mapa.

O João perguntou se trocar o embedding é difícil, e se cada uma dessas peças
vale o retrabalho. Esta rodada responde com teste antes e depois.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **O relato cru é a consulta** em todos os testes desta rodada | Mede a busca sozinha. O tradutor é medido à parte, na [rodada 17](2026-09-24-18-tradutor-desligado.md) |
| 2 | **bge-m3** no lugar do MiniLM | Empata com o e5-large no critério, não precisa de prefixo e é o único multilíngue grande que não desaba na base em inglês (resultado 1) |
| 3 | A troca de embedding **mantém a receita de trechos** da base acadêmica (96/16 tokens) | Para não mudar duas coisas ao mesmo tempo |
| 4 | **As 3 fichas mais próximas, sem porta**, em vez da porta de confiança | É o que passou no critério escrito às 04h38, nos relatos de quem não viu o mapa (resultado 4). A porta, que protegia contra a ficha errada, barrava também a certa |
| 5 | **Âncoras fora** (conserto F3) | Das três correções, é a mais simples que passa no critério |
| 6 | **Título real na citação**; o rótulo do assunto, se ficar, explícito ("Assunto: …") | O título genérico quase não pesa na busca; o defeito dele é de honestidade, porque é mostrado ao tutor como a fonte |

## Resultado esperado

Escrito antes de rodar (plano da madrugada, 00h56, e cadernos das frentes C e
D):

| Peça | Critério escrito antes |
|---|---|
| Embedding (00h56) | "Fácil" se couber em cerca de um dia: lista exata de arquivos e do que muda, sem reescrever o pipeline, suítes passando. O modelo escolhido é **o menor que ficar a até 2 pontos do melhor** no 1º lugar, em média nos três lotes, com consulta abaixo de 200 ms na CPU |
| Porta (00h56) | A porta **mais simples** que zere ou quase zere as emergências perdidas sem subir os falsos alarmes, e que se mantenha na calibração e na régua |
| 3 fichas sem porta (04h38) | Fica se reduzir **em pelo menos 1/3** as emergências perdidas nos relatos de quem não viu o mapa, sem subir **mais de 2** os falsos alarmes da prova + régua |
| Âncoras (01h45) | O conserto fica se trouxer a obstrução para o contexto nas três frases e não piorar **nenhum** caso dos 134. Entre os que passarem, o mais simples |
| Títulos (00h56) | A hipótese de 23/09 era que o título genérico funciona como rótulo escondido do assunto. Se o título real derrubar a busca, a hipótese se confirma e o rótulo tem de ficar explícito |

## Resultado obtido

### 1. O embedding: bge-m3, e só junto com as fichas em português

Só vetor, relato cru. P@1 = assunto certo em 1º lugar; P@3 = entre os três
primeiros. Lotes `dev` / calibração / régua (47 / 16 / 66 casos com assunto):

| Modelo | Dim. | Tamanho | Fichas do mapa, P@1 | Fichas, P@3 | Base acadêmica, P@1 | Consulta (CPU) |
|---|---|---|---|---|---|---|
| MiniLM multilíngue (o de hoje) | 384 | 118 M | 0,23 / 0,12 / 0,26 | 0,45 / 0,38 / 0,41 | 0,19 / 0,12 / 0,20 | 14 ms |
| mpnet multilíngue | 768 | 278 M | 0,36 / 0,25 / 0,44 | 0,72 / 0,50 / 0,68 | 0,21 / 0,06 / 0,26 | 29 ms |
| e5-small | 384 | 118 M | 0,55 / 0,75 / 0,67 | 0,79 / 0,94 / 0,83 | 0,06 / 0,00 / 0,04 | 17 ms |
| e5-base | 768 | 278 M | 0,68 / 0,75 / 0,65 | 0,85 / 0,88 / 0,85 | 0,00 / 0,06 / 0,06 | 31 ms |
| e5-large | 1024 | 560 M | 0,72 / 0,88 / 0,79 | 0,89 / 0,94 / 0,91 | 0,04 / 0,06 / 0,08 | 99 ms |
| **bge-m3** | 1024 | 568 M | **0,83 / 0,81 / 0,79** | **0,96 / 0,94 / 0,91** | 0,09 / 0,19 / 0,27 | 119 ms |

- **Nas fichas, qualquer multilíngue maior deixa o MiniLM muito para trás**: de
  ~0,2 para ~0,7 a 0,8 no 1º lugar. Até o e5-small, do mesmo tamanho do
  MiniLM, triplica o acerto.
- **Na base acadêmica, o e5 desaba**, de 0,19 para ~0,05. A causa é o viés de
  língua. Com consultas em português, o e5 põe em 1º lugar os poucos trechos
  em português da base: 96 trechos, de 6 assuntos. No e5-small, **129 de 129**
  primeiros lugares caíram num desses 6 assuntos; no e5-large, 111 de 129. O
  MiniLM também sofre, menos: 56 de 129 no assunto que tem mais trechos em
  português (engasgo).
- **Pelo critério**, bge-m3 e e5-large empatam: 0,81 e 0,80 de média no 1º
  lugar, tamanhos quase iguais, os dois abaixo de 200 ms. Três motivos
  desempatam para o bge-m3:
  - ele não precisa de prefixo (`query:`/`passage:`), então a função de
    embedding do Chroma serve como está;
  - ele é o único grande que **não desaba na base acadêmica**, que continua
    no sistema como braço da ablação e como fonte das citações;
  - nos testes seguintes, com as fichas escritas por IA e em inglês, ele se
    manteve na frente ([rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md#3-português-e-não-inglês)).

### 2. Trocar só o embedding, mantendo a base acadêmica, não resolve

Reindexei os 3.481 trechos com o bge-m3 (11 min na CPU) e rodei a busca de
produção de hoje sem mexer em mais nada: roteador, reranker e porta 0,72.

| Lote | 1º lugar (bge-m3) | Assunto certo no prompt | Prompt vazio | Só assunto errado |
|---|---|---|---|---|
| `dev` (47) | 25 | 8 | 39 | 0 |
| calibração (16) | 10 | 3 | 13 | 0 |
| régua (66) | 42 | 18 | 46 | 2 |
| relatos de quem não viu o mapa (61) | 22 | **3** | **58** | 0 |

O 1º lugar melhora um pouco (77 de 129, contra 60 de 129 com o MiniLM). Mas a
porta, calibrada no MiniLM, **fecha quase tudo**: 98 de 129 prompts vazios, e
58 de 61 nos relatos independentes. **Embedding, fichas e porta são uma
mudança só.**

### 3. A troca no código é pequena

Na cópia de `fceab20`, a troca para o bge-m3 mexeu **só no
`embedding_config.py`**: o nome do modelo, a revisão fixada
(`5617a9f61b028005a4858fdac845db406aefb181`), as dimensões (384 → 1024) e o
teto de tokens (128 → 512). **Nenhuma linha do pipeline.**
- **Suíte do backend:** 242 passavam antes; depois, **241 passaram e 1 falhou**.
  Era o `test_retrato_descreve_o_embedder_e_o_chunking`, que afirma
  `"MiniLM" in embedding_model`, uma afirmação fixa sobre o nome.
- **Tempo de indexar:** as 61 fichas em ~25 s, incluindo carregar o modelo; os
  3.481 trechos acadêmicos em 11 a 16 min na CPU.
- **Consulta:** ~0,12 s na CPU. O modelo tem ~2 GB.

**Resposta à pergunta do João: não é difícil.** O trabalho de verdade não está
no embedding: está na porta de entrada, que foi calibrada na escala do modelo
antigo.

A implementação completa é maior que isso, porque o sistema precisa abrir cada
coleção com o embedding da própria receita (as fichas no bge-m3, a base
acadêmica no MiniLM, para a ablação). Isso é trabalho das rodadas de
implementação.

### 4. A porta de entrada: do porteiro às três fichas

**Na busca.** Fichas do mapa com o bge-m3, na busca de produção (roteador +
reranker + porta):

| Porta | Ficha certa no prompt (`dev` · calib · régua) | Prompt vazio | Só a ficha errada |
|---|---|---|---|
| a de hoje (0,72 e o piso 0,721) | 20/50 · 11/18 · 33/66 | 30 · 7 · 29 | 0 · 0 · 4 |
| recalibrada no `dev` (0,56) | 40/50 · 13/18 · 50/66 | 1 · 0 · 1 | 9 · 5 · 15 |
| a mais próxima, sempre | 39/47 · 13/16 · 52/66 | 0 | 8 · 3 · 14 |

Com o bge-m3, **a porta de hoje virou uma porta de confiança**: deixa passar
metade dos casos, e quase só a ficha certa. A porta recalibrada deixa passar
quase tudo, com a ficha errada sozinha em 18 a 28% dos casos. Uma porta por
margem (a 1ª ficha só entra se ganhar da 2ª por 0,011, calibrada no `dev`)
não separa melhor:
- nos relatos de quem não viu o mapa, mantém 31 de 34 e 27 de 29 das certas;
- mas corta só 12 de 27 e 16 de 32 das erradas.

A nota da ficha certa e a da errada se sobrepõem, e nenhum limiar separa as
duas.

**Na decisão, prova + régua** (74 emergências · 58 leves). Emergências
perdidas · falsos alarmes:

| O que entra no prompt | llama3.2:3b | qwen3:8b | gemini-3.5-flash-lite |
|---|---|---|---|
| nada | 14 · 2 | 7 · 0 | 0 · 3 |
| e5-base, a mais próxima | 0 · 6 | 6 · 0 | 6 · 0 |
| e5-base, as 3 mais próximas | 1 · 8 | 2 · 2 | — |
| e5-base, a mais próxima + a gêmea | 0 · 7 | 5 · 0 | — |
| MiniLM de produção, as 3 primeiras | 1 · 11 | 9 · 1 | — |
| **bge-m3 + a porta de hoje** | 4 · 4 | **2 · 0** | **0 · 2** |
| **bge-m3, as 3 mais próximas, sem porta** | 2 · 4 | 3 · 1 | 1 · 0 |
| ficha certa (oráculo) | 0 · 2 | 0 · 0 | 0 · 1 |

Na prova + régua, **a porta de hoje com bge-m3 e fichas foi a melhor
configuração para o qwen** (7 → 2 perdas, 0 falsos alarmes). Ela também
resolveu a armadilha do Gemini: as 6 perdas com a ficha e5 errada, da
[rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md#4-a-etapa-2-o-mapa-está-vazio-e-a-ficha-errada-custa-caro),
somem. **Pelo critério das 00h56, às 04h28, a porta ficava.**

**A virada, nos relatos de quem não viu o mapa** (76 · 46). O teste foi
escrito às 04h38, antes de rodar:

| qwen3:8b | Prova + régua | Relatos de quem não viu o mapa |
|---|---|---|
| nada | 7 · 0 | 21 · 9 |
| bge-m3 + a porta de confiança | 2 · 0 | 21 · 11 |
| **bge-m3, as 3 mais próximas, sem porta** | **3 · 1** | **7 · 7** |
| ficha certa (oráculo) | 0 · 0 | 0 · 4 |

- **Pareado porta × 3 fichas, emergências:**
  - relatos de quem não viu o mapa: **15 × 1 (p = 0,0005)**;
  - prova + régua: 2 × 3 (p = 1,0).
- **Por etapa, nos independentes:** na etapa 1, 9 → 1 perdas; na etapa 2,
  12 → 6. Na prova + régua, a etapa 2 piora um pouco (1 → 3), justamente onde
  as fichas do mapa são magras.
- **No llama** também melhora nos independentes (37 → 29; pareado 10 × 2,
  p = 0,04), mas ele continua ruim
  ([rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md)).
- **Passa no critério:** reduz as perdas em 2/3 (21 → 7) e sobe 1 falso
  alarme na prova + régua (0 → 1).

**Por que funciona.** Nos relatos de quem não viu o mapa, a ficha certa fica
em 1º lugar em só metade das vezes, mas fica **entre as três primeiras em
três de cada quatro**:

| Fichas do mapa, bge-m3 | 1º lugar | Entre as 3 |
|---|---|---|
| prova + régua (129) | 104 (80,6%) | 120 (93,0%) |
| relatos de quem não viu o mapa (122) | 63 (51,6%) | 93 (76,2%) |

O vocabulário de quem não viu o mapa não é o do mapa, e as notas ficam mais
baixas. Por isso a porta, que protegia contra a ficha errada, barrava também
a certa: com ela, **89 dos 122 relatos independentes** chegavam ao qwen sem
nenhuma ficha. Com as três na mão, o qwen reconhece a que é do caso. E a ficha
certa neutraliza o tom do tutor, como a
[rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md) mostra.

**Na configuração final**, a busca usa as fichas de busca escritas por IA
([rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)) e acerta mais:
- prova + régua: 107/129 (82,9%) em 1º e 123/129 (95,3%) entre as 3;
- relatos independentes: 74/122 (60,7%) e 94/122 (77,0%);
- piloto da prova 2: 16/40 e 32/40.

### 5. As âncoras que escondiam a obstrução uretral

**A causa**, achada lendo o código e a base, às 01h45 de 24/09:
- Os 60 trechos dos dois documentos de obstrução uretral têm
  `retrieval_anchors`: urine, urinary, urinate, urination, pee, bladder,
  dysuria, stranguria, urina, urinar, urinario, urinário, **xixi**, bexiga.
  Elas entraram em 20/09 (`5ed9bfd`).
- O reranker (`RerankerClient._eligible`) **descarta** qualquer trecho com
  âncoras se nenhuma âncora aparece no relato. "Vai na caixa e não sai nada"
  e "não consegue mijar" não têm nenhuma dessas palavras.
- **O pior:** nessas duas frases, o roteador do próprio time aponta obstrução
  uretral com confiança máxima (1,0). O vocabulário `retrieval_terms.json`
  tem "vai na caixa e nao sai nada", "faz forca", "chora quando tenta". O
  roteador acerta, e a âncora veta o documento que ele escolheu.
- Outros quatro documentos também têm âncoras (uva e xilitol; cobra e
  escorpião; carrapato; pulga), e o mesmo risco vale para eles.

**Três consertos**, na busca de produção (MiniLM + reranker + porta), nos 134
casos e em 16 frases extras escritas de propósito:
- **F1:** se o roteador aponta o assunto com confiança, os trechos dele são
  elegíveis mesmo sem âncora no relato;
- **F2:** âncoras ampliadas com o vocabulário do roteador e sinônimos óbvios;
- **F3:** sem âncoras.

Nas frases extras, C = o assunto certo entra no prompt; 5 = aparece entre os
cinco primeiros, mas não entra; X = nem aparece.

| Frase | Hoje | F1 | F2 | F3 |
|---|---|---|---|---|
| "meu gato vai na caixa e não sai nada, faz força e mia" | X | **C** | **C** | **C** |
| "meu gato não consegue mijar, fica tentando e chora" | X | **C** | **C** | **C** |
| "entra e sai da caixa de areia toda hora e não sai nada" | X | X | 5 | 5 |
| "fazendo força na caixinha e só sai umas gotinhas" | X | **C** | **C** | **C** |
| "gato macho agachado na caixa faz tempo, chora, barriga dura" | X | **C** | X | **C** |
| "não consegue fazer xixi desde ontem… miando de dor" (a da régua) | 5 | 5 | 5 | 5 |
| "comeu um cacho de uvas agora há pouco" | 5 | 5 | 5 | 5 |
| "comeu um pacote de frutinhas secas roxas do panetone" | X | X | 5 | 5 |
| "foi picado por uma cobra no sítio" | 5 | 5 | 5 | 5 |
| "uma jararaca mordeu meu cachorro" | X | X | 5 | 5 |
| "achei uns carrapatos, mas ele está bem" | 5 | 5 | 5 | 5 |
| "achei uns bichinhos grudados na orelha, parecem sementes" | X | X | X | X |
| "meu gato está se coçando muito e tem pulgas" | C | C | C | C |
| "não para de se coçar e morder as costas" | X | X | X | 5 |

- **Nos 134 casos, os três consertos mudam o contexto de um caso só** (régua
  b09, pulga, que passa a receber a ficha certa). **Nenhum caso piora**:
  nenhum perde o assunto certo, nenhum ganha um assunto errado.
- **Nas frases extras**, dois efeitos colaterais, nenhum de risco:
  - com F1 e F3, na frase dos "bichinhos grudados" (carrapato), entra a ficha
    de pulga (os dois quadros são leves);
  - na das "frutinhas roxas", o documento de raticida entra no prompt em
    todas as variantes, inclusive hoje.
- **Pelo critério, F3.** F1 e F3 levam a obstrução ao prompt em 4 das 5
  formas de contar. F2, ampliar a lista, é o pior dos três: conserta 3 de 5 e
  nunca vai acabar, porque sempre haverá um "mijar", uma "jararaca" ou uma
  "frutinha" que a lista não tem. É a fragilidade das âncoras em si.
- **Com as fichas, o problema some sozinho**: elas não têm âncoras. O conserto
  vale para a base acadêmica, que continua como braço da ablação e fonte das
  citações.

### 6. Os títulos genéricos

Nas fichas de documento (`backend/data/documents/*.json`), o título real do
artigo foi trocado por um título genérico com o nome do assunto. Reindexei a
base acadêmica (só vetor) com quatro variantes. Dos 66 títulos reais, 47
foram achados nos metadados dos PDFs; os outros ficaram com o de hoje. P@1 em
`dev` / calibração / régua:

| Título no texto indexado | MiniLM (o de hoje) | mpnet multilíngue |
|---|---|---|
| hoje (genérico) | 0,15 / 0,06 / 0,21 | 0,26 / 0,12 / 0,21 |
| real do artigo | 0,09 / 0,00 / 0,21 | 0,21 / 0,06 / 0,24 |
| sem título | 0,11 / 0,12 / 0,17 | 0,17 / 0,19 / 0,18 |
| real + "Assunto: <quadro do mapa>" | 0,13 / 0,06 / **0,27** | **0,28** / 0,00 / **0,26** |

O título genérico ajuda um pouco no `dev` (3 casos a mais que o real) e nada
na régua, tudo dentro do ruído destas amostras. **A hipótese de 23/09 não se
confirma com força**: o título não é o que sustenta a busca, o conteúdo é o
problema.

O defeito do título genérico é outro. **Ele é mostrado ao tutor como a fonte
citada e descreve o artigo de forma enganosa.** O conserto é barato: título
real para citar e, se quiserem, o rótulo do assunto explícito. Com as fichas,
a base acadêmica deixa de entrar no prompt, e o título real passa a aparecer
**na citação**: a ficha usada e o documento aprovado por trás dela.

## O que mudou no repositório

| Arquivo | O que é |
|---|---|
| esta evidência | |
| `data/evaluation/autopsia2/resultados_por_caso.csv` (versionado na rodada 14) | as condições desta rodada: `e5_fichas_top1`, `e5_fichas_top3`, `e5_fichas_top1_gemea`, `rag_fichas_top3`, `ctxarq_bge_fichas_top1`, `ctxarq_bgeprod_fichas` (bge-m3 + porta), `ctxarq_bge_fichas_top3` (3 sem porta), `ctxarq_bgeprod_fichase1` (só etapa 1), `oraculo_ficha` |
| `data/evaluation/autopsia2/busca/` (versionado na rodada 14) | as buscas desta rodada, por caso: os seis embeddings nas duas bases (`embed_fichas.json`, `embed_academica.json`), a busca em cada base de fichas, com a porta por margem (`busca_fichas.json`), a busca de produção com bge-m3 (`producao_bge_fichas.json`, `producao_bge_academica.json`), as âncoras nos 134 casos e nas frases extras (`ancoras_*.json`) e os títulos (`titulos.json`) |

Nenhum código mudou no repositório: a troca foi feita numa cópia. O diff muda
4 constantes do `embedding_config.py` e entra com a implementação.

## Observações

**1. Pior caso, "entregar só a etapa 1".** Com a porta ligada, o resultado do
qwen fica idêntico, caso a caso, com a base inteira ou só com as 31 fichas da
etapa 1 (2 · 0 na prova + régua; 21 · 11 nos independentes). As fichas magras
da etapa 2 nunca passavam da porta. Com as 3 fichas sem porta, um relato da
etapa 2 numa base só da etapa 1 receberia 3 fichas erradas. Esse cruzamento
não foi rodado. Deixou de importar porque a etapa 2 ganhou fichas de busca
([rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)).

**2. A porta continua como opção.** Com o bge-m3 as notas vivem noutra faixa
(de ~0,55 a ~0,70 nas fichas). Qualquer limiar precisa ser recalibrado, e a
"porta de confiança" fica como braço da ablação (bge-m3 + fichas + porta
0,72). Ela é a melhor configuração na prova e a pior nos relatos de quem não
viu o mapa, o que mostra o quanto a prova atual é otimista.

**3. `RERANK_TOP_K` e `CONTEXT_TOP_K`** ([B-17](../backlog.md#b-17)). Com a
busca vetorial pura e as 3 mais próximas, o que chega ao prompt é o que a busca
devolve, sem reordenação: a sobreposição das duas chaves deixa de importar no
caminho padrão.

**4. Re-ranking por cross-encoder.** Prometido no TCC1, não foi testado. Com
as 3 fichas, o que ele poderia melhorar é o "entre as 3" dos relatos de quem
não viu o mapa (77%). Na prova + régua isso já está em 95%.

**5. A prova escolhe a porta errada.** Na prova + régua, a porta de confiança
empata com as 3 fichas (2 × 3). Só nos relatos de quem não viu o mapa aparece
a diferença (15 × 1). Se a decisão tivesse sido tomada só com a prova de hoje,
teríamos ficado com o porteiro.

## Deixado para depois

- **A régua de recuperação nas fichas como instrumento oficial**
  ([B-67](../backlog.md#b-67)). Esta rodada mediu a busca com scripts da
  autópsia. A régua do time (`run_retrieval_eval.py`) precisa ler a coleção de
  fichas, contar o "entre as 3" e ter uma linha de base citada.
- **Re-ranking por cross-encoder**: fica para a ablação, se houver tempo (ver
  a atualização do [B-02](../backlog.md#b-02)).

## Próximo passo

Com a busca feita no relato cru, a pergunta seguinte é o que o tradutor
(reescrita, multi-query e HyDE) faz com essa busca e com a decisão: a
[rodada 17](2026-09-24-18-tradutor-desligado.md).
