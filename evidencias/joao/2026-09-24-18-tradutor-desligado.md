# O tradutor desligado: reescrita, multi-query e HyDE, testados com os dois geradores

**Data:** 24/09/2026 (escrita em 25/09 a partir do registro da autópsia) ·
**Trilho:** B2, olhando o sistema inteiro · **Rodada:** 17 · **Commits:** este

> Rodada de **experimento**. Nada no sistema mudou. "O tradutor" é a etapa de
> consulta do pipeline: as três técnicas que transformam o relato do tutor
> antes da busca. Esta rodada mostra o que cada técnica produz, se isso
> ajuda a busca e a decisão, e por que elas ficam **desligadas por padrão**.
> Elas continuam no código, como braço da ablação. O método está na
> [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md#como-medimos-vale-para-as-rodadas-14-a-21).

## O que foi feito

1. **Ler o código** (`ChatPipeline._build_queries`, em `fceab20`): o que cada
   técnica faz, com qual prompt e quem a gera.
2. **Gerar e certificar os defeitos.** As saídas das três técnicas, caso a
   caso, com os dois geradores que o sistema usa:
   - o `llama3.2:3b` local, que é o que roda sem a chave do Gemini, nos 134
     casos da prova + régua;
   - o `gemini-3.5-flash-lite`, que roda com a chave, nos 50 casos do `dev`,
     porque a cota não deu para mais.
   
   Um juiz e regras determinísticas conferem cada saída.
3. **O efeito na busca**, sem modelo de linguagem, em duas buscas: a de hoje
   (base acadêmica, MiniLM, reranker e porta) e a proposta (as fichas, com
   bge-m3 e com e5).
4. **Três consertos**, medidos do mesmo jeito.
5. **O efeito na decisão:** a tabela 2×2, base (artigos × fichas) × tradutor
   (desligado × ligado), com qwen e llama.

## Por quê

A [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md) mostrou o
pipeline completo inventando consultas: "Diagnóstico de coccidiose em cães",
para um relato de secreção ocular. No conjunto antigo, ele troca 5 emergências
perdidas por 10 falsos alarmes. Os próprios prompts pedem para o modelo chutar
o diagnóstico: o do multi-query pede "sintomas, causa provável, conduta"; o do
HyDE, "possíveis causas e a conduta esperada".

E a arquitetura proposta muda a premissa do tradutor. Ele foi feito para
aproximar a fala do tutor da linguagem técnica dos artigos. Com fichas
escritas na língua do tutor ([rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md)),
talvez não sobre distância para encurtar. O João pediu que o motivo de
desligar essa parte fique claro e testado: nas duas bases, com o tradutor
ligado e desligado.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **Dois geradores**: o llama (produção sem chave) e o Gemini (produção com chave) | O sistema de hoje usa os dois, conforme a chave e a cota. Um defeito só do modelo pequeno não condenaria a técnica |
| 2 | O Gemini gerou pelo **próprio `GeminiQueryClient` do projeto**, com os mesmos prompts e o mesmo pós-processamento; só a chamada foi trocada por uma sem fallback | Mede a integração real, não uma imitação dela |
| 3 | **Juiz** `gemini-3.1-flash-lite`, em lotes, mais as **regras do próprio código** (troca de espécie; `_contains_unwarranted_urgency`) e a minha leitura de uma amostra | O juiz também erra, e a leitura mediu isso (resultado 2) |
| 4 | **Critério de ficar ligado** (00h56): subir o 1º lugar da busca em pelo menos 3 pontos sobre o relato cru, sem piorar as emergências perdidas nem os falsos alarmes | Técnica que não melhora a busca e custa tempo e cota não se justifica |
| 5 | Na 2×2, o tradutor ligado usa as consultas **geradas pelo llama** | É o único gerador com saída para os 296 casos. O do Gemini foi medido na busca, no `dev` (resultado 3) |
| 6 | **Desligar por padrão e manter no código**, religável por preset | A ablação precisa mostrar esse resultado. E, na base acadêmica, o tradutor ajuda o llama (resultado 5) |

## Resultado esperado

Escrito antes de rodar (plano da madrugada, 00h56):

> Uma técnica fica ligada só se subir o 1º lugar da busca em **≥ 3 pontos**
> sobre o relato cru e não piorar emergências perdidas nem falsos alarmes na
> classificação. Senão, fica desligada por padrão e vira braço da ablação.

Os três consertos seguiram o mesmo critério. A tabela 2×2 da noite de 24/09
**não teve critério próprio**: foi pedida para confirmar a decisão com a
arquitetura completa, e o critério que vale é o de cima.

## Resultado obtido

### 1. O que o tradutor faz hoje

A etapa de consulta (`_build_queries`) faz, nesta ordem:
1. **Reescrita.** O relato vira uma frase "técnica". Se a reescrita trouxer um
   termo de urgência que o relato não tinha, é descartada (a trava do
   [B-08](../backlog.md#b-08)).
2. **Multi-query** sobre a reescrita: 3 consultas curtas, "cada uma abordando
   um aspecto clínico diferente (sintomas, causa provável, conduta)".
3. **HyDE** sobre a reescrita: um "trecho de protocolo" hipotético com
   "quadro clínico, possíveis causas e a conduta esperada".
4. A busca recebe `[reescrita] + variações + [HyDE]`. O reranker usa o relato
   original para o roteador e a elegibilidade.

**Quem gera** é o `HybridQueryClient`. Com a chave, usa o Gemini. Se o Gemini
falha, a reescrita e o multi-query **caem para o llama local sem avisar**, e
o HyDE some. A trava contra urgência vigia só a reescrita, não o multi-query
nem o HyDE.

### 2. Os defeitos, certificados com os dois geradores

**Com o llama** (134 casos), porcentagem das saídas:

| Técnica | Inventa sinal | Insere diagnóstico | Insere urgência (juiz / regra do código) | Fala de conduta | Troca a espécie (juiz) |
|---|---|---|---|---|---|
| Reescrita | 54% | 17% | 1% / 0% | 2% | 1% |
| Multi-query sobre a reescrita (produção) | 54% | **45%** | 9% / 6% | **81%** | 1% |
| HyDE sobre a reescrita (produção) | **86%** | **86%** | **34%** / 25% | **100%** | 2% |
| Multi-query sobre o relato | 47% | 37% | 13% / 8% | 69% | 1% |
| HyDE sobre o relato | 88% | 87% | 27% / 26% | 99% | 1% |

**O juiz é confiável no llama.** Li à mão 10 reescritas que ele marcou como
"inventa sinal", e 9 estavam bem marcadas. Exemplos reais:
- "a cabeça ficou torta, cambaleando, olhos tremendo" virou "**paralisia
  facial**, ataxia… possivelmente causados por **trauma craniano**";
- "balançando a cabeça e coçando a orelha, **sem perder o equilíbrio**" virou
  "apresentando **balanço vestibular**". O tutor negou justamente isso;
- "veneno de rato, fraco, gengiva pálida, sangrando pelo nariz" virou
  "**desidratação, dor bucal** e hemorragia nasal". Sumiram "fraco" e
  "gengiva pálida", os sinais de gravidade;
- "corrimento com pus, bebendo muita água" virou "sintomas de **cio**… e
  comportamento de **desidratação**". É o quadro clássico de piometra;
- p37, permetrina **em gato**, virou "**Cão** apresentando sintomas de reação
  adversa… **suor excessivo**". A reescrita trocou a espécie, e a permetrina
  é tóxica justamente para gatos;
- HyDE: "**Cálculo Renal Agudo** em Gatos", para um relato de xixi fora da
  caixa sem esforço; "Infecção por **Parvovirus**… administração imediata de
  **antibióticos**".

**Com o Gemini** (50 casos do `dev`, mesmo juiz), comparado ao llama no mesmo
lote:

| Técnica | Inventa sinal (juiz) | Insere diagnóstico | Insere urgência (juiz / regra) | Fala de conduta |
|---|---|---|---|---|
| Reescrita — llama / Gemini | 56% / 46%\* | 18% / 12% | 2% / 0% | 4% / 2% |
| Multi-query — llama / Gemini | 58% / 16% | 44% / **76%** | 8% / 12% | 80% / 82% |
| HyDE — llama / Gemini | 84% / 78% | 88% / **90%** | 28% / **56%** (regra: 64%) | 100% / 100% |

\* **No Gemini, o juiz exagera.** Li 6 reescritas marcadas como "inventa
sinal", e quase todas são traduções técnicas corretas: "coração disparado" →
taquicardia; "barulho estranho tentando respirar" → estridor; "indo mais vezes
na caixinha" → polaquiúria; "focinho inchando" → angioedema. **A reescrita do
Gemini é fiel; a do llama, não.**

No multi-query e no HyDE, o Gemini nomeia o diagnóstico **ainda mais** que o
llama, e em geral acerta o nome. Ele faz isso porque o prompt pede. Também fala
de tratamento em 82% a 100% das saídas, e o HyDE dele insere urgência em mais
da metade. **O problema está no pedido, não no modelo:** o sistema diagnostica
antes de ler as fontes, e, se o chute estiver errado, a busca vai atrás do
documento errado.

**Pelo que as técnicas produzem, as três não funcionam como deveriam**, com os
dois geradores:
- a reescrita do llama distorce sinais em metade dos casos;
- o multi-query nomeia doença em 45% (llama) a 76% (Gemini) das saídas e fala
  de tratamento em ~80%;
- o HyDE inventa diagnóstico e conduta em quase todas.

### 3. O efeito na busca

**Com o llama gerando** (129 casos com assunto; fração com o assunto certo em
1º lugar):

| Consulta enviada à busca | Busca de hoje: certo em 1º | Busca de hoje: certo **no prompt** | Fichas + bge-m3: 1º | Fichas + e5-base: 1º |
|---|---|---|---|---|
| V0 · relato cru | 0,47 | 0,21 | **0,81** | **0,67** |
| V1 · só a reescrita | 0,52 | 0,33 | 0,65 | 0,59 |
| V2 · relato + multi-query | 0,47 | 0,56 | 0,67 | 0,53 |
| V3 · relato + HyDE | 0,47 | 0,45 | 0,64 | 0,62 |
| V5 · produção sem HyDE (o que roda sem chave) | 0,50 | 0,54 | 0,64 | 0,53 |
| V4 · cadeia de produção completa | 0,51 | 0,57 | 0,57 | 0,57 |

**Com o Gemini gerando** (lote `dev`, 47 casos com assunto):

| Consulta | Busca de hoje: 1º | Busca de hoje: certo no prompt | Fichas + bge-m3: 1º | Fichas + e5-base: 1º |
|---|---|---|---|---|
| relato cru | 0,40 | 0,17 | **0,83** | **0,68** |
| só a reescrita | 0,34 | 0,26 | 0,62 | 0,49 |
| produção sem HyDE | 0,51 | 0,60 | 0,68 | 0,66 |
| produção completa | 0,51 | **0,64** | 0,74 | 0,66 |

Três leituras:
1. **Nas fichas, toda técnica piora a busca, com os dois geradores.** O relato
   cru põe a ficha certa em 1º em 81 a 83% dos casos; com o tradutor, 57 a 74%.
   A ficha está na língua do tutor, e o tradutor tira o relato dessa língua.
   Até a reescrita fiel do Gemini piora (0,83 → 0,62), porque troca a palavra
   do tutor ("coração disparado") pela técnica ("taquicardia"), e a ficha está
   escrita com a palavra do tutor.
2. **Na busca de hoje, o 1º lugar quase não muda** com o llama (0,47 → 0,50 a
   0,52). O que muda é **quantos casos passam pela porta** (0,21 → 0,54 a
   0,57): várias consultas aumentam a nota máxima e furam o corte de 0,72. É
   um efeito colateral da porta, não uma busca melhor.
3. **Com o Gemini gerando, o tradutor ajuda a busca de hoje**: na base
   acadêmica, o 1º lugar vai de 0,40 para 0,51 e o assunto certo no prompt, de
   0,17 para 0,64. Ele "traduz" o relato para a língua técnica dos artigos. **É
   o remendo para a distância entre o tutor e a base acadêmica em inglês**, e,
   com fichas em português de tutor, essa distância some e o remendo vira
   ruído.

**Pelo critério** (≥ 3 pontos no 1º lugar sem piorar a segurança):
- **na arquitetura com fichas, nenhuma técnica passa**;
- na de hoje, a reescrita do llama sozinha passa no 1º lugar (+5 pontos), mas
  é justamente a que distorce sinais em metade dos casos.

### 4. Os três consertos também perdem para o relato cru

Gerados pelo llama, 129 casos com assunto, busca nas fichas:

| Consulta | Busca de hoje: 1º | Fichas + bge-m3: 1º | Fichas + e5-base: 1º |
|---|---|---|---|
| relato cru (referência) | 0,47 | **0,81** | **0,67** |
| E1 · extração estruturada (espécie; sinais presentes e negados; exposição; tempo) | 0,42 | 0,70 | 0,60 |
| E2 · relato + 3 paráfrases só dos sinais, sem nome de doença | 0,48 | 0,71 | **0,67** |
| E3a · relato + "ficha hipotética" sem nomear o quadro | 0,45 | 0,41 | 0,41 |
| E3b · relato + "ficha hipotética" com o quadro mais provável | 0,49 | 0,45 | 0,47 |

**Defeitos dos consertos** (mesmo juiz, 134 casos cada):
- a extração estruturada zera diagnóstico, urgência e conduta: as proibições
  funcionaram ali. Mas ela ainda inventa sinal em metade das saídas. No
  primeiro caso da prova, registrou "não tem sangue" como sinal **negado**
  pelo tutor, e o relato não fala de sangue;
- as paráfrases "só dos sinais" ainda nomeiam doença em 34%: o llama
  desobedece a proibição;
- a "ficha hipotética" sem quadro nomeia em 10%; com o quadro, em 90%.

**Nenhum conserto supera o relato cru nas fichas.** O melhor, E2, empata no e5
e perde 10 pontos no bge-m3. A "ficha hipotética" é a pior. Todas as fichas
têm o mesmo esqueleto ("Ficha de triagem… Sinais que o tutor costuma
relatar…"), então a consulta escrita nesse esqueleto fica parecida com todas e
perde o que distingue um quadro do outro. **Os consertos deixam as consultas
mais limpas, mas mesmo limpas elas não buscam melhor que o relato cru.**

### 5. Na decisão: a tabela 2×2

A pergunta do João: as fichas com as técnicas desligadas funcionam melhor que
(a) os artigos com as técnicas ligadas, (b) os artigos com elas desligadas e
(c) as fichas com elas ligadas?

**O que é cada célula.**
- **Artigos:** o sistema de hoje. São os 3.481 trechos acadêmicos, com
  MiniLM, roteador, reranker e porta 0,72.
- **Fichas:** a arquitetura proposta. A busca é feita com o bge-m3 nas 61
  fichas de busca, as 3 mais próximas entram sem porta, e o atendente lê a
  ficha do mapa ([rodadas 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md) e
  [19](2026-09-24-20-fichas-em-duas-camadas.md)).
- **Tradutor ligado:** reescrita, multi-query e HyDE com os prompts de
  produção, gerados pelo llama.

**qwen3:8b.** Emergências perdidas · falsos alarmes · acerto geral:

| | Prova + régua (74 · 58) | Relatos de quem não viu o mapa (76 · 46) |
|---|---|---|
| nada | 7 · 0 · 126/134 | 21 · 9 · 92/122 |
| artigos, tradutor desligado | 7 · 0 · 126/134 | 21 · 9 · 92/122 |
| artigos, tradutor ligado | 11 · 1 · 121/134 | 19 · 5 · 98/122 |
| **fichas, tradutor desligado** | **2 · 1 · 130/134** | **5 · 7 · 109/122** |
| fichas, tradutor ligado | 6 · 1 · 126/134 | 8 · 8 · 105/122 |

**Pareados** (emergências, "só A perde × só B perde"), sempre contra **B =
fichas com o tradutor desligado**:

| A | Prova + régua | Relatos de quem não viu o mapa |
|---|---|---|
| (a) artigos, tradutor ligado | **9 × 0 (p = 0,004)** | **14 × 0 (p = 0,0001)** |
| (b) artigos, tradutor desligado | 7 × 2 (p = 0,18) | **16 × 0 (p < 0,0001)** |
| (c) fichas, tradutor ligado | 4 × 0 (p = 0,125) | 3 × 0 (p = 0,25) |

**llama3.2:3b**, só na base de artigos (as células com fichas não foram
rodadas para ele):

| | Prova + régua | Relatos de quem não viu o mapa |
|---|---|---|
| artigos, tradutor desligado | 15 · 4 · 115/134 | 40 · 22 · 60/122 |
| artigos, tradutor ligado | 8 · 3 · 121/134 | 37 · 23 · 62/122 |

Pareado desligado × ligado (emergências): **8 × 1 (p = 0,04)** na prova +
régua; 4 × 1 (p = 0,38) nos relatos independentes.

**Busca nas fichas de busca** (bge-m3), ficha certa em 1º / entre as 3:

| Consulta | Prova + régua (129) | Relatos de quem não viu o mapa (122) |
|---|---|---|
| relato cru | 107 (82,9%) / 123 (95,3%) | 74 (60,7%) / 94 (77,0%) |
| com o tradutor (llama) | 84 (65,1%) / 109 (84,5%) | 64 (52,5%) / 91 (74,6%) |

**A resposta, célula por célula:**
- **(a) Contra o sistema de hoje como ele roda** (artigos com o tradutor), as
  fichas sem tradutor ganham nos dois conjuntos, com folga e com
  significância.
- **(b) Contra os artigos sem tradutor**, a diferença é enorme e
  significativa nos relatos de quem não viu o mapa (16 × 0), e **não é
  significativa na prova + régua** (7 × 2, p = 0,18). O motivo: com a porta
  0,72, os artigos quase nunca entram no prompt (104 de 134 casos chegam sem
  trecho), e "artigos sem tradutor" dá o mesmo total que "nada". Na prova, o
  qwen sozinho já acerta muito; é nos relatos de quem não viu o mapa que a
  ficha faz a diferença.
- **(c) Contra as fichas com o tradutor**, a direção é a mesma nos dois
  conjuntos (4 × 0 e 3 × 0), sem significância com estas amostras. A busca
  explica o porquê: com o tradutor, a ficha certa em 1º cai de 107 para 84 na
  prova + régua, e de 74 para 64 nos independentes.

**O tradutor não é inútil em todo lugar.** Na base de artigos, ele ajuda o
llama a não perder emergências (15 → 8, p = 0,04). Com mais consultas, a porta
deixa passar trecho em quase todos os casos (sem trecho: de 104 para 11 em
134), e o assunto chega ao prompt. No qwen, na mesma base, o efeito é misto:
7 → 11 perdas na prova + régua, 21 → 19 nos independentes. É o mesmo retrato
da busca: **um remendo que só serve à base acadêmica**.

## O que mudou no repositório

| Arquivo | O que é |
|---|---|
| esta evidência | |
| `data/evaluation/autopsia2/resultados_por_caso.csv` (versionado na rodada 14) | as condições desta rodada: `rag_full`, `ragtrad_full`, `ctxarq_bgecl_leitura_mapa_top3`, `ctxarq_bgecl_trad_leitura_mapa_top3` e, de 23/09, `rag_query_hibrido_full`, `rag_query_ollama_full`, `rag_query_ingles_full` |
| `data/evaluation/autopsia2/tradutor/` (versionado na rodada 14) | as saídas do tradutor caso a caso (llama: 134 casos × 5 saídas; Gemini: 50 × 3; consertos: 134 × 4), o veredito do juiz em cada uma e o efeito na busca por variante |

## Observações

**1. Fiel não quer dizer útil.** A reescrita do Gemini é uma boa tradução
técnica, e mesmo assim piora a busca nas fichas. A reescrita existe para
trocar a palavra do tutor pela do especialista, e a arquitetura nova precisa
justamente da palavra do tutor.

**2. A trava do B-08 vigia a peça errada.** Ela protege a reescrita, onde a
urgência inserida é de 0% a 2%. O HyDE insere urgência em 25% a 64% das
saídas, conforme o gerador e o método de contagem, e passa sem trava.

**3. A troca silenciosa de gerador muda o sistema sem deixar rastro.** Com a
chave e a cota, o tradutor é o Gemini, fiel na reescrita. Sem elas, é o llama,
que distorce metade das reescritas, e o HyDE some. Nada disso fica registrado
na resposta nem no retrato do sistema. A implementação da autópsia passa a
gravar quem gerou cada etapa.

**4. Latência.** O tradutor soma chamadas antes da busca. Na GPU desta
máquina, com o llama, a reescrita e o multi-query levam 0,92 s de mediana
([rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md)). Com o Gemini,
são chamadas remotas a mais, que gastam cota. Desligado, esse tempo some.

**5. Uma ideia que não foi testada:** ligar o tradutor só quando a busca
estiver insegura (nota baixa na 1ª ficha). Sobra pouco para ganhar, porque o
relato cru já põe a ficha certa entre as 3 primeiras em 95% da prova + régua e
em 77% dos relatos independentes ([B-69](../backlog.md#b-69)). O que falta
nos independentes é a ficha conhecer mais jeitos de o tutor falar, e isso se
resolve **do lado da base**, uma vez só e com validação
([rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)). Do lado da pergunta,
seria a cada relato e sem ninguém conferir.

## Deixado para depois

- **O tradutor gerado pelo Gemini, nas fichas, na decisão.** Só a busca foi
  medida, no `dev` (0,83 → 0,74). A célula "fichas + tradutor do Gemini" entra
  na ablação final ([B-66](../backlog.md#b-66)).
- **Tradutor condicional à confiança da busca** ([B-69](../backlog.md#b-69)).
- **Reescrever os prompts do multi-query e do HyDE sem diagnóstico nem
  conduta.** O conserto E2 mostrou que o llama desobedece a proibição (34%).
  Com o Gemini, não foi testado. Fica para a ablação, se valer a pena depois
  dela.

## Próximo passo

A busca e o que entra no prompt estão decididos. Falta quem lê: o
[atendente](2026-09-24-19-atendente-llama-qwen-gemini.md) (rodada 18).
