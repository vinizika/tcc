# Autópsia 2: o sistema de 23/09, medido

**Data:** 23/09/2026 (escrita em 25/09 a partir do registro da autópsia) ·
**Trilho:** B2, olhando o sistema inteiro · **Rodada:** 14 · **Commits:** este

> Rodada de **análise**. Nada no sistema mudou. É a primeira de oito rodadas
> que registram a autópsia 2 (14 a 21). Esta mede o sistema como ele está em
> `fceab20`. As seguintes testam, peça por peça, o que o substitui, e a
> [rodada 21](2026-09-24-22-arquitetura-proposta-contra-a-de-hoje.md) junta tudo.
> A primeira parte dos números saiu dos runners do repositório (rodadas
> citadas). O resto saiu de um executor próprio, que chama o código do
> pipeline por dentro e foi conferido contra o runner. A seção "Como medimos",
> no fim do resultado, vale para as oito rodadas.

## O que foi feito

Uma medição do sistema como o repositório o entrega em 23/09, numa cópia de
`fceab20`, com a coleção candidata de 3.481 trechos
(`veterinary_documents__20260920T160842289762Z__388f518d`) ativada **só na
cópia**. Foram três frentes:

1. **Classificação com e sem RAG** nos quatro conjuntos do time: a prova
   (lotes `dev` e calibração), a régua de recuperação e o conjunto antigo dos
   98 relatos. Rodou pela API, com os runners do repositório, com o
   atendente de hoje (`llama3.2:3b`).
2. **O caminho de um trecho até o prompt.** O que a busca devolve, o que passa
   pela porta de 0,72 e por quê. Isso inclui a régua de recuperação e a
   composição da base.
3. **O sistema de hoje em dois instrumentos novos**, construídos para o que a
   prova não mede. O primeiro são 122 relatos escritos por quem **não viu o
   mapa**. O segundo é o teste de tom: a mesma emergência com uma frase
   tranquilizadora no fim.

## Por quê

Até 12/09, a pergunta do TCC tinha resposta negativa e mecanismo conhecido:
com a base sintética, o RAG custava 20 pontos
([rodada 4](2026-09-04-05-runner-de-avaliacao.md)) e, com o corte, ficava
silencioso ([rodada 9](2026-09-12-10-corte-de-relevancia.md)). Entre 13 e
22/09 o sistema mudou muito:
- 66 documentos cobrindo os 61 quadros do mapa;
- a ingestão versionada;
- o roteador por assunto e o reranker;
- a prova nova de 150 casos;
- a etapa de consulta com o Gemini.

A pergunta voltou a estar em aberto: **com a base real, o RAG ajuda a
triagem?** A porta de decisão de 26/09 precisava de números, e o João pediu
uma autópsia antes de voltar a desenvolver.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Medir numa cópia, sem ativar nada no repositório; **o lote `teste` da prova não é usado** | O `teste` só pode ser tocado uma vez, pela configuração final. Uma autópsia não é essa ocasião |
| 2 | **Emergência perdida inclui INCERTO** | É o critério mais seguro: um INCERTO dado a uma emergência não manda o tutor ao veterinário |
| 3 | Dois instrumentos novos: **relatos de quem não viu o mapa** e **teste de tom** | A prova e a régua foram escritas com o mapa na mão e quase não têm relato "grave contado com calma". Os dois instrumentos medem exatamente o que elas não medem (ver o resultado 6) |
| 4 | **Executor próprio**, conferido contra o runner | Para trocar o que entra no prompt (trecho certo, ficha, três fichas) sem mexer no código. O runner não permite isso. A conferência: 18 de 18 previsões iguais às do runner na calibração, com e sem RAG |
| 5 | Toda linha registra **qual modelo respondeu**; falha vira ERRO, **nunca** troca de modelo | O pipeline de hoje troca o Gemini pelo Ollama em silêncio na etapa de consulta. O executor não pode repetir esse defeito |
| 6 | Este registro fica **só com os achados técnicos** | O relatório daquela tarde também tratava de processo. O João decidiu que esses pontos não são prioridade, e eles não mudam nenhum número |

