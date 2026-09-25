# Prova 2: por que uma prova nova, como ela é, e o piloto

**Data:** 24/09/2026 (madrugada e noite; escrita em 25/09 a partir do registro
da autópsia) · **Trilho:** B2, para o instrumento do time · **Rodada:** 20 ·
**Commits:** este

> Rodada de **construção de instrumento e experimento**. Nada no sistema
> mudou. Mede os limites da prova 1, especifica a prova 2 e testa, com um
> piloto de 40 relatos, se o jeito proposto de escrevê-la funciona. A prova 2
> completa é gerada depois desta rodada, e os rótulos dela passam pela
> validação de veterinários antes de qualquer uso. O método está na
> [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md#como-medimos-vale-para-as-rodadas-14-a-21).

## O que foi feito

1. **Os limites da prova 1**, medidos com implementação própria:
   - o vazamento (as palavras entregam a classe?), com a divisão aleatória e
     com a divisão por assunto;
   - a regra do "mas";
   - a conta de poder estatístico: quantos casos são precisos para ver as
     diferenças que importam.
2. **Os instrumentos que a autópsia criou**, reunidos aqui como parte da
   prova: os relatos de quem não viu o mapa e as quatro frases de tom
   ([rodadas 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md) e
   [18](2026-09-24-19-atendente-llama-qwen-gemini.md)).
3. **A especificação da prova 2**: composição, autoria, divisão,
   congelamento e rótulo.
4. **O piloto**: 40 relatos escritos por duas instâncias isoladas de IA
   (Claude), que antes pesquisaram como tutores descrevem cada quadro. Foi
   medido do mesmo jeito que os relatos independentes, para dizer se dá para
   escalar para os 330.

## Por quê

Três rodadas desta autópsia esbarraram no mesmo limite: **a prova 1 é
otimista e pequena**.
- **A prova e as fichas saem do mesmo mapa.** Quem escreveu os relatos tinha os
  sinais do mapa na mão. A busca acerta a ficha em 1º em ~80% dos casos da
  prova e em ~50% dos relatos de quem não viu o mapa
  ([rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md)).
- **A prova escolheria a arquitetura errada.** Nela, a porta de confiança
  empata com as 3 fichas (2 × 3); nos relatos de quem não viu o mapa, as 3
  fichas ganham com folga (15 × 1).
- **A prova quase não tem o risco central do produto**, o tutor que conta
  uma emergência com calma: são 3 casos. É esse o caso em que o atendente de
  hoje falha (1 de 38; [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md)).
- **74 emergências só enxergam diferenças grandes.**

Sem uma prova nova, qualquer número com fichas é otimista, e o TCC não tem
como comparar dois atendentes bons entre si.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **Quem escreve não vê o mapa, as fichas nem a prova 1**. Recebe só o quadro (nome leigo), a espécie, a gravidade e o tom | É o que separa medir o sistema de medir o vocabulário que ele compartilha com a prova |
| 2 | **330 relatos**: 190 emergências, 115 não emergências, 25 especiais | Poder para comparar atendentes bons entre si (resultado 1) |
| 3 | **O tom é variável controlada**: em cada emergência, 2 contadas com calma ou minimizando; em cada leve, 2 aflitas | O risco real de uso, que a prova 1 quase não tem |
| 4 | **Divisão por assunto e congelamento por hash** antes de qualquer rodada. Um relato de cada quadro vai para a calibração (66) e os outros 264 formam o teste, rodado **uma vez**, pela configuração final | Sem assunto em comum entre os lotes, e sem ajustar nada no conjunto que dá o número final |
| 5 | **O rótulo é validado por veterinários** que não escreveram o caso. Onde o veterinário discordar do mapa, vale o veterinário, e o mapa é revisto | Hoje o rótulo é a urgência da linha do mapa, e a autópsia achou rótulos discutíveis (observação 4) |
| 6 | **Decisão do João (25/09): só relatos escritos por IA**, por agentes isolados, sem âncora humana; a autoria é dita uma vez, e a validação dos veterinários, ao lado | Uma âncora humana de 30 a 60 relatos era a recomendação do piloto. O João decidiu não fazê-la |
| 7 | **O lote teste da prova 1 é congelado e guardado**, sem uso | Fica como o instrumento histórico, com a sua ressalva |

## Resultado esperado

Escrito antes de medir:

| Teste | Critério |
|---|---|
| Mais frases de tom (01h50) | Se alguma frase derrubar 20% ou mais das emergências de um atendente **mesmo com ficha**, a prova 2 precisa de uma seção de tom com várias frases |
| Piloto (19h17), "dá para escalar para os 330" se | **(a)** ≥ 90% dos relatos passarem na minha leitura; **(b)** o acerto em 1º com a ficha do mapa **não** ficar mais de 10 pontos acima do dos relatos independentes nos mesmos assuntos (a prova 1 fica ~30 acima); **(c)** um Naive Bayes treinado na prova 1 acertar ≤ 70% (na prova 1, 79%); **(d)** o ganho da ficha do Claude no piloto não passar do ganho nos independentes em mais de 10 pontos ("mesmo autor"). Com 40 relatos, é indício, não prova |

O vazamento e o poder não tiveram critério: eram medidas para dimensionar a
prova 2.

## Resultado obtido

### 1. A prova 1 carrega a classe nas palavras e tem pouco poder

**Vazamento**, nos 164 casos binários (a prova de 150 + a calibração de 18,
sem os INCERTO). **Nenhum sistema foi avaliado no lote teste**: aqui só entram
o texto, a classe e o assunto.

| Medida (Naive Bayes, validação cruzada 5 × 20) | Acerto |
|---|---|
| divisão aleatória (o assunto pode repetir entre os lotes) | 0,91 (0,86 a 0,94) |
| **divisão por assunto** (nenhum assunto em comum) | **0,79** (0,74 a 0,85) |
| regra "tem 'mas' ⇒ não emergência" | 0,77 (126 de 164) |

- **Cerca de 12 pontos do acerto fácil vêm de assunto repetido** entre os
  lotes: são 62 assuntos, quase todos com 2 a 5 casos.
- **Mesmo sem assunto em comum, só as palavras acertam 79%.** Os relatos
  carregam a classe na superfície.
- **O "mas" marca o caso leve:** 50 dos 60 relatos com "mas" são leves.

A prova 2 precisa de relatos em que a classe não se adivinha pelas palavras:
emergência contada com calma, caso leve contado com aflição.

**Poder estatístico** (McNemar exato, 80% de poder, alfa de 5%; "aninhado"
quer dizer que as perdas do sistema melhor estão todas dentro das do pior, o
caso mais favorável):

| Diferença de emergências perdidas | Emergências necessárias (aninhado / independente) |
|---|---|
| 19% → 0% (llama sem contexto → com a ficha) | 40 / 50 |
| 10% → 2% | 100 / 150 |
| 8% → 0% (qwen sem contexto → com a ficha) | 100 / 100 |
| 5% → 1% | 200 / 300 |
| 3% → 0% | 300 / 300 |

Com "0 emergências perdidas em n", o limite superior do IC 95% da taxa real é:
- n = 50: 5,8%;
- n = 74: **4,0%**;
- n = 150: 2,0%;
- n = 190: 1,6%;
- n = 300: 1,0%.

**Com as 74 emergências da prova + régua, "0 perdas" ainda pode esconder até
4% de erro real**, e só diferenças grandes aparecem, como a do llama com e sem
ficha. Para comparar atendentes bons entre si (qwen × Gemini, os dois perto de
0 a 8%), são precisas de 150 a 300 emergências.

**A busca desaba quando o autor não viu o mapa.** Ficha certa em 1º lugar,
bge-m3, fichas do mapa:

| Lote | 1º lugar |
|---|---|
| `dev` (relatos escritos com o mapa na mão) | 0,83 |
| régua (idem) | 0,79 |
| autor independente 1 (`gemma-4-31b-it`) | **0,56** |
| autor independente 2 (`gemini-3.1-flash-lite`) | **0,47** |

**O tom depende pouco da frase, e o llama cai com qualquer uma**: de 36% a 64%
das emergências perdidas, 43% mesmo com ficha. **Pelo critério das 01h50, a
prova 2 precisa de uma seção de tom com várias frases.** Os detalhes estão na
[rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md#2-o-tom-não-depende-da-frase-para-o-llama).

### 2. A especificação da prova 2

**Composição: 330 relatos.**

| Parte | Quantos | Como |
|---|---|---|
| Emergências | **190** | 5 por quadro de emergência do mapa (38 × 5): 2 contadas com calma ou minimizando, 1 aflita, 1 neutra, 1 parecida com a gêmea leve |
| Não emergências | **115** | 5 por quadro leve (23 × 5): 2 aflitas ou exageradas, 2 neutras, 1 parecida com a gêmea grave |
| Casos especiais | **25** | 10 com informação insuficiente (a resposta certa é INCERTO); 8 quadros clínicos reais que o mapa não cobre; 7 perguntas não clínicas |

Com 190 emergências, "0 perdidas" limita o erro real a 1,6%, e uma diferença
de 10% para 2% entre dois atendentes aparece com folga. Uma de 5% para 1% fica
no limite.

**Autoria.**
- Os relatos são escritos por **agentes de IA isolados**, que não veem o mapa,
  as fichas nem a prova 1. Recebem o quadro em linguagem leiga, a espécie, a
  gravidade, o tom e uma "persona" de tutor (idade, jeito de escrever, erros de
  digitação, tamanho).
- Antes de escrever, cada agente pesquisa como tutores descrevem o quadro e
  anota um caderno de linguagem, com as fontes. Os relatos são escritos do
  zero a partir desses padrões, sem cópia.

**Divisão e congelamento.**
- Por assunto: um relato de cada quadro vai para a calibração (66) e os outros
  264 formam o teste.
- O hash do arquivo é registrado antes da primeira rodada, e o teste roda uma
  vez por configuração final.
- O vazamento é conferido antes de congelar: um Naive Bayes só com palavras
  deve ficar perto do acaso entre os lotes.

**Rótulo.** Cada caso é validado por um veterinário que não o escreveu. São
cerca de 30 s por relato, umas 3 horas para os 330, divididas entre dois ou
três especialistas.

**O que medir sempre:**
- emergências perdidas, com o IC 95%;
- falsos alarmes e INCERTO;
- o tom, pareado (o mesmo caso com e sem a frase);
- a busca separada: ficha certa em 1º, ficha certa no prompt, ficha errada no
  prompt.

### 3. O piloto: como foi escrito

**Desenho.** Foram 20 assuntos, 2 relatos cada, 40 no total: 24 emergências e
16 leves. Eles cobrem as etapas 1 e 2, as duas espécies e os pares de gêmeas:

| | Etapa 1 | Etapa 2 |
|---|---|---|
| Emergências (12) | obstrução uretral, convulsão, dificuldade respiratória, piometra, raticida anticoagulante, permetrina em gato | corpo estranho, insuficiência cardíaca, distocia, cinomose neurológica, sapo, tromboembolismo felino |
| Não emergências (8) | cistite ou xixi fora do lugar, cio normal, tremor sem convulsão, espirro e coriza leves | tosse dos canis leve, parto normal, carrapato sem sinais, ferida pequena |

Em cada emergência há um relato calmo ou minimizando e um neutro ou aflito. Em
cada leve, um aflito ou exagerado e um neutro. Isso dá 12 emergências calmas,
6 aflitas e 6 neutras; 8 leves aflitos e 8 neutros.

**Autores.** Duas instâncias do Claude, 10 assuntos cada, que **não viram** o
mapa, as fichas, a prova 1 nem os relatos independentes.

**Como se capacitaram.** Cada autor pesquisou na internet como tutores
descrevem cada quadro e anotou um caderno de linguagem por assunto:
- as palavras que o tutor usa;
- o que ele nota primeiro, o que minimiza e o que omite;
- os endereços consultados.

As fontes:
- **Quantas:** de 4 a 9 por quadro (autor A: 50 no total, 23 em português;
  autor B: 62, 43 em português).
- **O que funcionou:** comentários de leitores em sites de tutores, páginas
  abertas de pergunta e resposta a veterinários, comentários em artigos
  técnicos e relatos de caso brasileiros que registram a queixa do tutor.
- **O que não funcionou:** as redes e fóruns que recusam leitura automática
  ou pedem verificação anti-robô, que os autores não contornaram. Fala de
  tutor brasileiro é rara na busca. Em "carrapato sem sinais" e "ferida
  pequena" quase não há fala de tutor, e o autor marcou as expressões que são
  formulação dele.

**Cópia e isolamento.**
- O autor B conferiu as 54 páginas que citou, e nenhum relato repete 6 ou
  mais palavras seguidas de uma fonte.
- Os palpites de diagnóstico do próprio tutor ficaram em 4 por autor (o
  limite era 1 em 5), quase todos errados de propósito: "intestino preso",
  "gripe", "caiu e machucou a coluna".
- Nenhum dos dois abriu o mapa, as fichas ou a prova.

**A minha leitura dos 40: todos passam.**
- **Personas variadas de verdade:** regionalismos ("égua", "bah tchê", "uai",
  "mainha"), digitação de celular, CAPS LOCK, idosos.
- **As emergências calmas são boas e variadas:** o tutor acha que é intestino
  preso (obstrução), friagem (cinomose), "caiu e machucou a coluna"
  (tromboembolismo), "cio voltando" (piometra), "primeira cria demora"
  (distocia).
- **Ressalvas:** alguns relatos neutros saíram "de livro" ("almofadinhas
  ásperas" da cinomose; frequência respiratória contada: 64 por minuto). Dois
  têm o assunto ambíguo no rótulo: pA20 ("respira mal, tem sopro, tosse", que
  pode ser insuficiência cardíaca) e pB20 (arranhão de briga de gato, que pode
  ser a ferida de briga). A classe não muda em nenhum dos dois.

### 4. O piloto: as medidas

**Busca** (bge-m3), ficha certa em 1º / entre as 3 primeiras, em %:

| | Piloto (40) | Independentes, mesmos 20 assuntos (40) | Independentes, todos (122) | Prova + régua (129) |
|---|---|---|---|---|
| ficha do mapa | **45,0** / 67,5 | 55,0 / 75,0 | 51,6 / 76,2 | 80,6 / 93,0 |
| ficha do Claude | 40,0 / **80,0** | 62,5 / 72,5 | 60,7 / 77,0 | 82,9 / 95,3 |
| ganho do Claude | −5,0 / +12,5 | +7,5 / −2,5 | +9,0 / +0,8 | +2,3 / +2,3 |

- **O piloto não é "fácil": é o lote mais difícil de todos para a busca.** Com
  a ficha do mapa, o 1º lugar fica em 45, abaixo até dos independentes nos
  mesmos assuntos (55). A prova 1 fica em 81. **Critério (b): passa com
  folga.**
- **"Mesmo autor":** no 1º lugar, a ficha do Claude **não** ganha mais no
  piloto do que nos independentes (−5 × +7,5). Entre os 3 primeiros, ganha
  mais (+12,5 × −2,5): são 15 pontos, 6 relatos. **Critério (d): passa no 1º
  lugar, não passa nos 3 primeiros.** Com 40 relatos, a margem de ruído é de
  ~10 pontos, e isso fica como **ponto de atenção**, não como veredito.

**Palavras em comum com a ficha certa** (fração das palavras de conteúdo do
relato que aparecem na ficha do assunto):

| | Piloto | Independentes, mesmos assuntos |
|---|---|---|
| ficha do mapa | **0,08** | 0,13 |
| ficha do Claude | **0,23** | 0,33 |

O piloto divide **menos** vocabulário com as fichas, as do mapa e as do
Claude, do que os relatos independentes. Não há sinal de que os autores do
piloto "falem como as fichas". O vocabulário é mais coloquial e regional.

**Pistas de superfície.** Um Naive Bayes treinado só com as palavras da prova 1
(132 relatos) tenta adivinhar a classe; chutar a classe mais comum dá 60%:

| | Naive Bayes | Regra "tem 'mas' ⇒ leve" |
|---|---|---|
| Piloto | 77,5% | **67,5%** |
| Independentes, mesmos assuntos | 77,5% | 47,5% |

- **Critério (c) (Naive Bayes ≤ 70%): não passa.** Mas os independentes também
  dão 77,5%. Boa parte do que o Naive Bayes aprende é vocabulário clínico
  legítimo ("sangue", "não consegue respirar", "convulsão"), e a classe
  **deve** estar nos sinais. **O limiar de 70% foi mal calibrado por mim.**
- **A pista de estilo que sobrou é o "mas".** Os autores do piloto usaram "mas"
  nos casos leves mais do que os independentes ("mas eu tô em pânico", "mas
  segue latindo"). É uma correção de instrução para a versão completa.

**Os atendentes no piloto** (emergências perdidas de 24 · falsos alarmes de
16):

| O que o atendente recebe | qwen3:8b | gemini-3.5-flash-lite |
|---|---|---|
| nada | 4 · 4 | 1 · 2 |
| 3 fichas do mapa | 0 · 4 | 0 · 3 |
| 3 fichas do Claude | 2 · 2 | 0 · 1 |
| busca na ficha do Claude, leitura na do mapa | 0 · 3 | 0 · 3 |

- **O piloto reproduz o que os relatos independentes mostraram.** Sem
  contexto, o qwen perde as emergências contadas com calma (as 4 perdas são
  calmas) e dá falso alarme nos casos leves contados com aflição (os 4 são
  aflitos). O Gemini quase não cai. Com as 3 fichas, o qwen alcança o Gemini.
  E o piloto também reproduz o efeito da ficha do Claude no qwen: 2 perdas,
  as duas calmas.
- **A única emergência que o Gemini perdeu sem contexto (pA01) é falha
  técnica.** A resposta veio vazia depois de 2 tentativas, e o pipeline a
  converteu no INCERTO de segurança. Está contada, como o sistema faria.
- **O piloto mede as mesmas coisas que os independentes, na mesma direção**, e
  é isso que se espera de uma prova que funciona.

### 5. Veredito do piloto

| Critério (escrito antes) | Resultado |
|---|---|
| (a) ≥ 90% passam na minha leitura | **passa** (40 de 40) |
| (b) a busca não fica mais fácil que nos independentes | **passa** com folga (45 × 55 no 1º lugar; a prova 1 fica em 81) |
| (c) Naive Bayes ≤ 70% | **não passa** (77,5%), mas os independentes também dão 77,5%: o limiar estava mal calibrado. A pista de estilo real é o "mas" nos casos leves (67,5% × 47,5%), a corrigir na instrução |
| (d) sem efeito de "mesmo autor" | **passa no 1º lugar, não passa nos 3 primeiros** (+12,5 × −2,5); ponto de atenção, com n = 40 |

**É possível escrever a prova 2 assim.** O piloto indica que a prova escrita
desse jeito é **mais exigente** que a prova 1, não menos. Para a versão
completa, com as correções que o piloto ensinou:
1. equilibrar o "mas" entre as duas classes, e outras marcas de estilo, na
   instrução dos autores (a meta é "mas" em ~40% de cada classe);
2. menos relatos "de livro" nos neutros: pedir o tutor que não sabe o nome do
   sinal;
3. no máximo 1 palpite de diagnóstico do tutor em cada 5 relatos, e quatro
   famílias de frase calma (minimização, adiamento, bem-estar, "mas come
   normal"), além de relatos calmos sem frase pronta;
4. o rótulo validado pelos veterinários antes de qualquer uso.

A âncora humana que o piloto recomendava (30 a 60 relatos escritos por
pessoas) **não será feita, por decisão do João**. O risco que ela mediria, o
"mesmo autor" no top 3, é medido de novo na prova 2 inteira, que tem n para
isso (observação 2).

## O que mudou no repositório

| Arquivo | O que é |
|---|---|
| esta evidência | |
| `data/diagnostico/piloto_prova2.csv` | os 40 relatos do piloto: id, texto, espécie, classe, assunto, tom, persona, autor. **Não são prova:** serviram para decidir como escrever a prova 2 |
| `data/diagnostico/piloto_prova2/cadernos/<topic>.md` (20) | os cadernos de linguagem, com as fontes consultadas. As expressões são sínteses, não citações |
| `data/evaluation/autopsia2/resultados_por_caso.csv` (versionado na rodada 14) | as condições do piloto: `sem_rag`, `ctxarq_bge_fichasp_top3`, `ctxarq_bge_fichasclp_top3`, `ctxarq_bgecl_leitura_mapa_top3`, `ctxarq_bgecl_leitura_curta_top3` |

## Observações

**1. A prova 1 não é descartada: é redefinida.** Os lotes `dev` e calibração
continuam como conjuntos de desenvolvimento, e o lote teste fica congelado e
guardado. O que ela não pode é dar o número final do TCC. Quem mede a
arquitetura é a prova 2.

**2. O "mesmo autor", na prova 2.** A mesma família de modelo escreveu as
fichas de busca ([rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)) e o
piloto. O isolamento funciona no 1º lugar e nas palavras em comum, mas o top 3
ficou 15 pontos acima no piloto. Sem âncora humana, a conferência na prova 2
completa é repetir, com 330 relatos, as duas medidas do piloto: as palavras em
comum com as fichas e o ganho da ficha de busca sobre a do mapa, comparados
com os relatos independentes.

**3. O piloto é pequeno** (24 emergências). Ele serviu para decidir **como**
escrever a prova, e como terceiro conjunto de conferência na
[rodada 19](2026-09-24-20-fichas-em-duas-camadas.md#5-as-duas-correções-e-o-desenho-que-fica),
porque nenhuma decisão o tinha usado até ali. Não serve para dar número.

**4. Rótulos discutíveis nos relatos independentes.** São eles: "pão com
passas" (marcado leve), "comeu um pedaço de chocolate" (marcado leve),
"inchaço enorme na cara" (marcado leve), "rosto meio inchado, picada de algum
bicho" (marcado como cobra). Mostram por que o rótulo precisa de veterinário:
o autor escolhe o quadro, mas quem decide a urgência do relato **escrito** é
quem o lê.

## Deixado para depois

- **A prova 2 inteira** ([B-63](../backlog.md#b-63)). São seis etapas:
  - a geração, com as correções do piloto;
  - a conferência completa (composição, duplicatas, "mas" por classe,
    palpites, palavras em comum com as fichas);
  - a planilha para os veterinários validarem sem ver o rótulo;
  - a divisão por assunto;
  - o congelamento;
  - o README com a autoria e a validação.
  
  A geração é o primeiro passo depois desta rodada. Nada disso roda no lote
  teste antes do congelamento.

## Próximo passo

A [rodada 21](2026-09-24-22-arquitetura-proposta-contra-a-de-hoje.md) junta
tudo: o sistema proposto contra o de hoje, nos mesmos relatos.
