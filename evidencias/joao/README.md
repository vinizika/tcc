# Evidências — João Pedro Peterutto · Trilho B2 (Decisão)

Trilho responsável pelo caminho **da evidência recuperada até a resposta**:
geração ancorada nos documentos, classificação estruturada, Chain-of-Thought e
Self-Refine, e a régua de avaliação do sistema (runner de métricas).

- **[planejamento.md](planejamento.md)** — o que já foi feito, o que vem a
  seguir e o que está travando.
- **[../backlog.md](../backlog.md)** — a fila única de melhorias do projeto,
  compartilhada pelos três; é para lá que vão as observações que exigem ação.
- [`docs/divisao-de-trabalho.md`](../../docs/divisao-de-trabalho.md) — escopo
  e fronteiras entre os trilhos.
- [`../README.md`](../README.md) — o padrão destes registros.

## Rodadas

| # | Data | Rodada | Resultado |
|---|---|---|---|
| 0 | 03/09 | [Estado inicial](2026-09-03-01-estado-inicial.md) | Marco zero: geração é mock, régua quebrada, baseline de 70,41% não reproduzível |
| 1 | 03/09 | [Higiene do repositório e ambiente](2026-09-03-02-higiene-e-ambiente.md) | 41 arquivos gerados fora do Git; clone limpo sobe; modelo 100% na GPU |
| 2 | 03/09 | [Configuração centralizada](2026-09-03-03-configuracao-centralizada.md) | Mesmo código roda em Docker e local; saída por schema com campos exatos em 8s |
| 3 | 04/09 | [Geração ancorada nos documentos](2026-09-04-04-geracao-ancorada.md) | Mock morto: classificação real com fontes citadas, 43 testes. RAG muda a decisão em 1 dos 3 casos, mas a etapa de consulta erra 1 em 4 execuções |
| 4 | 04/09 | [Runner de avaliação](2026-09-04-05-runner-de-avaliacao.md) | A régua existe. **O prompt da rodada 3 vale +32 pontos**; e com a base atual **o RAG custa 20 pontos e 22 falsos não urgentes** (p = 0,0001) |
| 5 | 05/09 | [Determinismo da consulta](2026-09-05-06-determinismo-da-consulta.md) | Segundo uso da régua, confirmatório. A correção do B1 cortou 82% da instabilidade (33 → **6 linhas em 98**), mas não zerou: o resto é ruído de GPU, proporcional ao tamanho da geração. **A etapa de decisão é determinística** (0 exceções) |
| 6 | 11/09 | [Endurecimento do instrumento](2026-09-11-07-endurecimento-do-instrumento.md) | Revisão das entregas dos trilhos A e B1. A régua passa a **recusar medir sobre a base errada ou vazia**, o retrato identifica conteúdo e embedder, e o `compare` avisa quando o código mudou. Nenhuma métrica mudou |
| 7 | 11/09 | [Chain-of-Thought](2026-09-11-08-chain-of-thought.md) | **Resultado negativo.** Falsos não urgentes de 8 para 1, mas a classe leve foi a **zero** e a balanceada caiu de 0,856 para 0,408. O controle mostrou que escrever o raciocínio **depois** é melhor que antes — a hipótese da ordem está refutada |
| 8 | 12/09 | [Autópsia do Chain-of-Thought](2026-09-12-09-autopsia-do-cot.md) | Análise, sem código. A causa não era o modelo: **a rubrica pergunta o que o dado não tem**. O raciocínio do modelo é racionalização, não julgamento. A linha de base é atalho lexical, e os braços com RAG mediram **ruído** — nenhum trecho passou do limiar em 98 linhas |
| 9 | 12/09 | [Corte de relevância](2026-09-12-10-corte-de-relevancia.md) | O sistema para de injetar trecho irrelevante. Com a base atual a busca fica **silenciosa em 98 de 98** linhas, e o resultado é **idêntico** à linha de base de 04/09. O par com e sem corte isola o custo do ruído: **11,8 pontos e 22 falsos não urgentes** |
| 10 | 12/09 | [Régua de recuperação](2026-09-12-11-regua-de-recuperacao.md) | Construída **em nome do trilho A**. O protocolo certo está sempre entre os cinco devolvidos, mas vem em 1º em só 5 de 9: o problema é **ordenação**. E existe um **protocolo-ímã** — "trauma" em 1º em 9 de 18 casos |
| 11 | 12/09 | [Mapa de assuntos](2026-09-12-12-mapa-de-assuntos.md) | Construção, sem medição. **61 quadros clínicos** com referência, par de confusão e a pergunta que separa cada par; etapa 1 com 31. O eixo toxicológico do Brasil é outro: **"chumbinho" é metade das intoxicações em gatos** na USP. A decisão de ir às 61 fica para uma porta com critérios escritos antes |
| 13 | 12/09 | [Compare da régua](2026-09-12-14-compare-da-regua.md) | O instrumento da porta de decisão; a determinismo da régua permanece válido. **Errata de 13/09:** a cobertura histórica não preservava espécie por rodada nem exigia encontro no caso esperado; o compare foi corrigido sem reescrever resultados brutos |
| 12 | 12/09 | [O pesquisador](2026-09-12-13-pesquisador.md) | O agente que acha as fontes, com captura determinística e piloto na torção gástrica. Achado de fundo: **não existe fonte autoritativa, em português e para tutor** — então cada linha leva uma de cada natureza, e a etapa 1 vira experimento de idioma × registro |
| 14 | 23/09 | [Autópsia 2: o sistema de hoje, medido](2026-09-23-15-autopsia-do-sistema-de-hoje.md) | Análise, sem código. Com a base de 3.481 trechos, **o RAG não ajuda** (conserta 2, quebra 8 em 232; p = 0,11): nenhum trecho passa da porta por mérito, e **116 de 122 relatos de quem não viu o mapa chegam sem contexto**. Nesses relatos o sistema erra metade; o llama acerta **1 de 38** emergências contadas com calma. A âncora esconde a obstrução uretral |
| 15 | 23–24/09 | [Fichas no lugar dos artigos](2026-09-23-16-fichas-no-lugar-dos-artigos.md) | Com a busca perfeita, o trecho acadêmico não ajuda (llama: 16 perdas com ele, 14 sem nada) e **a ficha de triagem resolve** (0). Sem a linha de conduta, a ficha ainda derruba as perdas do qwen de 21 para 4: é o conteúdo que ensina. Português ganha de inglês. A etapa 2 está vazia no mapa, e a ficha errada custa caro |
| 16 | 24/09 | [Busca: bge-m3, 3 fichas, sem porta nem âncoras](2026-09-24-17-busca-bge-m3-e-tres-fichas.md) | bge-m3 leva a ficha certa em 1º de ~20% para ~80%; só vale com as fichas em português. **As 3 mais próximas, sem porta**, ganham da porta nos relatos de quem não viu o mapa (qwen 21 → 7 perdidas, p = 0,0005) — na prova, empatam. Âncoras fora; título real na citação |
| 17 | 24/09 | [O tradutor desligado](2026-09-24-18-tradutor-desligado.md) | Defeitos certificados com o llama e o Gemini: o multi-query e o HyDE diagnosticam porque o prompt pede. **Nas fichas, toda técnica piora a busca**, e nenhum conserto resolve. Na 2×2, fichas sem tradutor é a melhor célula (9 × 0 e 14 × 0 contra o sistema de hoje). Fica como braço da ablação |
| 18 | 24/09 | [Quem decide: llama, qwen ou Gemini](2026-09-24-19-atendente-llama-qwen-gemini.md) | O llama decide pelo tom. Com as mesmas fichas, **qwen e Gemini empatam** em segurança; o Gemini dá menos alarmes falsos e é mais rápido na mediana, com cauda; o qwen precisa de GPU (34 s sem ela). Pelo critério escrito antes, ficaria o qwen; **a decisão de produto foi o Gemini**, com o qwen e o llama como opções |
| 19 | 24/09 | [Fichas em duas camadas](2026-09-24-20-fichas-em-duas-camadas.md) | A IA escreve as fichas com a origem de cada frase (99,8% dos trechos conferem). A ficha escrita pela IA **busca** melhor (independentes: 52 → 61% em 1º), mas **ler** ela piora o qwen (13 perdas; vira checklist). Busca na ficha da IA, leitura na do mapa: 5 · 7. O critério pré-registrado falhou, e está dito |
| 20 | 24/09 | [Prova 2: desenho e piloto](2026-09-24-21-prova-2-desenho-e-piloto.md) | A prova 1 entrega a classe pelas palavras (79% sem assunto em comum) e só vê diferenças grandes. Especificação dos 330 relatos. O piloto de 40 passou: é **mais difícil** que a prova 1 e reproduz os efeitos dos relatos independentes |
| 21 | 24/09 | [O sistema proposto contra o de hoje](2026-09-24-22-arquitetura-proposta-contra-a-de-hoje.md) | Nos relatos de quem não viu o mapa: **40 · 22 → 6 · 3** (35 × 1, p < 0,0001); tom 46 → 3. Na prova + régua, 15 · 4 → 2 · 1 — mas contra o sistema de hoje com o tradutor, 8 × 2 (p = 0,11): o limite da prova 1. A implementação e a réplica pelo runner são as rodadas seguintes |
| 22 | 25/09 | [Preparação da implementação](2026-09-25-23-preparacao-da-implementacao.md) | Ponto de partida conferido: clone de `2d37a5e`, suíte do CI verde (242 / 197) e os lotes iguais aos da autópsia. **O lote teste da prova 1 está congelado** (100 casos, `d370a0a5…`), com a ressalva do B-05 e um contador de uso (0) |
| 23 | 25/09 | [Fichas de busca e de leitura por script](2026-09-25-24-fichas-de-busca-e-de-leitura.md) | O `sync_fichas.py` gera o arquivo que o backend lê, e os **61 textos de busca e os 61 de leitura saem iguais, byte a byte, aos medidos na autópsia** (maior texto: 485 tokens). Coluna `por_que_importa` no mapa, vazia. Títulos reais pelo DOI (35 dos 67 não eram) e âncoras fora. Seis documentos aprovados tratam de outro assunto |
| 24 | 25/09 | [Busca nas fichas com o bge-m3](2026-09-25-25-busca-por-fichas-com-bge-m3.md) | Receita de embedding por manifesto (a coleção acadêmica continua abrindo com o MiniLM), coleção das 61 fichas versionada e ativa, busca vetorial pura como padrão, tradutor desligado. **A API devolve as mesmas 3 fichas que a autópsia em 296 de 296 casos**, e os agregados exatos (prova + régua 107/123 de 129; independentes 74/94 de 122). Clone limpo sobe sem passo manual (B-57) |
| 25 | 25/09 | [A resposta: ficha, fonte real e procedência](2026-09-25-26-resposta-com-ficha-e-fonte.md) | "Baseado em" mostra a ficha e o documento aprovado com título real e DOI; o trecho que não coube no prompt deixa de ser fonte; a resposta diz provedor, modelo e versão, e a queda do Gemini na consulta deixa de ser silenciosa; `think` do qwen configurável; runner com `--cases`. **O qwen pela API repete a autópsia em 50 de 50 casos** do lote dev |
| 26 | 25/09 | [O Gemini como atendente, e a réplica](2026-09-25-27-atendente-gemini-e-replica.md) | Gemini padrão, qwen e llama como opções; **sem chave, a API responde 503 em vez de trocar de modelo**, e a troca, quando permitida, vem dita na resposta. **A réplica pela API bate caso a caso**: Gemini 2 · 1 e 6 · 3, qwen 2 · 1 e 5 · 7, com a mesma resposta da autópsia em todos os casos; o sistema de hoje, 15 · 4. Só o braço de hoje com o tradutor fica fora (11 · 3 contra 8 · 3): o HyDE da autópsia não existe sem chave, e a reescrita do llama não é estável |
| 27 | 25/09 | [Fontes para as frases sem fonte das fichas de busca](2026-09-25-28-fontes-para-tutor-etapa-2.md) | Quatro agentes pesquisadores capturaram 45 fontes pelo script do time. **36 das 53 frases "geral" ganharam trecho literal (68%)**, 16 têm fonte parcial, 1 ficou sem; os 52 trechos conferidos por programa. Nenhuma frase mudou (a coleção reindexada seria idêntica). Cinco capturas são da VCA, que proíbe redistribuir |
| 28 | 25/09 | [Prova 2: a geração](2026-09-25-29-prova-2-geracao.md) | Nove agentes isolados escreveram os **330 relatos, com a composição exata** (190 emergências e 115 leves de 61 quadros, mais 25 especiais), "mas" em 40% de cada classe e nenhum texto repetido. Rótulos provisórios; a validação dos veterinários, a divisão e o congelamento vêm depois. A pesquisa foi mais fraca que a do piloto: a busca na web acabou cedo |
| 29 | 25/09 | [Fechamento da implementação](2026-09-25-30-fechamento-da-rodada-noturna.md) | Documentação, sem código de sistema: README, `.env.example`, contratos e estado atual descrevem o sistema que o código roda; a interface antiga sai; o backlog ganha B-74 a B-76 e registra o que as rodadas 22 a 28 deixaram para depois |
| 30 | 26/09 | [A validação dos especialistas, registrada](2026-09-26-31-validacao-dos-especialistas.md) | Registro, sem mudar o sistema: a ASAVET aceitou os 513 itens da folha das fichas, as 47 fontes que esperavam especialista e os seis documentos de outro assunto como estão, e validou **os 330 rótulos da prova 2, sem nenhuma mudança**. Os textos que o sistema lê ficaram iguais (61 de 61). Levar o conteúdo certificado à ficha de leitura é a próxima rodada, medida |

