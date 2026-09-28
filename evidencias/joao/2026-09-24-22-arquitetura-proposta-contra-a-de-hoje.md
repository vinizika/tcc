# O sistema proposto contra o de hoje, nos mesmos relatos

**Data:** 24/09/2026 (22h30; escrita em 25/09 a partir do registro da autópsia)
· **Trilho:** B2, olhando o sistema inteiro · **Rodada:** 21 · **Commits:** este

> Rodada de **síntese**. Junta as decisões das rodadas 14 a 20 e põe o sistema
> proposto inteiro contra o de hoje, **nos mesmos relatos**. O único teste novo
> é o que faltava para a comparação ser igual com igual: o sistema de hoje nos
> relatos de quem não viu o mapa e no teste de tom (22h33). O número definitivo
> vem de dois lugares depois desta rodada. Um é a réplica pelo runner do
> repositório, na implementação; o outro, a prova 2. O método está na
> [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md#como-medimos-vale-para-as-rodadas-14-a-21).

## O que foi feito

1. O sistema proposto, peça por peça, com a rodada que justifica cada decisão.
2. A comparação completa, hoje × proposto, com os dois atendentes do proposto
   e com o tradutor ligado e desligado no de hoje.
3. O que ainda não se sabe.
4. A lista do que muda no código e do que depende de validação clínica, sem
   donos: a implementação (rodadas 23 a 30) é a próxima etapa.

## Por quê

Depois de dois dias de testes, o João pediu, com razão, para fechar: "estou
sentindo que estamos fazendo muitos testes, mas não estamos chegando numa
conclusão". Esta rodada é a conclusão. Os porquês estão nas rodadas 14 a 20;
aqui fica o que se faz, e o tamanho do ganho.

## Decisões desta rodada

| Peça | Hoje (`fceab20`) | Proposto | Onde está o porquê |
|---|---|---|---|
| O que o atendente lê | trechos de artigos acadêmicos, 96% em inglês | **a ficha de leitura** do quadro: a ficha curta do mapa, validada, com a conduta fixa pela urgência | [rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md) |
| O que a busca procura | os mesmos trechos | **a ficha de busca**: a ficha escrita por IA, com as variações de como o tutor conta e a origem de cada frase | [rodada 19](2026-09-24-20-fichas-em-duas-camadas.md) |
| Embedding | MiniLM multilíngue (384 dim.) | **bge-m3** (1024 dim.) | [rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md) |
| Porta de entrada | nota ≥ 0,72, com o piso de 0,721 pela rota | **as 3 fichas mais próximas, sempre**, sem porta, sem roteador e sem reranker no caminho padrão | [rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md) |
| Âncoras | vetam documentos sem as palavras da lista | **fora** | [rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md) |
| Tradutor (reescrita, multi-query, HyDE) | ligado | **desligado por padrão**; continua no código como braço da ablação | [rodada 17](2026-09-24-18-tradutor-desligado.md) |
| Atendente | `llama3.2:3b` | **`gemini-3.5-flash-lite`** (decisão de produto do João); `qwen3:8b` e `llama3.2:3b` como opções | [rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md) |
| Troca de modelo | silenciosa, na etapa de consulta | **nunca em silêncio**; a resposta registra provedor e modelo | [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md), [18](2026-09-24-19-atendente-llama-qwen-gemini.md) |
| Citação ao tutor | o título genérico do documento | **a ficha usada e o documento aprovado por trás dela, com o título real** | [rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md#6-os-títulos-genéricos) |
| Instrumento final | prova 1 | **prova 2**: 330 relatos, agentes isolados, rótulos validados por veterinários | [rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md) |
| Ablação completa | — | **só com o projeto completo** (depois de CoT e Self-Refine), por decisão do João | [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md) |

## Resultado esperado

Esta rodada **não tem critério próprio**: ela soma decisões que já tinham o
seu. A medição das 22h33 foi feita para comparar igual com igual. O que se
esperava, pela [rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md), era
o sistema de hoje errar perto de metade dos relatos de quem não viu o mapa,
porque 116 de 122 deles chegam ao atendente sem nenhum trecho.

## Resultado obtido

### 1. O sistema proposto, do relato à resposta

1. **O tutor escreve** (ou fala, e a voz vira texto).
2. **O relato vai cru para a busca.** Reescrita, multi-query e HyDE ficam
   desligados.
3. **A busca compara o relato com as 61 fichas de busca** usando o bge-m3, e
   pega as **3 mais parecidas**, sempre.
4. **O atendente recebe, para cada uma das 3, a ficha de leitura** do mesmo
   quadro (a ficha do mapa).
5. **O atendente responde** EMERGÊNCIA, NÃO EMERGÊNCIA ou INCERTO, com a
   justificativa, e a resposta cita a ficha e o documento aprovado por trás
   dela.

**Um exemplo real** (relato i37, de autor independente, contado com calma):

> "Oi, minha cadela teve filhotes semana passada e agora começou a tremer uns
> músculos da perna e tá meio durinha. Acho que é só cansaço de amamentar, né?
> Amanhã eu vejo se ela melhora."

| Sistema | O que chega ao atendente | Resposta | Justificativa |
|---|---|---|---|
| hoje (llama, artigos) | nada (a porta barra) | NÃO EMERGÊNCIA | "Sinais de cansaço e possível dor, mas não há risco imediato à vida." |
| qwen, sem contexto | nada | NÃO EMERGÊNCIA | "Sinais leves e possíveis de monitorar em casa." |
| **proposto, Gemini** | eclâmpsia, distocia, artrose | **EMERGÊNCIA** | "Tremores e rigidez em cadela amamentando indicam quadro grave que requer atendimento veterinário imediato." |
| **proposto, qwen** | eclâmpsia, distocia, artrose | **EMERGÊNCIA** | "Tremores e rigidez podem indicar eclampsia puerperal, que é uma emergência." |

### 2. Hoje × proposto, nos mesmos relatos

"Hoje" é o sistema do repositório como está: `llama3.2:3b`, os 3.481 trechos
acadêmicos, o MiniLM e a porta de 0,72. Ele aparece com o tradutor desligado
(o relato cru) e ligado (reescrita, multi-query e HyDE gerados pelo llama, que
é o que roda sem a chave do Gemini). Emergências perdidas · falsos alarmes ·
acerto geral:

| | Hoje, tradutor desligado | Hoje, tradutor ligado | **Proposto, Gemini** | Proposto, qwen |
|---|---|---|---|---|
| **Prova + régua** (casos do time; 74 · 58) | 15 · 4 · 115/134 | 8 · 3 · 121/134 | **2 · 1 · 129/134** | 2 · 1 · 130/134 |
| **Relatos de quem não viu o mapa** (76 · 46) | 40 · 22 · 60/122 | 37 · 23 · 62/122 | **6 · 3 · 109/122** | 5 · 7 · 109/122 |
| emergências contadas **com calma**, acertadas (38) | **1** | 2 | **33** | 33 |
| **Teste de tom** (74 emergências + "mas fora isso come e brinca normal"), perdidas | **46** | — | **3** | 4 |
| **Piloto da prova 2** (24 · 16) | — | — | 0 · 3 | 0 · 3 |
| **Relatos de quem não viu o mapa sem nenhum contexto no prompt** | **116 de 122** | 17 de 122 | 0 de 122 (a ficha certa está entre as 3 em 94) | idem |
| Tempo por caso (mediana) | 1,1 s | + a etapa de consulta | 1,1 s (API) + 0,1 s de busca | 2,6 s (com placa de vídeo) |

Em porcentagem, nos relatos de quem não viu o mapa, o sistema de hoje deixa
passar **53%** das emergências e acerta **49%** dos casos (cara ou coroa). O
proposto, com o Gemini, deixa passar **8%** e acerta **89%**.

**Pareados** (emergências, "só o de hoje perde × só o proposto perde"):

| Hoje × proposto (Gemini) | Prova + régua | Relatos de quem não viu o mapa | Tom |
|---|---|---|---|
| hoje com o tradutor desligado | **15 × 2 (p = 0,002)** | **35 × 1 (p < 0,0001)** | **43 × 0 (p < 0,0001)** |
| hoje com o tradutor ligado | 8 × 2 (p = 0,11) | **32 × 1 (p < 0,0001)** | — |

Com o qwen no lugar do Gemini, os pareados são praticamente os mesmos: 15 × 2,
35 × 0 e 42 × 0 contra o de hoje sem tradutor; 8 × 2 e 32 × 0 contra o de hoje
com tradutor.

**A leitura, sem exagero:**
- **Nos relatos de quem não viu o mapa, a diferença é enorme e não é sorte**:
  de 40 para 6 emergências perdidas, 35 × 1 no pareado. E eles são a melhor
  aproximação que temos do tutor de verdade.
- **Na prova + régua, contra o sistema de hoje com o tradutor ligado, a
  diferença não é significativa** (8 × 2, p = 0,11). A prova foi escrita com o
  vocabulário do mapa. Nela, o tradutor ajuda o llama a furar a porta, e o
  próprio llama já acerta boa parte sozinho. **É o limite da prova 1**, e o
  motivo de a prova 2 existir.
- **No tom, o sistema de hoje perde 46 das 74 emergências; o proposto, 3.**

### 3. Por que fichas, e por que sem tradutor

A pergunta que o João pediu para deixar respondida com teste. Com o qwen, o
atendente que foi rodado nas quatro células
([rodada 17](2026-09-24-18-tradutor-desligado.md#5-na-decisão-a-tabela-22)):

| qwen3:8b | Prova + régua | Relatos de quem não viu o mapa |
|---|---|---|
| artigos, tradutor ligado | 11 · 1 | 19 · 5 |
| artigos, tradutor desligado | 7 · 0 | 21 · 9 |
| fichas, tradutor ligado | 6 · 1 | 8 · 8 |
| **fichas, tradutor desligado** | **2 · 1** | **5 · 7** |

**As fichas com o tradutor desligado são a melhor célula nos dois conjuntos.**
Contra as outras três, os pareados das emergências são:

| Contra | Prova + régua | Independentes |
|---|---|---|
| artigos com tradutor | **9 × 0 (p = 0,004)** | **14 × 0 (p = 0,0001)** |
| artigos sem tradutor | 7 × 2 (p = 0,18) | **16 × 0 (p < 0,0001)** |
| fichas com tradutor | 4 × 0 (p = 0,125) | 3 × 0 (p = 0,25) |

Onde não há significância, a direção é a mesma, e o mecanismo está medido. Os
artigos quase não entram no prompt pela porta, e o que entra não diz quando
procurar o veterinário ([rodada 15](2026-09-23-16-fichas-no-lugar-dos-artigos.md)).
O tradutor tira o relato da língua do tutor, que é a língua das fichas: a
ficha certa em 1º cai de 107 para 84 em 129 ([rodada 17](2026-09-24-18-tradutor-desligado.md)).

### 4. O que ainda não se sabe

- **A prova + régua é otimista** para o proposto: as fichas e a prova saem do
  mesmo mapa. Os relatos de quem não viu o mapa são mais honestos, mas também
  são texto de IA, com rótulo tirado do mapa.
- **Os relatos independentes serviram de diagnóstico.** Várias decisões desta
  autópsia (as 3 fichas, as duas camadas) foram tomadas olhando para eles. O
  piloto (40) foi o único conjunto que nenhuma decisão tinha usado, e ele
  confirmou a direção, com n pequeno.
- **O ganho de segurança das duas camadas sobre a ficha do mapa sozinha não
  está provado** (5 × 7 em 76 no qwen, dentro do ruído). O que está provado é
  que ler a ficha escrita pela IA piora o modelo pequeno, e que separar busca e
  leitura não piora nada e melhora a busca.
- **O tradutor gerado pelo Gemini, nas fichas, não foi medido na decisão**,
  só na busca (e piorou).
- **Todos os números saíram de um executor próprio.** A implementação só está
  pronta quando o runner do repositório, pela API, reproduzir estes números
  dentro do ruído. A primeira tarefa depois do código é essa réplica.
- **O número do TCC é o da prova 2**, com os rótulos validados.

### 5. O que muda no código

Sem donos, porque a implementação é uma sequência só (rodadas 23 a 30):
1. **Fichas versionadas e geradas por script.** Os rascunhos de busca
   ([rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)) e o mapa geram o
   arquivo que o backend lê, por tópico, com o texto de busca, o texto de
   leitura, o título, a espécie, a urgência e as referências.
2. **A coleção das fichas no bge-m3**, com o embedding escolhido pela receita
   gravada no manifesto de cada coleção, para que a coleção acadêmica continue
   abrindo com o MiniLM (braço da ablação).
3. **Busca vetorial pura, as 3 mais próximas, sem porta.** A porta, o roteador
   e o reranker continuam como opção.
4. **O tradutor desligado por padrão**, religável por preset.
5. **A resposta.** Quatro mudanças, mais o retrato do sistema com tudo isso:
   - a citação com a ficha e o título real;
   - as fontes contando só o que o modelo viu (hoje, o bloco de contexto é
     cortado em 4.000 caracteres, e um trecho cortado continua listado como
     fonte);
   - a procedência (provedor, modelo, versão) na resposta;
   - o `think` do qwen configurável.
6. **O cliente do Gemini como atendente**, com o provedor selecionável, sem
   troca silenciosa, e o erro de cota explícito.
7. **Títulos reais** nas fichas de documento e **âncoras fora**.
8. **A réplica**: os números desta rodada, reproduzidos pelo runner, pela
   API, e promovidos a `cited/`.

### 6. O que depende de validação clínica

1. **As notas internas** que ficaram no "por que importa" de 11 fichas de
   leitura ("Caso b14", "não encontrei artigo primário, só um TCC") — é texto
   que o atendente lê.
2. **A etapa 2:** as 60 células vazias do mapa (sinais e discriminador), a
   partir dos rascunhos da folha de certificação.
3. **Os 5 conflitos** entre o mapa e o documento (convulsão, piometra,
   conjuntivite, cistite, obstrução uretral).
4. **Os rótulos da prova 2.**

Cada mudança de texto numa ficha de leitura é uma rodada medida, porque o
número do sistema depende desse texto.

### 7. O que não fazer

- Mais variações de ficha antes da prova 2.
- LightRAG: o mapa já é o grafo.
- Mais artigos acadêmicos na base.
- Uma regra de prompt contra o tom: foi testada e não muda nada.
- Fichas em inglês.

CoT e Self-Refine também ficam fora por enquanto, adiados por decisão do João
até o RAG estar consolidado.

## O que mudou no repositório

| Arquivo | O que é |
|---|---|
| esta evidência | |
| `data/evaluation/autopsia2/resultados_por_caso.csv` (versionado na rodada 14) | as condições desta rodada: `rag_full`, `ragtrad_full`, `cue_calmo_rag_full` (o de hoje, llama) e `ctxarq_bgecl_leitura_mapa_top3` com `cue_calmo_ctxarq_bgecl_leitura_mapa_top3` (o proposto, Gemini e qwen), nos seis lotes |

## Observações

**1. "Hoje" são dois sistemas.** Com a chave do Gemini, o tradutor é o Gemini;
sem ela, o llama. A autópsia mediu o de hoje sem a chave, que é como um clone
limpo roda. Com a chave, o tradutor é mais fiel e ajuda mais a busca na base
acadêmica ([rodada 17](2026-09-24-18-tradutor-desligado.md#3-o-efeito-na-busca)).
O sistema com o Gemini nas duas pontas (tradutor e atendente) não foi medido.

**2. O ganho está onde a prova 1 não enxerga.** Na prova + régua, o sistema de
hoje com o tradutor já perde "só" 8 emergências. Nos relatos de quem não viu o
mapa, perde 37. **A seção de resultados do TCC precisa ser construída sobre a
prova 2**, e não sobre a prova 1.

**3. Divergências com o TCC1**, para o artigo ([B-44](../backlog.md#b-44)).
Quatro mudanças têm de ser escritas com o porquê:
- base de protocolos → fichas de triagem em duas camadas;
- modelo local → Gemini como padrão, com o local como opção;
- tradutor previsto → desligado por padrão, braço da ablação;
- MiniLM → bge-m3.

## Deixado para depois

- **A ablação final** na arquitetura nova ([B-66](../backlog.md#b-66)). Braços:
  - sem contexto;
  - artigos com e sem tradutor;
  - fichas com e sem tradutor;
  - porta × 3 fichas;
  - leitura na ficha do mapa × na escrita pela IA;
  - os três atendentes, mais o tom;
  - o tradutor gerado pelo Gemini;
  - uma semântica só de métrica ([B-60](../backlog.md#b-60)).
  
  Fica para quando o projeto estiver completo, por decisão do João.
- **A prova 2** ([B-63](../backlog.md#b-63)), a **validação clínica**
  ([B-61](../backlog.md#b-61)), a **LGPD** ([B-64](../backlog.md#b-64)) e a
  **latência na demonstração** ([B-65](../backlog.md#b-65)).

## Próximo passo

A implementação, numa sequência de rodadas (23 a 30), cada uma com a sua
evidência e o seu teste de convergência. A primeira prova de que o código
converge é a réplica: o runner, pela API, reproduzindo a linha "proposto" da
tabela do resultado 2.
