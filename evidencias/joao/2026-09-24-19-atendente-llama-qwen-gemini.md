# Quem decide a urgência: llama, qwen e Gemini

**Data:** 24/09/2026 (escrita em 25/09 a partir do registro da autópsia) ·
**Trilho:** B2 · **Rodada:** 18 · **Commits:** este

> Rodada de **experimento**. Nada no sistema mudou. Compara os três
> atendentes nos mesmos casos e com os mesmos contextos, e registra a
> **decisão de produto** tomada pelo João em 25/09. O critério escrito antes
> dos testes apontava o qwen; a decisão foi o Gemini, e esta rodada diz as
> duas coisas. O método está na
> [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md#como-medimos-vale-para-as-rodadas-14-a-21).

## O que foi feito

A mesma bateria para `llama3.2:3b` (o atendente de hoje), `qwen3:8b` (local,
maior) e `gemini-3.5-flash-lite` (remoto, o modelo já configurado no
projeto):
1. **Sem contexto nenhum**, na prova + régua, nos relatos de quem não viu o
   mapa e no teste de tom.
2. **Quatro frases tranquilizadoras** diferentes, coladas no fim das 74
   emergências.
3. **Uma regra no prompt contra o tom**, como defesa possível.
4. **Com a ficha certa** (oráculo), e depois **com as mesmas 3 fichas da
   busca**, a do mapa e a da configuração final.
5. **Latência** (na GPU, só no processador e pela API) e **repetibilidade**.

## Por quê

A [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md) mostrou que o
atendente de hoje decide pelo tom do tutor: o llama acerta 1 de 38
emergências contadas com calma. Isso não se conserta na busca.

O time também já tinha posto o Gemini na etapa de consulta, sem registro de
decisão, e o João decidiu, depois da autópsia, que ele fica, com o objetivo de
aumentar a capacidade de decisão e responder mais rápido. E o TCC1 promete
modelo local. Então a escolha do atendente precisa de número, com o custo de
cada opção escrito ao lado.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Os três atendentes com o **mesmo prompt** (`v1_grounded`), o **mesmo esquema de saída**, temperatura 0 e semente 42 | Muda só o modelo |
| 2 | **qwen3:8b com `think=False`** | O prompt pede o JSON direto; o modo de raciocínio do qwen3 dobra o tempo e não é o que o prompt mede |
| 3 | **Gemini por um cliente próprio, sem fallback**. Uma falha vira ERRO e o caso é refeito, e cada linha registra o modelo | O defeito que o João mandou consertar (troca silenciosa) não pode contaminar a medição |
| 4 | A bateria do Gemini **coube na cota gratuita** (500 chamadas por dia por conta no `flash-lite`), com as contas do projeto, cada uma dentro da própria cota, e intervalo de 4 a 8 s entre chamadas | A cota reinicia às 04h00 de Brasília. Recusas por sobrecarga (503) **também contam** nela |
| 5 | **Critério de escolha escrito antes** (01h00), com pesos: segurança primeiro, tom em segundo | Evita escolher o atendente depois de ver qual ganha no que se quer |
| 6 | **Decisão de produto do João (25/09):** o Gemini é o atendente padrão; qwen e llama ficam como opções selecionáveis | Registrada no fim do resultado, com os motivos e o custo |

## Resultado esperado

Escrito antes de rodar (01h00):

> Em ordem de peso: 1) emergências perdidas na melhor configuração de cada um
> (a métrica de segurança manda); 2) resistência ao tom (o risco real de uso:
> tutor que minimiza); 3) falsos alarmes; 4) repetibilidade e latência
> (≤ 5 s por caso é aceitável para triagem); 5) o custo de sair da máquina (a
> promessa do TCC1 é modelo local; o Gemini manda o relato do tutor para fora
> e depende de cota gratuita). **Regra de decisão:** se um modelo local
> empatar com o Gemini em 1 e 2 (diferença não significativa), fica o local.
> O Gemini só vale como atendente se ganhar com folga em segurança.