**Decisões do João depois de ler a autópsia** (valem para as rodadas 14 a 21
e para a implementação):
- **O Gemini fica.** Foi decisão do time, e o objetivo é aumentar a capacidade
  de decisão e responder mais rápido. No mínimo, fica como braço da ablação.
  O time quer mostrar o ganho dele contra o Ollama.
- **O registro de qual modelo respondeu passa a ser obrigatório** em todo
  teste.
- **A troca silenciosa Gemini → Ollama precisa ser consertada.** Quando a
  cota acabar, isso tem de ficar claro, e os dois nunca se misturam.
- **CoT e Self-Refine ficam para depois**, quando o RAG estiver consolidado.
  A ablação completa é "praticamente a última parte".
- **LGPD:** reconhecida, fica para uma rodada própria. **README:** precisa ser
  revisto.

## Resultado esperado

**Não houve previsão escrita antes desta rodada**, porque ela nasceu como
diagnóstico. O que existia escrito antes eram os **critérios da porta de
decisão**, fixados em 12/09 (`data/curadoria/README.md`) antes de qualquer
medição com a base nova. Eles servem de esperado:

| Critério da porta (12/09) | O que ele pedia |
|---|---|
| Velocidade | ≥ 25 das 31 linhas da etapa 1 aprovadas ou indexadas |
| Ordenação | casos que pioraram ≤ casos que melhoraram |
| Ímã | nenhum documento em 1º em mais de 1/3 dos casos |
| Ruído nos leves | nenhum caso leve com trecho acima do corte |
| Cobertura real | ≥ 70% dos quadros novos entre os cinco do próprio caso |
| Classificação | RAG não pior que sem RAG, além do ruído de 2 a 3 linhas |

A partir de 24/09 00h56, todo teste das rodadas seguintes teve critério
escrito antes, com a hora.

## Resultado obtido

### 1. Com a base de 3.481 trechos, o RAG não ajuda

Rodadas feitas pelos runners do repositório, pela API, com o `llama3.2:3b`.
O mesmo backend, o mesmo modelo e a mesma coleção; só a busca liga e desliga.

| Conjunto | Casos | Acertos sem RAG → com RAG | Emergências perdidas | Falsos alarmes | Consertou · quebrou |
|---|---:|---|---|---|---|
| Prova, lote `dev` | 50 | 43 → 43 | 5/25 → 4/25 | 2/24 → 3/24 | 1 · 1 |
| Prova, calibração | 18 | 15 → 14 | 3/9 → 3/9 | 0/8 → 1/8 | 0 · 1 |
| Régua do trilho A | 66 | 59 → 57 | 7/40 → 9/40 | 0/26 → 0/26 | 1 · 3 |
| Conjunto antigo | 98 | 86 → 83 | 7/71 → 9/71 | 5/27 → 6/27 | 0 · 3 |
| **Total** | **232** | **203 → 197** | **22 → 25** | **7 → 10** | **2 · 8** |

Pareado, caso a caso, o RAG conserta 2 e quebra 8 (McNemar exato,
p = 0,11). A diferença não é significativa, mas a direção é a mesma nos
quatro conjuntos, e não há ganho em nenhum deles. **Pelo critério
"classificação" da porta, o RAG passa em cada conjunto isolado, sem nenhum
ganho e com a direção contra.**

**O pipeline completo, como um clone sem a chave do Gemini o executa.** A
reescrita e o multi-query rodam pelo Ollama e o HyDE é pulado sem aviso. No
conjunto antigo:

| 98 casos | Acertos | Emergências perdidas | Falsos alarmes | Casos com trecho no prompt |
|---|---:|---:|---:|---:|
| Sem RAG | 86 | 7 | 5 | 0 |
| RAG direto | 83 | 9 | 6 | 43 |
| Pipeline completo | 81 | 2 | **15** | **88** |

