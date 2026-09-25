# O que o atendente deve ler: fichas de triagem no lugar dos trechos acadêmicos

**Data:** 23 e 24/09/2026 (escrita em 25/09 a partir do registro da autópsia) ·
**Trilho:** B2, olhando o sistema inteiro · **Rodada:** 15 · **Commits:** este

> Rodada de **experimento**. Nada no sistema mudou. A pergunta é o que ajuda
> o atendente a decidir, e para respondê-la a busca sai da equação: o
> atendente recebe **exatamente** o conteúdo certo (o "oráculo") e vê-se se
> ele acerta. Tudo foi medido com o executor da autópsia; o método está na
> [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md#como-medimos-vale-para-as-rodadas-14-a-21),
> e cada caso, em `data/evaluation/autopsia2/`.

## O que foi feito

1. **A ficha de triagem do mapa.** Um programa monta, para cada uma das 61
   linhas do mapa, um texto curto com as colunas validadas (quadro, sinais
   que o tutor relata, discriminador, gêmea, motivo). No fim vai uma linha de
   conduta **fixa pela urgência** do mapa, que não é escrita por nenhum
   modelo. É a "ficha do mapa".
2. **O teste do oráculo** (23/09). Nos casos da prova e da régua, o atendente
   recebe, no lugar do que a busca traria:
   - os trechos acadêmicos do assunto certo;
   - os mesmos trechos traduzidos para o português;
   - os textos para tutor reais que existem (PDSA, Cornell, CRMV-SP);
   - a ficha do mapa do assunto certo;
   - só a ficha da gêmea, de propósito errada.
   
   Primeiro com o llama; depois, com qwen e Gemini, na prova + régua.
3. **O que a ficha acrescenta além da resposta** (24/09). A ficha certa,
   **sem** a linha de conduta: sobra só o conteúdo (sinais, discriminador,
   motivo).
4. **Português × inglês** (24/09). O mesmo conteúdo em português e em inglês,
   na busca e na decisão.
5. **A etapa 2** (24/09). O que falta nela, se os documentos dão conta, e o
   que acontece quando a busca traz a ficha errada.

## Por quê

A [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md) mostrou que o
RAG não ajuda e que o trecho que chega ao prompt é do assunto certo, mas não
diz quando procurar o veterinário. Há dois culpados possíveis:
- **a busca**, que traz o trecho errado ou nenhum;
- **o conteúdo**, que nem o trecho certo ajuda.

Consertar o culpado errado custa semanas. O oráculo separa os dois: se o
atendente não acerta nem com o conteúdo certo na mão, a busca não é o
problema.

E a base é acadêmica por uma razão concreta, registrada nas evidências do
trilho A de 14 a 20/09. As fontes escritas para tutor (PDSA, Cornell, VCA,
CRMV-SP) foram deixadas fora da ingestão porque não tinham licença clara para
redistribuir o texto num repositório público. Os artigos de acesso aberto
entraram no lugar delas, mas eles descrevem pesquisa, não o que o tutor vê em
casa. O João decidiu tornar o repositório privado quando o orientador
liberar ([B-52](../backlog.md#b-52)), o que permite voltar a usar essas
fontes. E uma ficha escrita a partir delas não redistribui o texto de
ninguém: cita a fonte.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | A ficha é **montada por código**, só com as colunas do mapa | O mapa é o conteúdo que o time já fundamentou e mandou validar ([rodada 11](2026-09-12-12-mapa-de-assuntos.md)); nenhuma frase clínica nova entra sem origem |
| 2 | **A linha de conduta sai fixa da urgência** do mapa, com três textos, um por nível | A urgência é decisão clínica do mapa. A ficha não pode deixar um modelo escrevê-la |
| 3 | **Testar com a busca perfeita antes de mexer na busca** | Separa o problema do conteúdo do problema da busca |
| 4 | "Por que importa" usa a coluna `motivo`, sem as frases de bastidor do projeto | Nenhuma coluna do mapa foi feita para o atendente ler. O `motivo` é a mais próxima. O filtro deixou passar notas internas em 11 fichas (observação 1) |
| 5 | Medir a ficha **sem a linha de conduta** | Se tudo viesse de "a resposta está escrita na ficha", o resultado seria trivial. O teste separa o conteúdo da resposta |
| 6 | Na etapa 2, a ficha fica **como o mapa está** (magra) | É o conteúdo validado que existe. Enriquecer é trabalho de especialista, e a [rodada 19](2026-09-24-20-fichas-em-duas-camadas.md) testa um rascunho |

O molde da ficha do mapa, sem acentos como as colunas do mapa:

```
Ficha de triagem: <quadro> (<especie>).
Sinais que o tutor costuma relatar: <sinais_que_o_tutor_relata>.
Como diferenciar: <discriminador>.
Pode ser confundido com: <quadro da gemea>.
Por que importa: <motivo, sem as frases de bastidor>.
Conduta: <fixa pela urgencia>
```

As três condutas:
- **imediato:** "Isto é uma emergência: procure um veterinário agora, sem
  esperar."
- **até 24 h:** "Não é emergência imediata, mas precisa de consulta nas
  próximas 24 horas; vá antes se piorar."
- **rotina:** "Não é emergência: pode aguardar uma consulta de rotina,
  observando se surgem sinais de alarme."

Duas fichas reais: uma da etapa 1, com as colunas preenchidas, e uma da
etapa 2, sem sinais nem discriminador:

> **Obstrução uretral (etapa 1, 99 palavras).** Ficha de triagem: Obstrucao
> uretral (cao e gato). Sinais que o tutor costuma relatar: vai na caixa e nao
> sai nada, faz forca, sai so gotinhas, chora quando tenta, lambe muito a
> regiao, barriga dura e dolorida. Como diferenciar: Sai urina? Fazer forca
> repetidamente sem sair nada e emergencia; se sai um pouco, e outro quadro.
> Pode ser confundido com: Xixi fora do lugar e cistite. Por que importa:
> urologico e a causa numero 1 em gatos no PS; morte possivel em menos de 24 a
> 48 horas. Conduta: Isto e uma emergencia: procure um veterinario agora, sem
> esperar.

> **Insuficiência cardíaca descompensada (etapa 2, 45 palavras).** Ficha de
> triagem: Insuficiencia cardiaca descompensada (cao e gato). Pode ser
> confundido com: Tosse dos canis leve. Por que importa: Tosse noturna com
> esforco respiratorio em cao com sopro conhecido; edema pulmonar e
> emergencia. Conduta: Isto e uma emergencia: procure um veterinario agora,
> sem esperar.

A mediana é de 73 palavras (de 37 a 123).

## Resultado esperado

**O teste do oráculo, de 23/09, não teve previsão escrita antes.** Ele nasceu
de uma pergunta do João naquela noite: "o que está mais errado: a base ou o
RAG?". Os testes de 24/09 tiveram critério escrito antes (plano da madrugada,
00h56, e caderno da frente J, 03h20):

| Teste | Escrito antes |
|---|---|
| Ficha sem a linha de conduta (03h20) | "Se o atendente continuar acertando, é o conteúdo (sinais, discriminador) que ajuda; se desabar, o ganho das fichas vem de a conduta estar escrita nelas — o que é legítimo num sistema de protocolos, mas muda a leitura dos números" |
| Português × inglês (00h56) | "Português se for igual ou melhor", na busca e na decisão |
| Etapa 2 (00h56) | Classificar cada documento da etapa 2 em suficiente (≥ 3 sinais leigos e ≥ 1 critério de gravidade com apoio no texto), parcial ou insuficiente |

## Resultado obtido

### 1. Com a busca perfeita, o trecho acadêmico não ajuda; a ficha resolve

**llama3.2:3b, 23/09.** Emergências perdidas · falsos alarmes · acertos.
São 63 casos da prova e não 68: nas linhas de "assunto certo", os 5 casos
fora do mapa ou INCERTO não têm assunto para receber.

| O que o atendente recebe | Prova, `dev` + calibração | Régua (66) |
|---|---|---|
| nada | 8/34 · 2/32 · 58/68 | 6/40 · 0/26 · 60/66 |
| o que a busca de hoje traz | 8/34 · 4/32 · 56/68 | 7/40 · 0/26 · 59/66 |
| **trechos acadêmicos do assunto certo** | 7/34 · 6/29 · 50/63 | 9/40 · 0/26 · 57/66 |
| os mesmos trechos, traduzidos para o português | 3/34 · 6/29 · 54/63 | 5/40 · 2/26 · 59/66 |
| **a ficha do mapa do assunto certo** | **0/34 · 1/29 · 62/63** | **0/40 · 1/26 · 65/66** |
| só a ficha da gêmea (assunto errado de propósito) | 3/28 · 4/17 · 38/45 | 2/32 · 2/14 · 42/46 |

**Prova + régua, os três atendentes** (74 emergências · 58 leves):

| | llama3.2:3b | qwen3:8b | gemini-3.5-flash-lite |
|---|---|---|---|
| nada | 14 · 2 · 118/134 | 7 · 0 · 126/134 | 0 · 3 · 130/134 |
| trechos acadêmicos do assunto certo | **16** · 6 · 107/129 | **10** · 1 · 118/129 | (não coube na cota) |
| ficha do mapa do assunto certo | **0** · 2 · 127/129 | **0** · 0 · 129/129 | **0** · 1 · 128/129 |

Pareados (emergências, "só A perde × só B perde"):
- **nada × trechos acadêmicos certos:** llama 6 × 8 (p = 0,79); qwen 3 × 6
  (p = 0,51). O trecho acadêmico certo não melhora e tende a piorar.
- **nada × ficha certa:** llama **14 × 0 (p = 0,0001)**; qwen **7 × 0
  (p = 0,016)**.

**Por que o texto acadêmico não ajuda: ele empurra para os dois lados.**
- **Ajudou** quando o trecho dizia que o quadro é fatal: torção gástrica (p27,
  p07), permetrina (p37), corpo estranho (p38), obstrução em cão (b15),
  cebola (p20).
- **Atrapalhou** quando era texto de pesquisa:
  - trauma com sangramento (p23, b06) virou "sangramento leve";
  - filhote gelado (p28, b14) virou "sinais leves";
  - também erraram colapso com gengiva branca (b42), carrapato com anemia
    (b46) e hipoglicemia (p42, com saída inválida convertida em INCERTO; é
    uma das duas falhas técnicas da autópsia).
- **Criou falsos alarmes:** artrose (p49, p13), conjuntivite leve (p52),
  exposição à raiva (p63), cistite (p09, "FLUTD").

Traduzir o trecho para o português reduz as perdas na prova (7 → 3), mas
mantém os falsos alarmes. A língua pesa, mas não é o principal: o problema é
**o registro** (pesquisa, não orientação). Os textos para tutor reais só
existem para 2 quadros (8 casos). Neles, texto acadêmico, texto para tutor e
ficha acertaram igual, e o resultado é inconclusivo.

**A ficha da gêmea não derruba o modelo** (3 perdas na prova, 2 na régua),
porque ela traz "Como diferenciar" e "Pode ser confundido com": o
discriminador ajuda até quando a ficha é do assunto errado.

### 2. A ficha não é só "a resposta escrita"

Ficha **certa**, com e sem a linha de conduta:

| | qwen, prova + régua | qwen, relatos de quem não viu o mapa | llama, prova + régua | llama, relatos de quem não viu o mapa |
|---|---|---|---|---|
| nada | 7/74 · 0/58 | 21/76 · 9/46 | 14/74 · 2/58 | 40/76 · 22/46 |
| ficha certa **sem** a linha de conduta | **0/74 · 8/55** | **4/76 · 8/46** | 2/74 · 6/55 | 33/76 · 24/46 |
| ficha certa com a conduta | 0/74 · 0/55 | 0/76 · 4/46 | 0/74 · 2/55 | 25/76 · 22/46 |

- **O conteúdo, sozinho, faz a maior parte do serviço.** Sem a linha de
  conduta, o qwen passa de 21 para 4 emergências perdidas nos relatos de quem
  não viu o mapa (pareado **17 × 0, p < 0,0001**). Os sinais e o
  discriminador validados ensinam o atendente a reconhecer o quadro.
- **A linha de conduta faz duas coisas:** fecha as últimas perdas (4 → 0) e,
  principalmente, **segura os falsos alarmes** (8 → 0 na prova + régua; 8 → 4
  nos independentes).
- **No llama, o conteúdo ajuda pouco** (40 → 33 → 25). Ele continua decidindo
  pelo tom do tutor, até com a ficha certa na mão
  ([rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md)).

Pelo critério escrito às 03h20: **é o conteúdo que ajuda**, e a conduta
completa o serviço. O ganho das fichas não é trivial.

Isso também diz como ler qualquer número com fichas, nesta e nas próximas
rodadas. **Quando a busca acerta a ficha, o atendente recebe o protocolo do
quadro**, com a conduta do mapa, e "com a ficha certa" dá perto de 100% para
qwen e Gemini. O desempenho real depende de três coisas:
- com que frequência a busca acerta, com relatos de gente que não viu o mapa
  ([rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md));
- o que o atendente faz quando a ficha é errada ou não vem (resultado 4);
- se o atendente resiste ao tom do tutor ([rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md)).

### 3. Português, e não inglês

Mesmo conteúdo (a ficha escrita por IA em 24/09, gerada nas duas línguas na
mesma chamada; ver a [rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)).

**Busca, só vetor, relato cru.** Ficha certa em 1º lugar, lotes `dev` /
calibração / régua:

| Embedding | Ficha em português | A mesma ficha em inglês |
|---|---|---|
| multilingual-e5-base | 0,57 / 0,69 / 0,68 | 0,32 / 0,44 / 0,48 |
| bge-m3 | 0,81 / 0,62 / 0,82 | 0,64 / 0,56 / 0,62 |

**Decisão**, com a ficha mais próxima pelo e5 (prova + régua). Emergências
perdidas · falsos alarmes:

| | llama3.2:3b | qwen3:8b |
|---|---|---|
| ficha em português | 2 · 1 | 6 · 1 |
| ficha em inglês | 4 · 1 | 10 · 1 |

Na busca, o inglês perde de 6 a 25 pontos no 1º lugar, conforme o embedding e
o lote. Na decisão, o qwen com a ficha em inglês perde 10 emergências em vez
de 6 (pareado 7 × 3, p = 0,34; llama 4 × 2, p = 0,69). **Pelo critério ("português
se for igual ou melhor"), português.** O tutor escreve em português, e a
ficha precisa estar na língua dele.

### 4. A etapa 2: o mapa está vazio, e a ficha errada custa caro

**O que falta, medido.** As 31 linhas da etapa 1 têm sinais e discriminador
no mapa. As 30 da etapa 2 não têm nenhum dos dois (0 de 30). Elas têm fonte
(`cobertura = fonte_aprovada`), mas a ficha delas sai magra: título, gêmea,
motivo e conduta.

**Os documentos da etapa 2 dão conta?** Uma IA (a do autor barato da
[rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)) tentou extrair, do texto
indexado de cada assunto, sinais que o tutor vê e sinais de alarme, cada um
com um trecho literal do documento que o sustenta. Pelo critério escrito
antes:

| Situação | Assuntos |
|---|---|
| **Suficiente (7)** | queimadura e choque elétrico; eclâmpsia; uva, passa e xilitol; leptospirose; doença do carrapato com anemia; sapo; síndrome vestibular |
| **Parcial (15)** | engasgo; cetoacidose; cinomose; distocia; tromboembolismo felino; corpo estranho; queda de altura; hipoglicemia do filhote; picada de inseto; tosse dos canis; lírio; otite externa; tártaro; cobra, escorpião e aranha; carrapatos sem sinais |
| **Insuficiente (8)** | ferida de briga de gato; **insuficiência cardíaca descompensada**; ofegação após exercício; ferida pequena; parto normal; bebe e urina mais; mordida de morcego; caroço de crescimento lento |

- **Nenhum documento deu apoio para "como diferenciar da gêmea".** Isso não é
  defeito do documento: diferenciar dois quadros é o papel do discriminador
  do mapa, que só os especialistas preenchem.
- **Os insuficientes são quase todos quadros leves** cujo documento é um
  artigo sobre outra coisa:
  - "parto normal" é um estudo de dinâmica uterina e monitoração fetal
    eletrônica, com 235 trechos;
  - "caroço" é um consenso sobre mastocitoma;
  - "ofegação" é um estudo de água enriquecida em cães de trabalho.
  
  A exceção grave é a **insuficiência cardíaca**. O documento dela ("Coughing
  in Small Animal Patients") só tem localização da tosse no exame, imagem de
  tórax, lavado broncoalveolar e tratamento. Nada do que o tutor vê. Conferi
  lendo o texto indexado dos dois primeiros casos.

**O que acontece quando a busca traz a ficha errada.** Com a ficha mais
próxima pelo e5 (uma busca que ainda erra bastante na etapa 2), nos casos da
prova + régua:

| | llama | qwen | Gemini |
|---|---|---|---|
| etapa 2 (27 emergências · 25 leves), nada | 3 · 1 | 1 · 0 | 0 · 3 |
| etapa 2, ficha do mapa certa (mesmo magra) | 0 · 0 | 0 · 0 | 0 · 1 |
| **etapa 2, ficha mais próxima pelo e5** | 0 · 1 | **6** · 0 | **6** · 0 |
| etapa 1 (47 · 30), ficha mais próxima pelo e5 | 0 · 4 | 0 · 0 | 0 · 0 |

**Todas as perdas do qwen e do Gemini com a ficha e5 estão na etapa 2, e todas
vieram de ficha errada.** As 6 do Gemini:

| Caso | Quadro | Ficha que a busca trouxe | Resposta |
|---|---|---|---|
| p33 | insuficiência cardíaca | torção gástrica | INCERTO |
| p38 | corpo estranho | lírio | INCERTO |
| p40 | distocia | obstrução uretral | INCERTO |
| p41 | cinomose neurológica | hipoglicemia do filhote | INCERTO |
| p14 | cobra | golpe de calor | INCERTO |
| b48 | síndrome vestibular | emergência ocular | INCERTO |

O Gemini justificou com frases como "o relato trata de dificuldade no parto,
assunto não abordado no trecho de protocolo fornecido". O prompt
`v1_grounded` manda decidir pelas fontes, e um modelo obediente, diante de
uma fonte errada, diz "não sei". O llama, que tende a dizer "emergência", não
cai nessa armadilha.

Três leituras:
1. **Com a ficha certa, até a ficha magra da etapa 2 resolve** (0 perdas nos
   três). O problema não é a ficha; é **a ficha errada**.
2. **Na etapa 2, o que falta não é texto bonito: é a busca acertar a ficha**,
   e ela erra mais ali justamente porque a ficha é magra (não tem as palavras
   com que o tutor conta). A [rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md)
   ataca a busca; a [rodada 19](2026-09-24-20-fichas-em-duas-camadas.md), as
   palavras.
3. **Sem contexto, na etapa 2, qwen e Gemini erram menos do que com ficha
   errada** (1 e 0 perdas contra 6 e 6). Um atendente bom, sozinho, é melhor
   que o mesmo atendente com a ficha errada. É o risco que a porta de entrada
   e o número de fichas precisam equilibrar.

## O que mudou no repositório

| Arquivo | O que é |
|---|---|
| esta evidência | |
| `data/evaluation/autopsia2/resultados_por_caso.csv` (versionado na rodada 14) | as condições desta rodada: `sem_rag`, `rag_full`, `oraculo_academico`, `oraculo_academico_pt`, `oraculo_tutor`, `oraculo_ficha`, `ficha_gemea`, `ctxarq_oraculo_fichassc` (ficha sem conduta), `e5_fichasia_top1`, `e5_fichasiaen_top1`, `e5_fichas_top1` |

O gerador das fichas do mapa não entra aqui. Ele entra com a implementação
(rodadas 23 a 30), junto com o arquivo de fichas que o backend lê.

## Observações

**1. Onze fichas do mapa mostram ao atendente notas internas de curadoria.**
O "Por que importa" sai da coluna `motivo`, escrita para o time e não para o
atendente. O filtro de bastidor tirou as frases óbvias, mas sobraram coisas
como "Caso b14", "não encontrei artigo primário, só um TCC" e "a exposição
pede reforço vacinal", em 11 das 61 fichas. Todos os números desta autópsia
foram medidos com esse texto, e a implementação o reproduz igual, para os
números valerem. Limpar é trabalho dos especialistas, e cada mudança de texto
de ficha passa a ser rodada medida ([B-61](../backlog.md#b-61)).

**2. Um prompt que manda "ignorar o trecho de outro assunto e decidir pelo
relato" não mudou nada no llama nem no qwen.** Com a ficha e5, o llama ficou
com 0 perdas antes e depois; o qwen, com 6 antes e 6 depois. No Gemini, que
é quem cai na armadilha, não coube na cota. A saída que funcionou foi outra:
dar ao atendente **mais de uma ficha** ([rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md)).

**3. Os dois erros que sobram com a ficha perfeita, no llama, são falsos
alarmes em casos leves:** cistite com sangue (p09) e conjuntivite (b11). É o
lado seguro do erro.

**4. Fichas e prova saem do mesmo mapa.** Quem escreveu os relatos da prova e
da régua tinha os sinais do mapa na mão, e a ficha é feita desses mesmos
sinais. Os números da prova com fichas são **otimistas**. A medida honesta
são os relatos de quem não viu o mapa, e a definitiva será a prova 2
([rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md)).

**5. O que a ficha é, para o artigo.** A ficha funciona como o protocolo de
triagem de um pronto-socorro, por quadro:
- que sinais indicam o quadro;
- como diferenciá-lo do parecido;
- qual a conduta.

É o que os protocolos de triagem veterinária (VTL, Manchester) fazem, e o que
a base acadêmica não faz.

## Deixado para depois

- **Validação clínica das fichas de leitura** ([B-61](../backlog.md#b-61)): as
  60 células vazias da etapa 2 (sinais e discriminador), as 11 notas internas
  do "Por que importa" e os conflitos entre mapa e documento que as rodadas
  seguintes acharam.
- **Uma fonte para tutor nos 8 quadros insuficientes**
  ([B-62](../backlog.md#b-62)): páginas de orientação de hospitais-escola ou
  manuais veterinários na versão para tutores. A ficha cita a fonte, e não é
  preciso indexar o texto inteiro.

## Próximo passo

Com o conteúdo resolvido para o caso em que a busca acerta, a pergunta passa a
ser a busca: com que frequência a ficha certa chega, e como fazer ela chegar
nos relatos de quem não viu o mapa. É a
[rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md).