E dois critérios escritos antes de testes específicos:
- **Regra contra o tom (04h28):** fica se reduzir em pelo menos 1/3 as
  emergências perdidas nos relatos de quem não viu o mapa, sem aumentar em
  mais de 2 os falsos alarmes da prova + régua.
- **Frases tranquilizadoras (01h50):** se alguma frase derrubar 20% ou mais
  das emergências de um atendente **mesmo com ficha**, a prova 2 precisa de
  uma seção de tom com várias frases, e o atendente precisa de defesa.

## Resultado obtido

### 1. Sem contexto nenhum, o Gemini lê os sinais e o llama lê o tom

Emergências perdidas · falsos alarmes · acerto geral:

| | Prova + régua (74 · 58) | Relatos de quem não viu o mapa (76 · 46) | Teste de tom (74) |
|---|---|---|---|
| llama3.2:3b | 14 · 2 · 118/134 | 40 · 22 · 60/122 | **44** |
| qwen3:8b | 7 · 0 · 126/134 | 21 · 9 · 92/122 | 11 |
| gemini-3.5-flash-lite | **0** · 3 · 130/134 | **5** · 10 · 103/122 | **3** |

**Por tom, nos relatos de quem não viu o mapa:**

| Acertou | llama | qwen | Gemini |
|---|---|---|---|
| emergência contada **com calma** (38) | **1** | 17 | **33** |
| emergência aflita (20) | 20 | 20 | 20 |
| emergência neutra (18) | 15 | 18 | 18 |
| não emergência contada **com aflição** (24) | **3** | 15 | 13 |
| não emergência neutra (22) | 21 | 22 | 19 |

**Pareados** (emergências):

| Comparação | Só o primeiro perde × só o segundo perde |
|---|---|
| qwen × Gemini, prova + régua | 7 × 0 (p = 0,016) |
| qwen × Gemini, teste de tom | 10 × 2 (p = 0,039) |
| qwen × Gemini, relatos de quem não viu o mapa | **16 × 0 (p < 0,0001)** |
| llama × qwen, relatos de quem não viu o mapa | 19 × 0 (p < 0,0001) |
| llama × qwen, teste de tom | 36 × 3 (p < 0,0001) |

- **O llama segue o tom quase sem exceção.** Acerta 1 de 38 emergências
  calmas e 3 de 24 casos leves aflitos. A prova + régua não mostrava isso
  porque quase não tem esses dois tipos de relato.
- **O qwen fica no meio:** perde mais da metade das emergências contadas com
  calma (21 de 38).
- **O Gemini lê os sinais.** Sem contexto nenhum, perde 5 de 76 emergências
  e acerta 33 das 38 contadas com calma. Nos casos leves contados com aflição
  ele ainda se deixa levar: acerta 13 de 24. Os 3 falsos alarmes dele na prova + régua são defensáveis:
  - duas mordidas de morcego (risco de raiva; o mapa diz "até 24 h");
  - um abscesso de briga de gato ("caroço quente com pus").
- **No teste de tom**, das 3 emergências que o Gemini perde, duas saíram
  INCERTO por "informações contraditórias". A frase colada às vezes contradiz
  o próprio relato ("não come" + "continua comendo"), e aí INCERTO é
  defensável.

### 2. O tom não depende da frase, para o llama

As 74 emergências da prova + régua com quatro frases diferentes no fim.
Emergências perdidas, sem contexto / com a ficha mais próxima pelo e5:

| Frase acrescentada | llama3.2:3b | qwen3:8b |
|---|---|---|
| (nenhuma — relato original) | 14 / 0 | 7 / 6 |
| "Mas fora isso continua comendo e brincando normalmente." | **44** / 21 | 11 / 7 |
| "Acho que não deve ser nada grave, ele parece tranquilo." | **47** / **32** | 5 / 4 |
| "Não quero exagerar, provavelmente passa sozinho até amanhã." | **37** / 13 | 6 / 2 |
| "Mas está bem-disposto, abanando o rabo e atento a tudo." | **27** / 12 | 9 / 10 |