O tradutor inventa consultas: um relato de secreção ocular e nasal gerou
"Diagnóstico de coccidiose em cães" e "Tratamento com antibióticos para
infecções fúngicas". Com isso, 88 dos 98 casos passam a receber trecho. **Os
15 falsos alarmes estão todos entre eles.** O sistema trocou 5 emergências
perdidas por 10 falsos alarmes e manda para a emergência 15 dos 27 casos
leves. A [rodada 17](2026-09-24-18-tradutor-desligado.md) mede o tradutor por
inteiro.

**As rodadas citadas**, com o trecho que o `report_evaluation.py cite`
imprime. Os números do runner e os das tabelas acima medem coisas um pouco
diferentes:
- o runner conta como "falso não urgente" só a emergência respondida NÃO
  EMERGÊNCIA;
- as tabelas desta rodada contam também o INCERTO.

Em cada uma das quatro rodadas, 2 emergências saíram INCERTO, e é essa a
diferença entre os dois números. É o motivo do [B-60](../backlog.md#b-60).

- Rodada [`20260923-181051_autopsia_llm_only`](../../data/evaluation/cited/20260923-181051_autopsia_llm_only/report.md) · preset `llm_only` · 98 linhas · acurácia balanceada 0.8581, estrita 0.8776, 5 falso(s) não urgente(s).
- Rodada [`20260923-181625_autopsia_naive_rag_cand3481`](../../data/evaluation/cited/20260923-181625_autopsia_naive_rag_cand3481/report.md) · preset `naive_rag` · 98 linhas · acurácia balanceada 0.8255, estrita 0.8469, 7 falso(s) não urgente(s).
- Rodada [`20260923-183742_autopsia_rag_query_sem_gemini`](../../data/evaluation/cited/20260923-183742_autopsia_rag_query_sem_gemini/report.md) · preset `rag_query` · 98 linhas · acurácia balanceada 0.7081, estrita 0.8265, 0 falso(s) não urgente(s).
- Rodada [`20260923-183115_autopsia_ab_prompt_1209`](../../data/evaluation/cited/20260923-183115_autopsia_ab_prompt_1209/report.md) · preset `llm_only` · 98 linhas · acurácia balanceada 0.8740, estrita 0.8673, 8 falso(s) não urgente(s). É o A/B do prompt (observação 1).

As rodadas da prova e da régua na classificação saíram do runner da prova.
Estão em `data/evaluation/prova_runs/20260923-*_autopsia_*`: `dev`,
calibração e régua, com e sem RAG, e o A/B do prompt.

### 2. A busca acha o assunto pelo vocabulário do mapa

| Medida | Régua do trilho A (66) | Prova, `dev` + calibração (66) |
|---|---:|---:|
| Assunto certo em 1º | 51,5% | 39,4% |
| MRR | 0,570 | 0,466 |
| Assunto certo entre os cinco | 66,7% | 59,1% |
| Etapa 1 em 1º (mapa com sinais) | 24 de 36 | 23 de 41 |
| Etapa 2 em 1º (mapa sem sinais) | 10 de 30 | 3 de 22 |

Rodada citada da régua:
`data/retrieval/cited/20260923-175254_autopsia_candidata_3481`.

A régua reproduz exatamente o número do benchmark do trilho A (51,5%): ela
continua determinística. E o protocolo-ímã acabou. O documento mais
frequente em 1º caiu de 9 casos em 18 (12/09) para 5 em 66.

O mecanismo, conferido no código e nos dados:
1. O **roteador lexical** (`topic_router.py`) usa o vocabulário das colunas
   `quadro` e `sinais_que_o_tutor_relata` do mapa. Ele inclui o assunto certo
   em 36 de 36 casos da etapa 1 na régua e em 40 de 41 na prova. Na etapa 2,
   cujas linhas nunca tiveram os sinais preenchidos, isso cai para 6 de 30 e
   3 de 22.
2. Quando a rota é confiante, a nota do trecho sobe para **0,721**, logo acima
   do corte de 0,72 (`reranker_client.py`, `ROUTING_SCORE_FLOOR`).
3. **A maior similaridade de vetor em toda a régua é 0,709. Nenhum trecho
   passa o corte por mérito próprio.** Dos 18 casos da régua que recebem
   contexto, 15 entram pelo piso da rota e 3 pelos bônus lexicais. Entrou no
   prompt até trecho com similaridade 0,074 (a mediana dos que entram é
   0,475).

Ou seja: o "RAG" de hoje é um roteador de palavras-chave que injeta trechos do
assunto adivinhado. Isso não é defeito em si: é o conhecimento do mapa
virando regra. Mas precisa ser descrito assim no artigo, e a régua que o
avalia não pode ser escrita com o mesmo vocabulário (resultado 7).

### 3. Quase nenhum relato chega ao atendente com contexto

Nos mesmos casos, pelo executor (condição `rag_full`, a busca de hoje com o
relato cru):

| | Prova + régua | Relatos de quem não viu o mapa |
|---|---:|---:|
| Casos que chegam ao atendente **sem nenhum trecho** | **104 de 134** | **116 de 122** |

E, quando o trecho chega, é do assunto certo e não serve para triar:

| Caso | Relato | O que entrou no prompt | Resultado |
|---|---|---|---|
| p31, emergência | Paracetamol dado a gato; gengiva e orelhas arroxeadas | Estatística de intoxicação por diclofenaco e ibuprofeno; a importância dos centros toxicológicos | Continuou "não emergência" |
| p49, leve | Cão idoso rígido de manhã, melhora ao andar | Tecido adiposo, inflamação sistêmica, programa de perda de peso | Virou falso alarme |
| p25, emergência | Gato com seis vômitos e diarreia com sangue | Enteropatógenos e prescrição empírica de antimicrobianos | Já estava certo sem RAG |

Em 12/09 o problema era ordenação: vinha o assunto errado. Em 23/09 vem o
assunto certo, com um trecho que não diz quando procurar o veterinário.

### 4. A base: volume no lugar de conteúdo

Medido na coleção candidata, pelos metadados e pelo texto dos trechos:

| Medida | Valor |
|---|---|
| Documentos / trechos / tópicos | 66 / 3.481 / 61 |
| Idioma dos trechos | 96% inglês, 4% português |
| Registro das fichas de documento | 60 acadêmico, 4 clínico, 1 tutor, 2 sem registro (67 fichas) |
| Trechos com marca de relato de pesquisa (n =, p <, %, figura, tabela, dose) | 25% |
| Trechos com qualquer linguagem de orientação ou urgência | 3% (heurística larga); 0,3% (estrita) |
| Parte da base que é da etapa 2 | 68,8% |
| Parte da base das linhas de prioridade A | 19,0% |
| Parto normal (quadro leve), sozinho | 235 trechos |
| Torção gástrica + trauma + vômito com diarreia + dificuldade respiratória, somados | 59 trechos |

Três trechos sorteados ao acaso mostram o problema:
- um descreve o teste t da temperatura de cães após exercício;
- outro fala de mutações genéticas em leucemia humana, na ficha de "caroço
  de crescimento lento";
- o terceiro trata do grupo controle de um estudo de necropsia, na ficha de
  "tosse dos canis leve".

As fichas de documento também **trocam o título real por um título genérico**.
O artigo *Diagnostic performance of lung ultrasound compared to thoracic
radiography…* aparece como "Respiratory Distress in Dogs and Cats", e esse
título é mostrado ao tutor como a fonte citada. A
[rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md) mede o efeito disso
na busca. Na citação, o título genérico engana.

### 5. A âncora que esconde a obstrução uretral

A obstrução uretral no gato macho mata em 24 a 72 horas; é o par de maior
letalidade do mapa. Na busca de produção:

| Frase do tutor | Obstrução entre os cinco? | O que vem em 1º |
|---|---|---|
| "minha gata não consegue fazer xixi desde ontem fica tentando na caixa e miando de dor" (a da régua) | Sim, em 1º | obstrução uretral |
| "meu gato vai na caixa e não sai nada, faz força e mia" (os sinais do próprio mapa) | **Não** | cistite, a gêmea leve |
| "meu gato não consegue mijar, fica tentando e chora" | **Não** | dificuldade respiratória |

Só a formulação que está na régua funciona. A causa foi achada na madrugada
seguinte ([rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md)): o campo
`retrieval_anchors` veta o documento quando o relato não tem nenhuma das
palavras da lista. Isso acontece mesmo quando o roteador aponta a obstrução
com confiança máxima.

### 6. O sistema de hoje nos relatos de quem não viu o mapa e no teste de tom

**Os dois instrumentos novos.**
- **Relatos de autor independente** (`data/diagnostico/relatos_independentes.csv`).
  São 122 relatos, 61 por autor, um por quadro do mapa. Os dois autores são
  modelos de IA de famílias diferentes do atendente testado
  (`gemma-4-31b-it` e `gemini-3.1-flash-lite`).
  - **O que cada autor recebeu:** só o nome leigo do quadro, a espécie, se é
    ou não emergência e o tom. **Não** recebeu a coluna de sinais do mapa,
    nem as fichas, nem a prova.
  - **Composição, por autor:** 38 emergências (19 contadas com calma ou
    minimizando, 10 aflitas, 9 neutras) e 23 não emergências (12 aflitas ou
    exageradas, 11 neutras).
  - **Rótulo:** a urgência do mapa.
  - **Limitações:** texto de IA, não de tutor; o rótulo vem do quadro pedido,
    não de um veterinário; há pelo menos um rótulo discutível ("comeu pão
    com passas", marcado como leve; uva-passa é tóxica para cães).
- **Teste de tom.** Uma frase tranquilizadora é colada no fim de cada uma das
  74 emergências da prova e da régua: "Mas fora isso continua comendo e
  brincando normalmente." A [rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md)
  acrescenta mais três frases, de tipos diferentes.

**O sistema de hoje nesses instrumentos**, pelo executor (`llama3.2:3b`, base
acadêmica, MiniLM, porta 0,72). Emergências perdidas · falsos alarmes ·
acerto geral:

| | Prova + régua (74 · 58) | Relatos de quem não viu o mapa (76 · 46) |
|---|---|---|
| sem contexto | 14 · 2 · 118/134 | 40 · 22 · 60/122 |
| **busca de hoje, relato cru** | **15 · 4 · 115/134** | **40 · 22 · 60/122** |
| busca de hoje + tradutor (reescrita, multi-query e HyDE gerados pelo llama) | 8 · 3 · 121/134 | 37 · 23 · 62/122 |

| Nos relatos de quem não viu o mapa (busca de hoje) | llama3.2:3b |
|---|---|
| emergências contadas **com calma**, acertadas | **1 de 38** |
| não emergências contadas **com aflição**, acertadas | **3 de 24** |
| emergências aflitas ou neutras, acertadas | 35 de 38 |
| **Teste de tom:** emergências perdidas com a frase colada | **46 de 74** (sem a frase: 15) |

Três leituras:
- **Nos relatos de quem não viu o mapa, o sistema de hoje erra metade**: perde
  40 das 76 emergências e alarma 22 dos 46 casos leves (acerto de 49%, o de
  cara ou coroa). E a busca não entra na conta. Nesses relatos, 116 de 122
  chegam sem nenhum trecho, e a busca de hoje dá o mesmo resultado que "sem
  contexto", caso a caso.
- **O llama decide pelo tom do tutor, não pelos sinais.** Ele acerta 1 de 38
  emergências contadas com calma e 3 de 24 casos leves contados com aflição.
  A prova não mostrava isso porque quase não tem esses casos (resultado 7).
- **O tradutor ligado muda o quadro na prova** (15 → 8 perdidas, porque mais
  consultas furam a porta; ver a [rodada 17](2026-09-24-18-tradutor-desligado.md)),
  **e quase nada nos relatos de quem não viu o mapa** (40 → 37).

O mesmo sistema com o `qwen3:8b` no lugar do llama perde 7 · 0 na prova +
régua e 21 · 9 nos relatos independentes. A escolha do atendente está na
[rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md).

### 7. Os limites dos próprios instrumentos

- **A prova (150 casos).** Medido com implementação própria:
  - a regra "tem a palavra 'mas', então não é emergência" acerta **76%** dos
    147 casos binários;
  - um classificador de palavras (Naive Bayes) treinado no lote `teste`
    acerta **94%** do lote `dev`;
  - 84 dos 98 casos binários do `teste` repetem um assunto do `dev`;
  - há só 3 casos "grave contado com calma" e 3 INCERTO;
  - os 8 "fora do mapa" são todos perguntas não clínicas, e todos leves.
  
  A [rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md) mede isso com a
  divisão por assunto e desenha a prova 2.
- **A régua de recuperação** foi escrita com o vocabulário do mapa. 22 de 36
  casos da etapa 1 (61%) copiam literalmente uma frase de sinal de duas ou
  mais palavras do próprio quadro no mapa; na prova, 12 de 41 (29%).
- **Ruído do executor.** A mesma condição rodada duas vezes na mesma sessão
  dá 0 diferenças em 134 casos. Depois de uma noite trocando de modelo na
  GPU, dá 1 em 134. Entre a sessão da API (tarde) e a do executor (noite), no
  conjunto antigo, dá 3 em 98. **Diferenças de 1 a 3 casos podem ser
  ruído**; acima disso, o efeito é real.

### A porta de decisão com estes números

| Critério | Hoje | Resultado |
|---|---|---|
| Velocidade | 29 de 31 linhas da etapa 1 com "fonte aprovada"; nenhuma indexada (a candidata está inativa) | Passa no papel |
| Ordenação | 8 casos comparáveis: 2 melhoraram, 1 piorou, 5 iguais | Passa, com amostra pequena |
| Ímã | 7,6% na régua; 15% na prova | Passa (era 50%) |
| Ruído nos leves | nenhum leve recebe trecho de emergência; 6 de 26 recebem trecho do próprio quadro leve | Passa no espírito; o texto do critério ficou velho |
| Cobertura real | 61% na régua; 56% na prova | **Reprova** |
| Classificação | −1 a −3 acertos por conjunto; conserta 2 e quebra 8 no total | Passa em cada conjunto isolado, sem nenhum ganho |

Seis emergências **nunca** aparecem entre os cinco primeiros em nenhuma das
duas réguas:
- carbamato ("chumbinho"), metade das intoxicações felinas na USP;
- permetrina em gato;
- cinomose neurológica;
- distocia;
- corpo estranho gastrointestinal;
- síndrome vestibular.

Os dois primeiros são da etapa 1 e de prioridade A.

### Como medimos (vale para as rodadas 14 a 21)

**Duas fontes de número.**
- **Os runners do repositório, pela API** (tarde de 23/09). São 13 rodadas,
  versionadas nesta rodada, cada uma na pasta do seu runner (ver "O que
  mudou no repositório").
- **O executor da autópsia** (23 e 24/09). Ele chama por dentro o próprio
  código do pipeline de `fceab20` (`ChatPipeline._build_queries`, `_retrieve`,
  `_classify`), sem servidor HTTP. Isso permite trocar só o que entra no
  prompt: nenhum trecho, os trechos da busca de hoje, o trecho certo, uma ou
  três fichas.
  - **Conferência contra o runner:** 18 de 18 previsões iguais na calibração,
    com e sem RAG, e o mesmo número de trechos.
  - **Onde está o resultado:** cada caso, em cada condição, está em
    `data/evaluation/autopsia2/resultados_por_caso.csv` (atendente, lote,
    condição, esperado, previsto, fichas ou trechos que entraram no prompt).
    As justificativas que as evidências leem estão em
    `justificativas_citadas.csv`, e o `README.md` ao lado descreve cada
    condição e mostra como recontar qualquer número.

**Lotes.**

| Lote | O que é | Casos |
|---|---|---:|
| prova `dev` | prova do trilho B1, lote de desenvolvimento | 50 |
| prova calibração | idem, calibração | 18 |
| régua | régua de recuperação do trilho A (`data/retrieval/cases.csv`) | 66 |
| antigo | os 98 relatos de 04/09 (listas de sintomas em inglês) | 98 |
| independentes 1 e 2 | relatos de quem não viu o mapa (dois autores) | 61 + 61 |
| piloto | 40 relatos do piloto da prova 2 ([rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md)) | 40 |

"Prova + régua" são os 134 casos de `dev`, calibração e régua (74
emergências, 58 leves e 2 INCERTO). **O lote `teste` da prova nunca foi usado.**

**Métricas.**
- **Emergência perdida:** uma emergência respondida como NAO_EMERGENCIA ou
  INCERTO.
- **Falso alarme:** um caso leve respondido como EMERGENCIA.
- **Acerto geral:** a resposta igual à esperada.
- **Comparações:** sempre pareadas, caso a caso, com o teste exato de McNemar
  só nas emergências ("só A perde × só B perde"). Diferença sem
  significância é chamada assim.

**Atendentes e parâmetros.**
- **`llama3.2:3b`** (digest `a80c4f17`, o das linhas de base) e **`qwen3:8b`**
  com `think=False`, no Ollama 0.34.3 nativo, na RTX 4060.
- **`gemini-3.5-flash-lite`**, com um cliente próprio que usa a mesma
  interface do `LLMClient`. Ele **nunca troca de modelo**: falha vira ERRO, e
  o caso é refeito depois.
- **Prompt e opções:** o mesmo prompt `v1_grounded` e o mesmo esquema de
  saída do projeto, com as opções padrão de `fceab20` (temperatura 0,
  semente 42, `num_ctx` 4096, `num_predict` 600).
- **Latência:** o tempo da chamada ao modelo. No Gemini, sem a espera entre
  chamadas que o executor impõe por causa da cota.

**Integridade.** São cerca de 17.900 linhas de resultado. Duas delas são falha
técnica, em que o modelo devolveu resposta vazia ou inválida e o pipeline a
converteu no INCERTO de segurança. Elas estão contadas como perda, como o
sistema faria com o tutor, e cada evidência diz onde aparecem. Uma queda de
energia na noite de 24/09 estragou um único bloco de 61 chamadas, que foi
descartado e refeito. Todos os outros arquivos foram conferidos.

## O que mudou no repositório

| Arquivo | O que é |
|---|---|
| esta evidência | |
| `data/evaluation/cited/20260923-*_autopsia_*` | as 4 rodadas do `run_evaluation.py` no conjunto antigo (sem RAG, RAG direto, pipeline completo sem Gemini e o A/B do prompt), promovidas com `report_evaluation.py cite` |
| `data/evaluation/prova_runs/20260923-*_autopsia_*` | as 8 rodadas do runner da prova (`dev`, calibração e régua, com e sem RAG, e o A/B do prompt) |
| `data/retrieval/cited/20260923-175254_autopsia_candidata_3481` | a régua de recuperação na candidata |
| `data/diagnostico/relatos_independentes.csv` e `README.md` | os 122 relatos de quem não viu o mapa, com a origem, a autoria, a composição e o aviso de que **não são prova** (o piloto da prova 2 entra na [rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md)) |
| `data/evaluation/autopsia2/` | `resultados_por_caso.csv` (cada caso, nas 106 combinações de condição e atendente citadas nas rodadas 14 a 21), `justificativas_citadas.csv` (o texto das justificativas que as evidências leem), `busca/` e `tradutor/` (as buscas e as saídas do tradutor, caso a caso) e `README.md` (o executor, as condições, como recontar qualquer número) |

Nenhum arquivo de código mudou. Suítes em `fceab20`, no Windows: backend 242
e scripts 197 testes, todos passando.

## Observações

**1. O texto do prompt mudou sem versão nova.** Em 20/09 o texto do
`v1_grounded` foi editado no lugar, e o hash dos prompts passou de `d04ad0f7`
para `a1e9cd51`. Todas as rodadas citadas até 12/09 usam o primeiro. O A/B
pelo runner, que só troca o texto das instruções, dá:
- conjunto antigo: 85 → 86 acertos, 5 casos divergem;
- `dev`: 43 → 43, 2 divergem;
- calibração: 15 → 15, nenhum diverge.

O efeito é de ±1 caso por conjunto. O texto novo trocou três emergências
perdidas por dois falsos alarmes, o lado mais seguro. O problema é de
rastreabilidade, não de efeito.

**2. Fim de linha no Windows.** O Git converte `.txt` e `.csv` para CRLF no
checkout, e o `.gitattributes` só protege os PDFs. Os hashes são calculados
sobre os bytes crus. Com isso:
- 10 fontes falham na verificação de hash;
- o `sync_retrieval_terms.py --check` falha no Windows e passa no Linux;
- o conjunto de fontes de uma máquina Windows sai diferente do de uma Linux.

É uma linha: `*.txt -text` e `*.csv -text` no `.gitattributes` ([B-59](../backlog.md#b-59)).

**3. Clone limpo.** Seguindo o README, o passo 4 (perfil `curated`) recusa os
67 documentos, todos marcados `experimental_only`. O retrato versionado do
Chroma está num caminho que o backend não lê ([B-57](../backlog.md#b-57)).
Nenhum número com RAG se reproduz sem passos manuais.

**4. O retrato do sistema não diz quem respondeu à consulta.** O
`/health/fingerprint` não registra:
- o provedor da etapa de consulta nem o modelo do Gemini;
- as chaves do tradutor;
- o vocabulário do roteador;
- as constantes do reranker.

Duas máquinas com o mesmo manifesto podem medir sistemas diferentes. A
implementação da autópsia leva isso ao retrato.

**5. O runner da prova e o do B2 contam INCERTO de jeitos diferentes.** O
`run_map_triage_eval.py` fixa o tradutor desligado nos dois modos e não
confere o hash da base. Para a ablação final, as métricas precisam de uma
semântica só ([B-60](../backlog.md#b-60)).

**6. A etapa de consulta local é rápida na GPU.** Com reescrita e
multi-query, e sem HyDE, ela leva 0,92 s de mediana nos 98 casos antigos,
nesta máquina. Comparações de latência entre Gemini e Ollama precisam ser
feitas no mesmo tipo de máquina; em CPU, o Ollama leva dezenas de segundos.

## Deixado para depois

- **Fim de linha CRLF** ([B-59](../backlog.md#b-59)): correção de uma linha,
  fora do caminho desta autópsia.
- **Uma semântica só de métrica entre os runners** ([B-60](../backlog.md#b-60)):
  só importa na ablação final.
- **A base acadêmica** não é consertada: as rodadas seguintes mostram que o
  problema não se resolve dentro dela (nem com a busca perfeita; ver a
  [rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md)). Ela fica como
  braço da ablação e como fonte das citações.

## Próximo passo

A pergunta que os resultados 3 e 4 deixam: se a busca entregasse o trecho
certo, o atendente acertaria? É a [rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md):
o que o atendente deve ler.
