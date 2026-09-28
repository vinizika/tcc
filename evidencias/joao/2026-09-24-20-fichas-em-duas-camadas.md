# Fichas escritas por IA, em duas camadas: uma para a busca, outra para o atendente ler

**Data:** 24/09/2026 (madrugada e noite; escrita em 25/09 a partir do registro
da autópsia) · **Trilho:** B2 · **Rodada:** 19 · **Commits:** este

> Rodada de **construção e experimento**. O produto é um artefato, as 61
> fichas de busca, que entram no repositório nesta rodada como rascunho, com
> a origem de cada frase, para os especialistas certificarem. Os testes dizem
> como usá-lo. Nada no sistema mudou. O método está na
> [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md#como-medimos-vale-para-as-rodadas-14-a-21).

## O que foi feito

A pergunta do João: dá para uma IA escrever as fichas a partir da base
validada e do mapa, para os especialistas só certificarem? O ganho compensa?
Foram duas tentativas no mesmo dia, e uma descoberta no meio da segunda.

1. **Madrugada, o autor "barato".** O `gemini-3.1-flash-lite` foi o que coube
   na cota gratuita; o modelo mais forte da conta (`gemini-3.8-flash`) teve 0
   respostas em 21 tentativas. Ele escreveu as 61 fichas a partir do texto
   indexado de cada assunto e da linha do mapa, com um trecho literal do
   documento para cada item. A conferência foi automática (o trecho existe?)
   e por um juiz de outra família (o trecho sustenta o item?). Depois veio a
   busca e a decisão.
2. **Noite, o Claude.** O pedido do João foi usar um modelo mais forte, ler os
   documentos inteiros e desenhar a ficha pensando no desempenho do RAG. Seis
   instâncias escreveram as 61 fichas, a partir do texto completo de cada
   documento e da linha do mapa. Cada frase marca a origem: `mapa`,
   `documento` (com o trecho e o arquivo) ou `geral` (conhecimento
   veterinário geral, para o especialista validar).
3. **A descoberta:** a ficha do Claude **busca** melhor, mas o qwen, **lendo**
   essa ficha, erra mais. Diagnóstico, duas correções com critério escrito
   antes, e o desenho que fica: **a busca procura na ficha escrita pela IA; o
   atendente lê a ficha do mapa**.
4. **A folha de certificação** dos especialistas: os itens que não vêm do
   mapa, os conflitos entre o mapa e o documento, e os rascunhos da etapa 2.

## Por quê

A [rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md) mostrou que a
ficha do mapa resolve quando chega. A [rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md)
mostrou que ela chega entre as 3 primeiras em só 76% dos relatos de quem não
viu o mapa, e em 1º lugar em 52%. **Na etapa 2 o mapa está vazio**: a ficha
não tem as palavras com que o tutor conta, e a busca erra mais ali. Preencher
as 60 células que faltam é trabalho de especialista. A pergunta é se a IA pode
fazer o rascunho, e se o rascunho já ajuda.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **A conduta nunca é escrita pela IA**: sai fixa da urgência do mapa | Urgência é decisão clínica do mapa |
| 2 | **Todo item traz a origem**; item de documento sem trecho literal que exista no texto **fica de fora** (e é contado) | É a condição para o especialista certificar em horas, não escrever do zero |
| 3 | **Proibido:** remédio, dose, tratamento, cuidado caseiro, decidir a urgência, sinal de outra espécie, achado de exame como sinal do tutor. O autor **não vê** nenhum caso de teste | A ficha não pode virar prescrição, nem aprender a prova |
| 4 | Autor barato: **"mapa sempre"** (o conteúdo validado do mapa entra inteiro; a IA só acrescenta) | Na primeira montagem, um sinal do mapa rotulado como "documento", sem trecho, foi descartado (permetrina: "tremendo muito"). O validado não pode sumir |
| 5 | Fichas do Claude, **diagramação v3**, desenhada para a busca: primeiro "como o tutor costuma contar", com 6 a 12 frases coloquiais e variações, depois os sinais de alarme, a diferença para a gêmea, o porquê e a conduta; alvo de 150 a 250 palavras | A busca compara o relato com o texto inteiro da ficha, e o que mais casa com o relato são as palavras do tutor. Texto demais dilui a parecença |
| 6 | **Conhecimento geral permitido, mas marcado** (`geral`) | O documento acadêmico muitas vezes não descreve o que o tutor vê. Melhor uma frase marcada para validar do que uma lacuna |
| 7 | Quatro variantes da base de busca, **definidas às 19h14, antes de qualquer teste**: a ficha do Claude; a mesma sem os itens `geral`; a mesma sem acentos; a híbrida (ficha do mapa na etapa 1, do Claude na etapa 2) | A ficha-IA da madrugada perdeu na etapa 1 mesmo mantendo as frases do mapa: acrescentar dilui |
| 8 | **Não trocar pela ficha do Claude, contra o meu próprio critério** (resultado 4) | O critério não tinha trava para a decisão do atendente, e ela piorou |
| 9 | **Separar o texto que a busca procura do texto que o atendente lê** | Resolve o problema sem perder o ganho da busca (resultado 5) |

## Resultado esperado

Três critérios, escritos antes de cada etapa:

| Etapa | Escrito antes |
|---|---|
| Autor barato (00h56) | Vale a pena se: **(a)** a ficha-IA não piorar a etapa 1 e melhorar a etapa 2 em recuperação (≥ 10 pontos no 1º lugar) ou em classificação; **(b)** ≥ 90% dos itens tiverem trecho verificável no documento e nenhum erro perigoso na leitura manual (urgência ou espécie errada); **(c)** a revisão do especialista couber em poucas horas. Não vale se não superar a ficha do mapa, ou se a fidelidade ficar abaixo de 80% |
| Fichas do Claude (18h55) | Trocar a ficha do mapa pela do Claude se, nos relatos de quem não viu o mapa, **(a)** o 1º lugar da busca subir ≥ 5 pontos, **ou (b)** as emergências perdidas do qwen com 3 fichas caírem ≥ 1/3 (de 7 de 76 para ≤ 4), **sem** piorar a prova + régua em mais de 3 pontos de busca ou 2 falsos alarmes; e se ≥ 95% dos trechos citados existirem no documento, sem erro perigoso na leitura manual |
| As duas correções (20h40) | Uma leitura só é adotada se, nos relatos de quem não viu o mapa, **não perder mais emergências que a ficha do mapa (≤ 7 de 76)**, não piorar o piloto da prova 2 e não passar de 3 falsos alarmes na prova + régua. Entre as que passarem, a de menos emergências perdidas; em caso de empate, a leitura A (que não exige texto novo para validar) |

## Resultado obtido

### 1. O autor barato (madrugada): fiel, barato, e só ajuda onde o mapa é vazio

**Fidelidade.** 465 itens propostos: 296 vindos do mapa e 169 do documento.

| Medida | Resultado |
|---|---|
| Itens do documento com o trecho **achado no texto** | 152 literais + 3 aproximados = **155 de 169 (91,7%)** |
| Descartados | 7 com um trecho que não existe no documento; 7 sem trecho |
| Juiz (`gemma-4-31b-it`, outra família), 89 dos 119 itens novos | **81 (91%) sustentados** pelo trecho; 5 (6%) em parte; **3 (3%) não**; 2 são achados de exame que o tutor não vê em casa; 0 de espécie errada |
| Leitura minha de 12 fichas críticas | **Nenhum erro perigoso** (nenhuma ficha rebaixa uma emergência; a conduta é fixa) |
| Custo | 12 chamadas, ~16 minutos, conta gratuita |

**Os 3 itens que o juiz reprovou mostram por que a certificação humana é
necessária**, e não só a conferência automática:
- corpo estranho: "vômitos frequentes" e "vômitos persistentes", apoiados no
  trecho "Main surgical findings were classified as foreign body". O trecho
  **existe** no documento e passou na conferência automática, mas não diz
  nada sobre vômito;
- tremor sem convulsão: "perda de consciência" como sinal de alarme, apoiado
  em "…there is **no** loss of consciousness during the episode". A IA
  inverteu o sentido do trecho.

**Busca** (bge-m3, ficha certa em 1º lugar), somando `dev`, régua e os dois
autores independentes:

| | Etapa 1 (126 relatos) | Etapa 2 (109 relatos) |
|---|---|---|
| ficha do mapa | **0,79** | 0,50 |
| ficha-IA ("mapa sempre") | 0,73 (**−6**) | **0,61 (+11)** |

**Decisão** (prova + régua): a ficha-IA **empata** com a do mapa.
- A mais próxima pelo e5: qwen 6 · 1 contra 6 · 0; llama 2 · 1 contra 0 · 6.
- A certa: qwen 1 · 1 contra 0 · 0.
- Com as 3 fichas, a base híbrida (ficha-IA na etapa 2) contra a do mapa:
  qwen 4 · 2 contra 3 · 1 na prova + régua, e 9 · 7 contra 7 · 7 nos
  independentes. Diferenças de 1 a 2 casos, dentro do ruído.

**Pelo critério:**
- **(b) e (c) passam:** 91,7% de trecho verificável, e o especialista
  certificaria ~120 itens, cerca de 1.200 palavras.
- **(a) passa só na etapa 2 e só na busca:** +11 pontos. Na etapa 1, a IA
  mexendo na ficha tira 6 pontos, mesmo mantendo as frases do mapa: o que ela
  acrescenta, mais técnico, dilui o que casava com o relato.

**A lição para a noite:** o que se acrescenta tem de estar **na língua do
tutor**, para ajudar a busca e não só informar.

### 2. As fichas do Claude (noite): geração e fidelidade

Seis instâncias, ~20 minutos, 61 de 61 fichas. A diagramação:

```
Ficha de triagem: <quadro> (<nome leigo>) — <espécie>.
Como o tutor costuma contar: <6 a 12 frases curtas, coloquiais, com variações>.
Sinais de alarme: <o que indica gravidade>.
Como diferenciar de <quadro gêmeo>: <o que o tutor consegue ver de diferente>.
Por que importa: <uma frase>.
Conduta: <fixa pela urgência do mapa; nunca escrita pela IA>
```

A ficha de busca da eclâmpsia, por inteiro. Na etapa 2 o mapa só tinha o
título, a gêmea e o motivo:

> Ficha de triagem: Eclâmpsia puerperal (febre do leite) — cão. Como o tutor
> costuma contar: Minha cadela tá amamentando e começou a tremer; Tá com o
> corpo duro, as patas esticadas; Tá agitada, inquieta, não para quieta; Fica
> batendo os dentes, mexendo a boca; Tá ofegante demais; Anda cambaleando, sem
> coordenação; Ela teve filhotes há poucas semanas; Ainda tá prenha, no fim da
> gestação, e começou a tremer; É pequena, novinha e teve muitos filhotes;
> Come comida caseira com muita carne; Os filhotes tão bem, só a mãe tá mal.
> Sinais de alarme: Teve convulsão; Caiu de lado e não consegue levantar;
> Respirando com dificuldade; O corpo todo trava, rígido. Como diferenciar de
> tremor sem convulsão: O tremor de frio ou de medo vem em animal atento que
> anda normal; na eclâmpsia é a cadela que está amamentando que treme e fica
> rígida. Por que importa: É uma queda de cálcio no sangue da cadela que
> amamenta, grave e que pode matar. Conduta: Isto é uma emergência: procure
> um veterinário agora, sem esperar.

Cada frase tem origem. Por exemplo, "fica batendo os dentes, mexendo a boca"
vem do documento: "muscular tremors (100%), and jaw chattering (100%)",
`eclampsia__ijvsah_2025_management.pdf`.

| Medida | Resultado |
|---|---|
| Itens | **956**: 442 do mapa, 461 do documento, 53 `geral` |
| Trechos do documento achados | **460 de 461 (99,8%)**: 457 literais, 3 aproximados; 1 item sem trecho ficou de fora. **124 só existem no texto completo**, não no indexado |
| Itens `geral` | 5 na etapa 1 (31 fichas) e **48 na etapa 2** (30 fichas) |
| Palavras por ficha | mínimo 150, mediana 193, máximo 302 (3 acima de 250: as que têm 4 gêmeas) |
| Sinais do mapa cobertos | todos, menos 2, que o montador inseriu como estão no mapa ("babando", "sem esforço") |
| Leitura minha de 12 fichas críticas | **nenhum erro perigoso**. Defeitos menores: um sinal do mapa repetido pela inserção automática e um título com parênteses duplos, corrigido no montador |

**Os autores acharam conflitos entre o mapa e o documento**, que ficam para os
especialistas:
- **convulsão:** 2 minutos no mapa × 5 minutos no documento;
- **piometra:** 1 mês × 2 a 4 meses depois do cio;
- **conjuntivite:** o documento dá como leves sinais que o mapa trata como de
  emergência;
- **cistite:** fazer força e lamber, que o mapa põe na obstrução;
- **obstrução uretral:** o discriminador diz "se sai um pouco, é outro
  quadro", mas os sinais incluem "sai só gotinhas".

### 3. Na busca, a ficha do Claude ganha, e o ganho está na etapa 2

bge-m3, ficha certa em 1º lugar e entre as 3 (em %), somando os relatos
independentes 1 + 2 (122) e a prova + régua (129):

| Base de busca | Indep., 1º | Indep., top 3 | Prova + régua, 1º | Prova + régua, top 3 | Indep. etapa 1 / 2 (1º) | Prova + régua etapa 1 / 2 (1º) |
|---|---|---|---|---|---|---|
| ficha do mapa | 51,6 | 76,2 | 80,6 | 93,0 | 62,9 / 40,0 | 93,5 / 61,5 |
| ficha-IA barata ("mapa sempre") | 54,1 | 74,6 | 80,6 | 93,0 | — | — |
| **ficha do Claude** | **60,7** | 77,0 | 82,9 | 95,3 | 59,7 / **61,7** | 79,2 / **88,5** |
| ficha do Claude sem `geral` | 59,8 | 77,9 | 82,9 | 95,3 | — | — |
| híbrida (mapa na etapa 1, Claude na 2) | 55,7 | **78,7** | **87,6** | **97,7** | — | — |
| ficha do Claude sem acentos | 63,9 | 77,0 | 81,4 | 95,3 | — | — |

- **Pelo critério (a), a troca vale:** nos relatos independentes, o 1º lugar
  sobe de 51,6 para 60,7 (+9 pontos). A prova + régua não piora (80,6 → 82,9).
- **O ganho está na etapa 2**: de 40 para 62 nos independentes, e de 62 para
  89 na prova + régua. Onde o mapa é vazio, a ficha do Claude dá à busca as
  palavras do tutor.
- **Na etapa 1, a ficha do mapa ainda ganha na prova** (93,5 × 79,2), que foi
  escrita com o vocabulário do mapa. Nos independentes, a diferença é pequena
  (62,9 × 59,7).
- **Os itens `geral` quase não pesam na busca** (60,7 × 59,8).
- Tirar os acentos dá +3 nos independentes e −1,5 na prova: ruído.

A regra das 19h14 dizia "a melhor na busca nos independentes", sem dizer se
pelo 1º lugar ou pelos 3 primeiros, e os dois discordam: a ficha do Claude no
1º lugar, a híbrida no top 3, por 2 casos. Para não escolher depois de ver a
decisão, **rodei as duas** com o qwen.

### 4. Na decisão, a ficha do Claude **piora** o qwen

qwen3:8b, 3 fichas (bge-m3). Emergências perdidas · falsos alarmes:

| O que a busca procura → o que o qwen lê | Prova + régua (74 · 58) | Independentes 1 + 2 (76 · 46) | etapa 1 / 2 (indep.) | Tom (74) |
|---|---|---|---|---|
| ficha do mapa → ficha do mapa | 3 · 1 | **7 · 7** | 1 / 6 | **4** |
| ficha do Claude → ficha do Claude | 3 · 1 | **13 · 6** | 6 / 7 | **8** |
| híbrida → híbrida | 3 · 1 | 9 · 7 | 3 / 6 | 8 |

Pareado ficha do mapa × ficha do Claude, emergências nos independentes:
**2 × 8 (p = 0,11)**; no tom, 1 × 5 (p = 0,22). A diferença não é
significativa, mas vai na direção errada, e emergência perdida é a métrica que
manda.

**O critério escrito às 18h55 diria "troque":** o 1º lugar subiu 9 pontos, a
prova não piorou, 99,8% dos trechos conferem e não houve erro perigoso.
**Não troquei.** O critério não tinha trava para a decisão do atendente nos
relatos de quem não viu o mapa, e ela piorou. **Fica registrado como falha do
meu critério.**

**A prova de que o problema é o texto, e não a busca.** Com **só a ficha
certa** no prompt (oráculo), o qwen perde:

| Ficha certa no prompt | Prova + régua (74 · 55) | Independentes 1 + 2 (76 · 46) |
|---|---|---|
| a do mapa | **0** · 0 | **0** · 4 |
| a do Claude | 3 · 1 | **8** · 4 |

**O diagnóstico, lendo caso a caso.** Nas 13 perdas com a ficha do Claude, a
justificativa do qwen é sempre a mesma: "sinais leves", "pode aguardar". Em
várias delas **a ficha certa estava em 1º lugar**, com o sinal do relato
escrito nela:
- **i13** (raticida; "sanguezinho do nariz"): a 1ª ficha era a do raticida.
  Com a ficha do Claude, o qwen disse "Sinais leves e não indicam risco
  imediato à vida". Com a do mapa, "Sangramento nasal pode indicar
  intoxicação por raticida anticoagulante".
- **i37** (eclâmpsia; "músculos tremendo, durinha, acho que é só cansaço de
  amamentar"): a 1ª ficha era a da eclâmpsia. Com a do Claude, "Sinais
  descritos são leves". Com a do mapa, "Tremores e rigidez em cadela
  amamentando indicam eclampsia puerperal, emergência obstétrica".

No oráculo, as justificativas mostram o mecanismo. O qwen usa a seção "Sinais
de alarme" **como lista de conferência**:
- "crise breve e sem repetição, **sem sinais de alerta graves**" (convulsão;
  a ficha lista "durou mais de 2 minutos; repetiu");
- "inchaço leve e comportamento normal, **sem sinais de gravidade**" (cobra);
- "o relato **não menciona sinais de alerta** ou risco à vida" (chocolate,
  com "comeu um pedaço grande de chocolate meio amargo").

**A ficha do Claude descreve a doença; a ficha do mapa é uma regra de
triagem.** A do Claude conta o quadro inteiro, com os sinais graves separados
e com a versão leve, para a busca casar com o jeito do tutor. Diante dela, o
qwen compara o relato com o quadro descrito. Quando o tutor conta uma versão
branda, ou diz "acho que é só cansaço", o modelo acha na ficha detalhada um
motivo para rebaixar: "não bate com os sinais de alarme, então é leve". A do
mapa diz, em poucas linhas, "se tem isto, é emergência". Ela não dá o que
comparar, e a regra se aplica.

**O Gemini não cai nisso.** Com as mesmas fichas do Claude: prova + régua
2 · 1, independentes 7 · 3, tom 2. É o mesmo que ele tem com a ficha do mapa
(6 · 3; tom 3; pareados p = 1,0). O modelo maior entende que o quadro
detalhado é ilustrativo e segue a conduta. **O efeito é do modelo pequeno.**

**Uma causa descartada:** o corte de 4.000 caracteres do bloco de contexto
(`CONTEXT_MAX_CHARS`). A linha de conduta fica no fim da ficha, e com as
fichas do Claude o corte aconteceu em 8 dos 256 contextos (em 3 cortou a
conduta), mas **em nenhuma das 13 perdas**.

### 5. As duas correções e o desenho que fica

Escritas às 20h40, antes de rodar. Nas duas, as 3 fichas vêm da busca na ficha
do Claude; muda só o texto que o qwen lê:
- **Leitura A:** a ficha do mapa, a validada e curta (na etapa 2 ela é
  magra).
- **Leitura B:** uma ficha do Claude curta, no formato da ficha do mapa. Os
  sinais de alarme entram na mesma lista, sem seção separada, e ficam no
  máximo 2 gêmeas. O alvo era ~100 palavras, e saiu com mediana de 141 (de
  108 a 202), porque o montador não mexe em "como diferenciar" nem em "por
  que importa". Rodei assim mesmo, sem ajustar depois de ver resultado.

Os testes cobrem os independentes, a prova + régua, o tom e o piloto da prova
2: 40 relatos novos que nenhuma decisão tinha usado
([rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md)). qwen3:8b,
emergências perdidas · falsos alarmes:

| O que a busca procura → o que o qwen lê | Prova + régua | Independentes 1 + 2 | etapa 1 / 2 (indep.) | Tom (74) | Piloto (24 · 16) |
|---|---|---|---|---|---|
| mapa → mapa (antes) | 3 · 1 | 7 · 7 | 1 / 6 | 4 | 0 · 4 |
| Claude → Claude | 3 · 1 | 13 · 6 | 6 / 7 | 8 | 2 · 2 |
| **Claude → mapa (A)** | **2 · 1** | **5 · 7** | 2 / **3** | **4** | **0 · 3** |
| Claude → Claude curta (B) | 3 · 1 | 9 · 5 | 5 / 4 | 4 | 0 · 3 |

Pareados (emergências): A × mapa → mapa, independentes 1 × 3 (p = 0,63); A ×
B, 1 × 5 (p = 0,22). No tom e no piloto, A empata com a ficha do mapa. **Nada
é significativo** com estas amostras, mas a direção é a mesma em todos os
lotes.

**Pelo critério das 20h40, fica a leitura A.** É a única que passa: 5
emergências perdidas nos independentes (≤ 7), sem piora no piloto e com 1
falso alarme na prova + régua. A leitura B melhora a ficha do Claude inteira
(13 → 9), mas ainda perde para a ficha do mapa.

**O Gemini na leitura A:** prova + régua 2 · 1, independentes 6 · 3, tom 3,
piloto 0 · 3. É igual ao Gemini com a ficha do mapa (pareados p = 1,0), e
empata com o qwen ([rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md)).

**O desenho que fica: duas camadas.**
1. **Ficha de busca** = a ficha escrita pela IA, com as variações de como o
   tutor conta e a origem de cada frase. É o que o bge-m3 indexa.
2. **Ficha de leitura** = a ficha curta do mapa, validada pelos especialistas,
   com a conduta fixa. É o que as 3 fichas mais próximas levam ao atendente.

**Uma vantagem que não estava prevista, de segurança.** O texto escrito pela
IA passa a servir **só para achar a ficha**, e nunca é lido como orientação
clínica. Se uma frase dela estiver errada, o pior que acontece é a busca
trazer a ficha errada entre as 3, e o atendente já sabe lidar com isso. O que
o atendente lê, e o que um dia pode aparecer para o tutor, continua sendo o
texto validado. Por isso a certificação das duas camadas tem pesos
diferentes: a de leitura precisa de validação rigorosa; a de busca, de uma
revisão.

**O que está provado e o que não está.** Os números da configuração
recomendada, com o qwen, ficam dentro do ruído em relação à ficha do mapa nas
duas pontas:
- prova + régua 2 · 1;
- independentes 5 · 7 (antes, 7 · 7);
- tom 4;
- piloto 0 · 3.

O ganho de segurança **não** está provado. O que está provado é que **ler a
ficha do Claude inteira piora o qwen** (no oráculo, 8 × 0, p = 0,008) e que separar busca e
leitura não piora nada e melhora a busca. Os independentes serviram para o
diagnóstico; a confirmação é a prova 2.

### 6. A folha de certificação

`data/curadoria/fichas/CERTIFICACAO.md` junta, por ficha:
- os itens que **não** vêm do mapa (documento, com o trecho, e `geral`);
- os conflitos entre o mapa e o documento;
- as notas dos autores.

São 513 itens. O trabalho dos especialistas passa a ser "aceitar, recusar ou
corrigir frases prontas", não "escrever 60 células do zero":
- a etapa 2 soma 274 itens de documento e 48 `geral`, cerca de 2 horas;
- o que eles aprovarem na etapa 2 vira o conteúdo das duas colunas vazias do
  mapa, e com isso enriquece também a ficha de leitura.

## O que mudou no repositório

| Arquivo | O que é |
|---|---|
| esta evidência | |
| `data/curadoria/fichas/<topic>.json` (61) | os rascunhos das fichas de busca, escritas pelo Claude. Cada frase traz a origem (`mapa`, `documento` com o trecho literal e o arquivo, ou `geral`) e o resultado da conferência automática |
| `data/curadoria/fichas/CERTIFICACAO.md` | a folha dos especialistas |
| `data/curadoria/fichas/README.md` | o que é a ficha de busca e o que é a de leitura, a diagramação, as regras dos autores e o estado ("rascunho, aguardando certificação") |
| `data/evaluation/autopsia2/resultados_por_caso.csv` (versionado na rodada 14) | as condições desta rodada: `e5_fichasia_top1`, `oraculo_fichaia`, `ctxarq_bge_fichashib2_top3`, `ctxarq_bge_fichascl_top3`, `ctxarq_bge_fichashibcl_top3`, `ctxarq_oraculo_fichascl`, `ctxarq_bgecl_leitura_mapa_top3` (A), `ctxarq_bgecl_leitura_curta_top3` (B), com as versões do tom e do piloto |

O texto que o backend indexa (a ficha de busca montada) e o que o atendente lê
(a ficha de leitura) **não** entram aqui. Eles são gerados a partir destes
rascunhos e do mapa, por um script, na implementação (rodadas 23 a 30), e
precisam sair byte a byte iguais aos desta autópsia para os números valerem.

## Observações

**1. As fichas de leitura têm as notas internas que a
[rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md) achou.** Todos os
números da leitura A foram medidos com elas. Limpá-las é mudança de texto de
ficha de leitura, e portanto rodada medida ([B-61](../backlog.md#b-61)).

**2. O autor forte da madrugada não rodou, e isso ensina sobre a conta
gratuita.** O `gemini-3.8-flash` tem cota de 20 chamadas por dia, e as recusas
por sobrecarga (503) **contam** nessa cota. O dia acabou com 21 recusas e
nenhuma ficha escrita.

**3. "Mesmo autor".** O Claude escreveu as fichas de busca e, na mesma noite,
instâncias isoladas dele escreveram o piloto da prova 2. Se os dois lados
"falarem do mesmo jeito", a busca parece melhor do que é. A
[rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md) mede isso: no 1º lugar,
nenhum sinal; entre os 3 primeiros, um ponto de atenção.

**4. O que a ficha do Claude muda na etapa 2, mesmo sem ser lida.** Com a busca
melhor, as perdas do qwen nos independentes da etapa 2 caíram de 6 para 3 (a
ficha lida continua sendo a magra do mapa). Preencher o mapa da etapa 2 segue
valendo, agora para o texto de leitura.

## Deixado para depois

- **A certificação** ([B-61](../backlog.md#b-61)). Tem duas partes:
  - a folha, com a etapa 2 primeiro, e os 5 conflitos;
  - a ficha de leitura da etapa 2, depois que as colunas do mapa forem
    preenchidas. Cada mudança de texto é rodada medida.
- **Uma fonte para tutor** nos quadros em que o documento não descreve o que o
  tutor vê ([B-62](../backlog.md#b-62)). Esses quadros concentram os itens
  `geral`.

## Próximo passo

Com a arquitetura desenhada, falta o instrumento que a confirme com relatos
que ninguém do sistema escreveu: a
[prova 2](2026-09-24-21-prova-2-desenho-e-piloto.md) (rodada 20).