- **Qualquer uma das quatro frases** derruba de 36% a 64% das emergências do
  llama. A ficha protege em parte: a pior frase ainda derruba 43% das
  emergências (32 de 74).
- **O qwen é robusto a todas**: 5 a 11 perdas sem ficha, 2 a 10 com ficha.
  Nenhuma frase passa de 14%.
- **Pelo critério das 01h50, o llama falha**, e a prova 2 precisa de uma seção
  de tom com várias frases ([rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md)).

### 3. Dizer ao modelo "ignore o tom" não muda nada

Uma regra a mais nos dois prompts, com e sem contexto (variante `@sinais`):

> "Ignore a opinião do tutor sobre a gravidade (por exemplo: 'acho que não é
> nada', 'deve passar', 'estou em pânico'). Decida só pelos sinais que ele
> descreve: um tutor calmo pode estar contando uma emergência, e um tutor
> aflito pode estar contando algo leve."

| Emergências perdidas · falsos alarmes, sem a regra → com a regra | qwen3:8b | llama3.2:3b |
|---|---|---|
| prova + régua, sem contexto | 7 · 0 → 7 · 0 | 14 · 2 → 11 · 2 |
| relatos de quem não viu o mapa, sem contexto | 21 · 9 → 22 · 9 | 40 · 22 → 38 · 23 |
| relatos de quem não viu o mapa, bge-m3 + porta | 21 · 11 → 22 · 10 | 37 · 22 → 37 · 23 |
| teste de tom | 11 → 12 | 44 → 42 |

**Nenhum efeito.** Pelo critério das 04h28, a regra não fica. O que muda o
comportamento diante do tom é outra coisa: **a ficha certa no prompt**, ou um
atendente que já lê os sinais.

### 4. Com a ficha certa, o qwen deixa de cair no tom; o llama, não

Relatos de quem não viu o mapa, só a ficha certa no prompt:

| | Emergências perdidas (76) | Calmas acertadas (38) | Falsos alarmes (46) |
|---|---|---|---|
| qwen, sem contexto | 21 | 17 | 9 |
| **qwen, ficha certa** | **0** | **38** | 4 |
| llama, sem contexto | 40 | 1 | 22 |
| llama, ficha certa | **25** | — | 22 |