## Estado atual

**26/09 — a arquitetura da autópsia 2 está no código, replicada e validada
pelo João** (rodadas 22 a 29), e a validação dos especialistas está registrada
(rodada 30). O relato cru vai à
busca vetorial (bge-m3) nas 61 fichas de busca; as 3 mais próximas entram no
prompt como fichas de leitura; o Gemini responde por padrão, sem troca
silenciosa de modelo, e o qwen e o llama ficam como opções. O runner do time,
pela API, reproduz a autópsia caso a caso. Suíte: backend 285, scripts 217.

A próxima entrega: levar o conteúdo certificado das fichas à ficha de leitura,
medido contra a réplica ([B-61](../backlog.md#b-61)), e **a prova 2 até o uso**
— o resto da conferência, a divisão e o congelamento
([B-63](../backlog.md#b-63)). A ablação completa fica para quando o projeto
estiver completo ([B-66](../backlog.md#b-66)).

O roteiro completo, com marcos e os sete bloqueios abertos, está em
**[planejamento.md](planejamento.md)**.

## Números de referência

Da réplica pela API ([rodada 26](2026-09-25-27-atendente-gemini-e-replica.md)),
em **emergências perdidas · falsos alarmes** (perdida inclui INCERTO). A prova 1
entrega a classe pelas palavras e só vê diferenças grandes
([rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md)); o número final sai da
prova 2.

| Configuração | Prova + régua (74 · 58) | Independentes (76 · 46) | Piloto (24 · 16) | Tom calmo (74) |
|---|---|---|---|---|
| **Proposto, Gemini (padrão)** | **2 · 1** | **6 · 3** | **0 · 3** | **3** |
| Proposto, qwen3:8b | 2 · 1 | 5 · 7 | 0 · 3 | 4 |
| Gemini sem busca | 0 · 3 | 5 · 10 | — | — |
| qwen sem busca | 7 · 0 | 21 · 9 | — | — |
| Hoje (artigos, MiniLM, porta 0,72, llama), tradutor desligado | 15 · 4 | 40 · 22 (autópsia) | — | 46 (autópsia) |

### Números de 04/09 (histórico)

Medidos em 04/09 sobre os 98 relatos de cão e gato, temperatura zero. A
métrica principal é a **acurácia balanceada**, média do recall das duas
classes: 71 das 98 linhas são emergência, então a acurácia simples premiaria
um sistema que sempre responde "emergência" (72,4%).

| Configuração | Balanceada | Estrita | Falsos não urgentes |
|---|---|---|---|
| Prompt antigo, sem RAG | 0,572 | 0,745 | 3/71 |
| **Melhor atual**: prompt novo, sem RAG | **0,893** | **0,878** | 8/71 |
| Prompt novo, sem RAG, com Chain-of-Thought (11/09) | 0,408 | 0,592 | 1/71, mas 16 falsos urgentes |
| Prompt novo, com RAG **sem corte** (ruído) | 0,775 | 0,673 | 30/71 |
| Prompt novo, com RAG **com corte** (12/09) | **0,893** | **0,878** | 8/71 |
| Pipeline completo (05/09, estável) | 0,704 | 0,571 | 40/71 |

A leitura completa está na [rodada 4](2026-09-04-05-runner-de-avaliacao.md).
Duas ressalvas acompanham qualquer uso destes números: no conjunto de
avaliação a origem do dado separa perfeitamente o rótulo, e regras triviais
sem modelo acertam 98 de 98 — ou seja, o conjunto mede se o sistema parou de
exagerar cinco sinais leves, não a capacidade geral de triagem.