Para o qwen, **a ficha certa neutraliza o tom por completo**. O llama ignora a
ficha e segue o tom, mesmo com o protocolo do quadro na mão. A distância do
qwen para o Gemini, então, está na busca: é a ficha certa que precisa chegar.
Por isso as [3 fichas mais próximas, sem porta](2026-09-24-17-busca-bge-m3-e-tres-fichas.md#4-a-porta-de-entrada-do-porteiro-às-três-fichas)
aproximam os dois.

### 5. Com as mesmas 3 fichas, qwen e Gemini empatam

As 3 fichas do mapa mais próximas pelo bge-m3, sem porta, iguais para os três:

| 3 fichas do mapa (bge-m3) | Prova + régua (74 · 58) | Relatos de quem não viu o mapa (76 · 46) | Tom (74) |
|---|---|---|---|
| llama3.2:3b | 2 · 4 | 29 · 24 | 21 |
| qwen3:8b | 3 · 1 | 7 · 7 | 4 |
| gemini-3.5-flash-lite | 1 · 0 | 6 · 3 | 3 |

- **Pareados qwen × Gemini:** prova + régua 2 × 0 (p = 0,50); relatos de quem
  não viu o mapa 3 × 2 (p = 1,0); tom 2 × 1 (p = 1,0). No acerto geral dos
  independentes, 5 × 3 (p = 0,73). **Empate em tudo.**
- **No Gemini, as fichas quase não mudam as emergências** (sem contexto × 3
  fichas: 0 × 1 na prova + régua, 2 × 3 nos independentes; p = 1,0). Ele já
  lia os sinais sozinho. Mas elas **cortam os falsos alarmes**: de 3 para 0 na
  prova + régua, de 10 para 3 nos independentes.
- **O llama melhora com as fichas** (tom: 44 → 21), mas continua muito atrás.

### 6. Na configuração final, o empate se mantém

A busca é nas fichas de busca e a leitura é na ficha do mapa
([rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)). Emergências perdidas ·
falsos alarmes · acerto geral:

| | Prova + régua (74 · 58) | Relatos de quem não viu o mapa (76 · 46) | Tom (74) | Piloto da prova 2 (24 · 16) |
|---|---|---|---|---|
| qwen3:8b | 2 · 1 · 130/134 | 5 · 7 · 109/122 | 4 | 0 · 3 |
| gemini-3.5-flash-lite | 2 · 1 · 129/134 | 6 · 3 · 109/122 | 3 | 0 · 3 |

Pareados qwen × Gemini (emergências):

| Conjunto | Resultado |
|---|---|
| prova + régua | 0 × 0 |
| independentes | 1 × 2 (p = 1,0) |
| tom | 2 × 1 (p = 1,0) |
| piloto | 0 × 0 |
| acerto geral dos independentes | 4 × 4 |

**As 6 emergências que o Gemini perde nos independentes:** 5 são INCERTO,
porque "faltam detalhes para definir a urgência". É o jeito dele,
conservador, e a métrica conta INCERTO como perda.

| Caso | Quadro | Tom | Resposta |
|---|---|---|---|
| i02 | piometra | aflito | INCERTO ("corrimento de pus e apatia, mas faltam detalhes") |
| i05 | leptospirose | calmo | INCERTO |
| i17 | cetoacidose diabética | calmo | INCERTO |
| i31 | cinomose neurológica | calmo | NÃO EMERGÊNCIA ("apenas tremores leves na face") |
| j03 | chumbinho | calmo | INCERTO ("babou um pouco após comer algo") |
| j33 | piometra | calmo | INCERTO |

**Os 3 falsos alarmes dele** são todos de relatos aflitos, e dois estão em
relatos de rótulo discutível (observação 2):
- cio com "sangramento ativo na caminha" (i59);
- "comeu um pedaço de chocolate" (j39);
- "inchaço enorme na cara" depois do jardim (j47).

### 7. Velocidade e repetibilidade

Tempo da chamada ao modelo, por caso:

| Atendente | Onde roda | Mediana | 9 em 10 abaixo de | 99 em 100 abaixo de | Pior caso |
|---|---|---|---|---|---|
| llama3.2:3b, sem contexto | RTX 4060 | 1,1 s | 1,2 s | 1,4 s | 5,3 s |
| qwen3:8b, configuração final | RTX 4060 | 2,6 s | 2,9 s | 3,2 s | 3,3 s |
| qwen3:8b, mesmo prompt, 8 relatos | **só o processador** (i5-14400F) | **34 s** | (de 31 a 38 s) | — | 58 s (1ª chamada, carregando o modelo) |
| gemini-3.5-flash-lite, configuração final | API | **1,1 s** | 1,7 s | **26 s** | 31 s |
| gemini-3.5-flash-lite, as 2.163 chamadas da autópsia | API | 1,1 s | 2,9 s | 22 s | **190 s** |

- **O Gemini é o mais rápido na mediana e o menos previsível.** Uma chamada
  em cada 100 passou de 20 s. Na conta gratuita há horas de sobrecarga, em que
  cada nova tentativa custa de segundos a minutos.
- **O qwen é estável na GPU, mas depende dela.** Sem a placa de vídeo, fica
  13 vezes mais lento (34 s por caso) e estoura os 5 s do critério. O método
  confere: o mesmo script, com a GPU, dá 2,8 s.
- **Repetibilidade:** o Gemini, rodado duas vezes sem contexto nos 134 casos,
  deu **134 de 134 respostas iguais** (temperatura 0 e semente fixa). O llama
  também deu 134 de 134 na mesma sessão. Entre sessões, as diferenças são de
  1 a 3 casos ([rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md#7-os-limites-dos-próprios-instrumentos)).

### 8. Chain-of-Thought, de passagem (23/09)

O checklist do projeto (`cot_position = first`), sem contexto e com fichas:

| | Prova (`dev` + calibração, 34 · 32) | Régua (40 · 26) |
|---|---|---|
| llama, sem CoT | 8 · 2 · 58/68 | 6 · 0 · 60/66 |
| llama, CoT | 8 · 2 · **38/68** | 7 · 4 · 40/66 |
| llama, CoT + 3 fichas e5 | 2 · 10 · 50/68 | 1 · 6 · 58/66 |
| qwen, sem CoT | 5 · 0 · 62/68 | 2 · 0 · 64/66 |
| qwen, CoT | 9 · 0 · 59/68 | — |
| qwen, CoT + 3 fichas e5 | 2 · 3 · 56/68 | — |

**O CoT piora os dois modelos locais.** No llama, no `dev`, 17 de 24 casos
leves e 4 de 25 emergências viraram INCERTO. A lista de verificação oferece a
opção "não sei", e o modelo se refugia nela. Fica adiado, por decisão do João
(depois do RAG consolidado), como braço da ablação; ver o
[B-42](../backlog.md#b-42).

### A decisão

**Pelo critério escrito às 01h00, ficaria o qwen.** Com as mesmas fichas, ele
empata com o Gemini em emergências perdidas e em tom, e a regra dizia: se um
local empatar, fica o local. A conclusão da madrugada (05h50) foi essa.

Essa conclusão mudou duas vezes na mesma noite:
- **às 04h55, o Gemini ganhava com significância**, porque o qwen ainda
  recebia a ficha pela porta de confiança, que barrava a ficha certa nos
  relatos de quem não viu o mapa;
- **com as 3 fichas sem porta, às 05h25, o qwen alcançou o Gemini**, e o teste
  do Gemini com as mesmas 3 fichas, na noite de 24/09, confirmou o empate.

**A decisão de produto, do João, em 25/09: o Gemini é o atendente padrão; o
qwen e o llama ficam como opções selecionáveis.** O que pesou, medido:

| A favor do Gemini | O custo (vai para o backlog) |
|---|---|
| Menos falsos alarmes com as mesmas fichas (3 contra 7 nos independentes) | O relato do tutor sai da máquina para o Google (LGPD, [B-64](../backlog.md#b-64)) |
| Mais rápido na mediana (1,1 s contra 2,6 s) | Cota gratuita de 500 chamadas por dia por conta; as recusas por sobrecarga também contam |
| Não depende de placa de vídeo (o qwen, sem ela, leva 34 s por caso) | Cauda de latência: 1 em 100 chamadas acima de 20 s ([B-65](../backlog.md#b-65)) |
| O melhor sem contexto (5 · 10 contra 21 · 9): se a busca falhar, ainda lê os sinais | Depende de rede e da disponibilidade do Google |
| Já era a decisão do time: aumentar a capacidade de decisão e responder mais rápido | Contradiz a promessa de modelo local do TCC1 (vai para as pendências do artigo) |

**Condições que a implementação cumpre**, pedidas pelo João depois da
autópsia:
1. **Nunca trocar de modelo em silêncio.** Se o Gemini falhar ou a cota
   acabar, a resposta diz isso. A alternativa local só entra quando
   configurada explicitamente, e registrada.
2. **A resposta registra quem respondeu:** provedor, modelo e versão.
3. **O qwen fica como opção local declarada**, para quem não pode mandar dados
   para fora. O **llama fica como o sistema de hoje**, braço da ablação.

## O que mudou no repositório

| Arquivo | O que é |
|---|---|
| esta evidência | |
| `data/evaluation/autopsia2/resultados_por_caso.csv` (versionado na rodada 14) | as condições desta rodada: `sem_rag`, `cue_calmo` a `cue_calmo4` (com e sem ficha e5), `sem_rag@sinais`, `ctxarq_bgeprod_fichas@sinais`, `cue_calmo@sinais`, `oraculo_ficha`, `ctxarq_bge_fichas_top3` e `cue_calmo_ctxarq_bge_fichas_top3`, `ctxarq_bgecl_leitura_mapa_top3` e `cue_calmo_ctxarq_bgecl_leitura_mapa_top3`, `sem_rag_rep2`, `sem_rag_repeticao`, `cot_*`, nos três atendentes, com o tempo de cada chamada |

## Observações

**1. O Gemini é conservador.** Quando falta informação, ele responde INCERTO,
e a métrica conta isso como emergência perdida. Na triagem de verdade, um
INCERTO precisa virar uma pergunta ao tutor ou um "procure o veterinário se…".
Isso é desenho da resposta, não do modelo.

**2. Três erros do Gemini nos independentes estão em relatos de rótulo
discutível.** O autor do relato escolheu o quadro, não um veterinário:
- **j39** ("comeu um pedaço de chocolate", marcado leve como "comeu algo fora
  da dieta"): o mapa tem a intoxicação por chocolate como emergência;
- **j47** ("inchaço enorme na cara", marcado leve como picada de inseto
  local): o mapa tem o inchaço facial da anafilaxia como emergência;
- **j07** ("rosto meio inchado", "picada de algum bicho", marcado como cobra):
  é ambíguo entre os dois.

Some-se o "pão com passas" da [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md#6-o-sistema-de-hoje-nos-relatos-de-quem-não-viu-o-mapa-e-no-teste-de-tom)
e fica o argumento para a prova 2 ter o rótulo validado por veterinário.

**3. O teste de tom com frase colada subestima o problema.** Com relatos
**naturalmente** calmos, o qwen perde 21 de 38 emergências calmas; com a frase
colada, 11 de 74. O teste mais natural é o do autor independente.

**4. Uma ideia de Self-Refine, para quando ele voltar à pauta.** Com um
atendente forte, o erro deixa de ser "raciocinar mal" e passa a ser o
contexto errado (a ficha de outro assunto leva a INCERTO). Um Self-Refine útil
conferiria **se o contexto é do mesmo assunto do relato** e se a justificativa
só usa sinais do relato, em vez de reescrever a resposta
([B-70](../backlog.md#b-70)).

**5. Uma lista de sinais de alarme gerais.** No estilo dos discriminadores do
protocolo de Manchester ou da VTL, sempre presente no prompt, ela protegeria o
relato cuja ficha não chega. Tentei montá-la com os sinais do mapa e desisti
antes de rodar. Fora do contexto de cada quadro, "vomitando" e "babando"
viram emergência, o que não é o que os especialistas validaram. Tem de ser
escrita e validada por eles ([B-68](../backlog.md#b-68)).

## Deixado para depois

- **LGPD com o Gemini como padrão** ([B-64](../backlog.md#b-64)): aviso ao
  tutor, consentimento, nada de dado pessoal no texto, opção "só local" e o
  relato fora dos logs. É rodada própria, por decisão do João.
- **Latência na demonstração** ([B-65](../backlog.md#b-65)): a cauda do Gemini
  e o qwen sem GPU.
- **Sinais de alarme gerais** ([B-68](../backlog.md#b-68)) e **Self-Refine**
  ([B-70](../backlog.md#b-70)).
- **CoT com o atendente escolhido** ([B-42](../backlog.md#b-42)): só na
  configuração final, porque o efeito muda com o modelo.

## Próximo passo

A [rodada 19](2026-09-24-20-fichas-em-duas-camadas.md): as fichas escritas por
IA, e por que a busca e a leitura usam fichas diferentes.
