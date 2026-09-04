# Runner de avaliação: a régua do time

**Data:** 04/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 4
**Commits:** [`bc90d80`](https://github.com/vinizika/tcc/commit/bc90d80) (identidade da versão) · [`aabd3c6`](https://github.com/vinizika/tcc/commit/aabd3c6) (métricas) · [`a95f895`](https://github.com/vinizika/tcc/commit/a95f895) (runner)

> As seções "Decisões" e "Resultado esperado" foram escritas **antes** de
> rodar as medições, como manda o padrão destas evidências.

## O que foi feito

A régua que transforma casos isolados em número. Três peças:

1. **Identidade da versão** (`GET /health/fingerprint`): modelo com digest,
   versão do Ollama, contagem e hash dos trechos indexados, hash dos
   prompts. Vai no manifesto de cada rodada.
2. **Módulo de métricas**: puro, offline, com teste de regressão contra as
   98 respostas de 04/05.
3. **Runner e comparador**: rodam o conjunto contra a API, gravam resultados
   versionáveis e comparam duas rodadas com teste estatístico.

## Por quê

O script de métricas do projeto apontava para a rota `/triagem`, removida na
entrega anterior: **os 70,41% de 04/05 não eram reproduzíveis**. Sem uma
régua funcionando não há Marco 1, e o estudo de ablação previsto no artigo
não tem como existir.

A rodada anterior deu o segundo motivo. O mesmo relato, repetido quatro
vezes, deu acerto três vezes e erro grave uma. Caso isolado não é medição, e
uma diferença entre duas execuções pode ser só ruído.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **Acurácia balanceada** é a métrica principal; a estrita fica como elo com 04/05 | O conjunto tem 71 emergências e 27 não emergências, então sempre responder "emergência" acerta 72,4%. Nos dados de 04/05 a diferença de leitura é clara: 70,41% de estrita, abaixo do chute ingênuo, contra 53,2% de balanceada, pouco acima dos 50% de chance |
| 2 | Relatos continuam em inglês, como em 04/05 | Comparabilidade. Traduzir as 194 strings de sintoma exige revisão humana e vira rodada própria |
| 3 | Rodadas gravam fora do Git; só as citadas por uma evidência são versionadas | Todo número do TCC tem os dados que o produziram, sem inchar o repositório com experimentos descartáveis |
| 4 | Regras triviais entram no relatório como referência | Sem elas, 70% parece bom. Com elas, fica claro o que o conjunto mede |
| 5 | Abstenções e saídas inválidas contam como erro nas acurácias | Um sistema que se recusa a decidir não ajuda o tutor. `coverage` mostra o outro ângulo, sempre ao lado |
| 6 | Seed explícita por repetição quando a temperatura é maior que zero | A API fixa a seed em 42 quando nenhuma é enviada, então as repetições seriam cópias da mesma execução, medindo nada |
| 7 | Cada linha confere que a configuração efetiva não mudou | Um backend reiniciado com outro `.env` no meio da rodada produziria linhas incomparáveis na mesma medição |
| 8 | Contrastes pré-registrados: primário RAG contra LLM puro; secundário o mesmo nas não emergências; o resto é exploratório | Com 98 linhas e várias comparações, correção de múltiplos testes zera tudo. Melhor declarar antes o que é confirmatório |
| 9 | Configuração recusada aborta no aquecimento; falha transitória é repetida; três falhas seguidas abortam | Erro de configuração não é dado. Erro de rede não pode derrubar 40 minutos de rodada |
| 10 | Ancoragem é nula, e não zero, quando a rodada não usa recuperação | "Zero citações" seria lido como falha, quando a etapa nem existiu |
| 11 | Divisão sem denominador devolve nulo | Nos estratos pequenos, a diferença entre "mediu e deu zero" e "não dá para medir" importa |
| 12 | Previsões em JSONL, gravadas linha a linha com sincronização | O texto bruto do modelo tem quebras de linha e aspas, que quebrariam um CSV em silêncio. E uma rodada de 40 minutos não pode perder tudo por uma interrupção no fim |

## Resultado esperado

*(escrito antes de rodar as medições)*

| Rodada | Configuração | Esperado |
|---|---|---|
| **R1** | Modo legado, temperatura 0,8, 3 repetições | Acurácia estrita entre 65% e 75% em cada repetição, com a faixa contendo os 70,41% de 04/05 |
| **R2** | LLM puro, prompt atual, temperatura 0, 2 repetições | Zero linhas instáveis entre as duas. Estrita entre 70% e 78%; recall de não emergência ainda baixo, abaixo de 30%, porque o prompt novo diz "um único sinal grave basta" e isso empurra para emergência |
| **R3** | RAG com busca ligada e otimização de consulta desligada | **Efeito abaixo da diferença mínima detectável.** A base tem só protocolos de emergência e os relatos são listas de sintomas em inglês, então a recuperação tende a trazer pouco de útil. Se houver efeito, deve ser para **mais** emergência, piorando o recall de não emergência |
| **R3b** | Pipeline completo, 3 repetições | Linhas instáveis acima de zero, quantificando a instabilidade que a rodada anterior viu em 1 de 4 execuções |

Vale registrar o que se espera do Marco 1: **um resultado nulo é o mais
provável, e não é fracasso**. Se o RAG não mover o número, os dados dizem
por quê — quantas linhas não tiveram nenhum documento relevante, e quais
trechos foram citados. Isso é insumo direto para o trilho A.

## Resultado obtido

### Testes automatizados: 54 novos (48 nos scripts, 6 no backend)

Rodam no host, sem API e sem modelo — o HTTP fica atrás de um cliente
injetável. O total do projeto passa a 97: 49 no backend e 48 nos scripts.

| Arquivo | Testes | O que garante |
|---|---|---|
| `test_run_evaluation.py` | 25 | Que o runner não estrague uma rodada: retomada sem duplicar, última linha truncada refeita, falha transitória repetida, configuração recusada abortando, seed avançando por repetição |
| `test_evaluation_metrics.py` | 14 | Que os números sejam os certos, com o **teste dourado** à frente |
| `test_report_evaluation.py` | 9 | Os testes estatísticos, com valores conferíveis à mão |
| `test_api_health.py` (backend) | 6 | Que a identidade da versão seja estável e não derrube a resposta quando uma parte não responde |

Dois testes carregam mais peso que os outros:

- **O teste dourado** alimenta o módulo com as 98 respostas registradas em
  04/05 e exige que ele devolva os números daquele dia: 0,7041 de acurácia,
  recall de emergência 0,9155, 4 falsos não urgentes, 19 falsos urgentes.
  **É o que autoriza comparar qualquer resultado novo com o histórico.** Sem
  ele, a régua nova poderia estar medindo outra coisa e ninguém saberia.
- **A regressão dos relatos** compara o texto enviado ao modelo com os 98
  relatos gravados em 04/05, um por um. Se alguém mudar o template, a
  comparação com o histórico deixa de valer — e isso agora falha alto em vez
  de virar uma diferença inexplicada nos números.

**As duas previsões mais importantes estavam erradas** — a do prompt para
menos, a do RAG na direção oposta. É o tipo de resultado que só aparece
medindo o conjunto inteiro.

### Panorama

| Rodada | O que testa | Balanceada | Estrita | Falsos não urgentes | Falsos urgentes |
|---|---|---|---|---|---|
| 04/05 (histórico) | prompt antigo, sem RAG | 0,532 | 0,704 | 4/71 | 19/27 |
| **R1** replicação | prompt antigo, T=0,8, 3 repetições | 0,572–0,666 | 0,714–0,765 | 3–4 | 11–22 |
| **R2** linha de base | **prompt novo**, sem RAG, T=0 | **0,893** | **0,878** | 8/71 | 2/27 |
| **R3** Marco 1 | prompt novo **com RAG** | 0,763 | 0,674 | **30/71** | 1/27 |

Referências sem modelo, no mesmo conjunto: sempre responder emergência
acerta 0,724; "menos de 5 sintomas" acerta 0,990; "só sintomas leves"
acerta 1,000.

### R1: a medição de 04/05 era um sorteio, não um ponto

A faixa das três repetições ficou em 0,714–0,765 de acurácia estrita, e
**não contém os 0,7041** registrados no diário. O motivo aparece na
estabilidade: **28 das 98 linhas mudaram de classificação entre execuções
idênticas**, e a concordância total foi de 0,714.

A instabilidade não é uniforme entre as classes:

| Classe esperada | Linhas instáveis |
|---|---|
| Emergência | 13 de 71 (18%) |
| Não emergência | **15 de 27 (56%)** |

Mais da metade das não emergências oscila. As linhas alternam entre os três
rótulos — por exemplo, a linha 17 deu não emergência, emergência e não
emergência nas três execuções.

Descartei as duas explicações mais óbvias para a diferença em relação ao
histórico: **nenhuma resposta precisou de segunda tentativa** e **nenhum
rótulo veio fora do padrão**, então nem o retry nem a normalização que eu
havia listado como diferenças influíram. Resta a versão do modelo, que não
foi registrada em 04/05, e o próprio ruído.

**A leitura que importa:** os 70,41% nunca foram um número preciso. Com 29%
das linhas instáveis, qualquer comparação que tratasse aquele valor como
referência exata estava comparando com um sorteio. É por isso que as rodadas
do trilho agora fixam temperatura zero e seed.

### R2: o prompt da entrega anterior foi o salto real

Esta rodada mede o prompt novo sem RAG, com temperatura zero:

| Métrica | 04/05 | R2 | Diferença |
|---|---|---|---|
| Acurácia balanceada | 0,532 | **0,893** | +36 pp |
| Recall de não emergência | 0,148 | **0,926** | +78 pp |
| Recall de emergência | 0,916 | 0,859 | −6 pp |
| Falsos urgentes | 19/27 | **2/27** | −17 |
| Falsos não urgentes | 4/71 | 8/71 | +4 |

**O problema central do projeto foi resolvido pelo prompt.** O sistema
reconhecia 4 de 27 não emergências; agora reconhece 25 de 27. Os falsos
urgentes, que são a causa do gargalo nas clínicas que o projeto quer
reduzir, caíram de 19 para 2.

O custo foi assimétrico e precisa ser dito: os falsos não urgentes subiram
de 4 para 8. Em triagem, esse é o erro grave — mas a métrica de 04/05 não
comparava as duas coisas, e por isso a troca ficava invisível.

**Zero linhas instáveis nas duas repetições**, confirmando que o braço sem
recuperação é determinístico e serve de linha de base.

Ressalva de atribuição: R1 e R2 diferem em duas coisas, o prompt e a
temperatura. A comparação limpa exige rodar o prompt antigo a temperatura
zero, o que está na fila.

### R3 (Marco 1): com a base atual, o RAG piora o sistema

Contraste primário pré-registrado, R2 contra R3, nas mesmas 98 linhas:

| Métrica | Sem RAG | Com RAG | Diferença |
|---|---|---|---|
| Acurácia estrita | 0,878 | 0,674 | **−20,4 pp** |
| Acurácia balanceada | 0,893 | 0,763 | −12,9 pp |
| Recall de emergência | 0,859 | 0,563 | −29,6 pp |
| **Falsos não urgentes** | 8/71 | **30/71** | **+22** |
| Falsos urgentes | 2/27 | 1/27 | −1 |

Teste de McNemar pareado: 23 linhas que o braço sem RAG acertou e o com RAG
errou, contra 3 no sentido oposto. **p exato = 0,0001.** Intervalo de
confiança de 95% para a diferença de acurácia: **[−29,6 pp, −11,2 pp]** —
inteiramente negativo, e muito além dos ~6 pontos de diferença mínima
detectável neste conjunto.

Não é ruído: **o RAG, com a base de hoje, degrada o sistema em 20 pontos, e
na direção mais perigosa.** As 27 linhas que mudaram de classificação foram
todas de emergência para não emergência.

### Por que o RAG piorou: recalibração, não alucinação

Os dados de recuperação explicam:

| Medida | Valor |
|---|---|
| Linhas sem nenhum trecho acima do limiar de 0,70 | **100%** |
| Score máximo médio | 0,574 |
| Trechos enviados por linha | 3 |
| Respostas que citaram alguma fonte | 39% |

E o detalhe decisivo: **as 30 linhas que passaram emergência como leve
citaram zero fontes**. Elas receberam três trechos irrelevantes cada e não
usaram nenhum. A justificativa mostra o mecanismo:

> Relato: *"Animal: Dog. Sintomas observados: Fever, Diarrhea, Coughing,
> Tiredness, Pain."*
>
> Resposta: *"[...] A ausência de sinais de emergência graves, como
> dificuldade respiratória intensa ou desmaio, torna o caso menos urgente."*

O modelo leu protocolos sobre dificuldade respiratória e convulsões, e
passou a usar aquela gravidade como régua. Febre com diarreia, tosse, dor e
cansaço virou "menos urgente" **por comparação**.

Ou seja: o contexto irrelevante não produziu citação falsa — produziu
**recalibração do limiar de gravidade**. A regra do prompt "se um trecho
tratar de outro problema, ignore-o" funcionou para a citação e falhou para o
julgamento. Esse é um efeito diferente do que a literatura de RAG costuma
tratar como risco principal, que é a alucinação ancorada em fonte errada.

**Isto é insumo direto para o trilho A**, com número: enquanto a busca não
separar assunto, ligar o RAG custa 20 pontos de acurácia e 22 falsos não
urgentes.


### R1b e R3c: dois braços a mais para fechar a atribuição

Duas perguntas ficaram abertas depois de R2 e R3, e cada uma virou um braço.

**"Foi o prompt ou a temperatura?"** R1 e R2 diferiam em duas coisas. R1b
roda o prompt **antigo** a temperatura zero, isolando a variável:

| | Prompt antigo (R1b) | Prompt novo (R2) | Diferença |
|---|---|---|---|
| Acurácia balanceada | 0,572 | 0,893 | **+32,1 pp** |
| Recall de não emergência | 0,185 | 0,926 | **+74,1 pp** |
| Recall de emergência | 0,958 | 0,859 | −9,9 pp |
| Falsos urgentes | 22/27 | 2/27 | −20 |
| Falsos não urgentes | 3/71 | 8/71 | +5 |

**O prompt da entrega anterior vale 32 pontos de acurácia balanceada**, com
uma única variável mudando. É o resultado mais forte do trilho até aqui, e
ele estava invisível porque a régua não existia.

**"E se o problema for só o excesso de contexto?"** R3c manda **um** trecho
em vez de três:

| | 1 trecho (R3c) | 3 trechos (R3) | Sem RAG (R2) |
|---|---|---|---|
| Acurácia balanceada | 0,690 | 0,763 | **0,893** |
| Falsos não urgentes | 19/71 | 30/71 | **8/71** |
| Falsos urgentes | 8/27 | 1/27 | 2/27 |

Reduzir o contexto **não resolve**. Com um único trecho os falsos não
urgentes caem de 30 para 19, mas continuam mais que o dobro do braço sem
RAG. Não é excesso de contexto: é contexto irrelevante, em qualquer
quantidade.

### R3b: o pipeline completo é o pior braço, e o mais instável

Com reescrita de consulta, multi-query e HyDE ligados, três repetições:

| Repetição | Balanceada | Estrita | Falsos não urgentes |
|---|---|---|---|
| 1 | 0,732 | 0,612 | 36/71 |
| 2 | 0,707 | 0,592 | 37/71 |
| 3 | 0,663 | 0,561 | 36/71 |

Média de 0,701 de balanceada, desvio de 0,029. **33 das 98 linhas mudaram de
classificação entre execuções idênticas**, com concordância total de 0,663.

O detalhe mais interessante: a etapa de consulta **melhorou a recuperação** e
**piorou o resultado**. As linhas sem nenhum trecho acima do limiar caíram de
100% (R3) para 60% (R3b), e o score máximo médio subiu de 0,574 para 0,680.
Ou seja, a reescrita e o HyDE aproximaram as consultas do vocabulário da
base — e trouxeram trechos mais parecidos, porém ainda do assunto errado.
Contexto mais plausível causou mais recalibração, não menos.

A latência também: 5,7s por resposta, sendo 3,5s só na etapa de consulta,
**60% do tempo antes de qualquer busca**.

### Panorama final: seis rodadas, 98 relatos cada

Tudo a temperatura zero, exceto onde indicado.

| Braço | Balanceada | Estrita | Falsos não urgentes | Falsos urgentes | Instabilidade |
|---|---|---|---|---|---|
| Prompt antigo, sem RAG | 0,572 | 0,745 | 3/71 | 22/27 | — |
| Prompt antigo, T=0,8 (3×) | 0,572–0,666 | 0,714–0,765 | 3–4 | 11–22 | 28/98 |
| **Prompt novo, sem RAG** | **0,893** | **0,878** | 8/71 | 2/27 | **0/98** |
| Prompt novo, RAG 1 trecho | 0,690 | 0,684 | 19/71 | 8/27 | — |
| Prompt novo, RAG 3 trechos | 0,763 | 0,674 | 30/71 | 1/27 | — |
| Pipeline completo (3×) | 0,663–0,732 | 0,561–0,612 | 36–37 | 0–3 | 33/98 |

**A melhor configuração medida do sistema é a mais simples: prompt novo, sem
RAG.** Cada componente de recuperação adicionado degradou o resultado, e o
pipeline completo — que é o que o artigo propõe — é o pior de todos.

Isso não invalida a proposta do TCC. Invalida a **base de conhecimento
atual**: 7 protocolos sintéticos, todos de emergência, em português, contra
relatos que são listas de sintomas em inglês. O mecanismo está medido e a
correção é do trilho A. O runner agora detecta isso em 5 minutos, o que é
exatamente para o que ele foi construído.

### As rodadas

Todas versionadas em `data/evaluation/cited/`, com previsões linha a linha,
manifesto e relatório:

| Rodada | Diretório |
|---|---|
| R1 replicação | [`r1_replicacao_legado`](../../data/evaluation/cited/20260904-022707_r1_replicacao_legado/report.md) |
| R1b prompt antigo, T=0 | [`r1b_legado_deterministico`](../../data/evaluation/cited/20260904-031331_r1b_legado_deterministico/report.md) |
| R2 linha de base | [`r2_linha_de_base`](../../data/evaluation/cited/20260904-023453_r2_linha_de_base/report.md) |
| R3 Marco 1 | [`r3_marco1`](../../data/evaluation/cited/20260904-024054_r3_marco1/report.md) |
| R3b pipeline completo | [`r3b_variancia`](../../data/evaluation/cited/20260904-024433_r3b_variancia/report.md) |
| R3c um trecho | [`r3c_um_trecho`](../../data/evaluation/cited/20260904-031550_r3c_um_trecho/report.md) |

## Observações

1. **A melhor configuração do sistema é a mais simples.** Prompt novo sem
   RAG bate todos os braços com recuperação. Isso precisa estar no artigo
   como resultado, não ser escondido: é um achado legítimo sobre o custo de
   ligar RAG com base inadequada.
2. **O mecanismo do dano é recalibração, não alucinação.** As 30 linhas que
   rebaixaram emergência citaram **zero** fontes. Elas leram protocolos de
   dificuldade respiratória e convulsão, e passaram a usar aquela gravidade
   como régua. A literatura de RAG trata a alucinação ancorada em fonte
   errada como risco principal; este é outro efeito, e vale mencionar na
   discussão.
3. **Melhorar a recuperação sem melhorar a base piorou o resultado.** A
   etapa de consulta elevou o score médio de 0,574 para 0,680 e derrubou a
   acurácia. Otimizar a busca sobre uma base enviesada aproxima do trecho
   errado com mais confiança. Trilho A e B1.
4. **A medição de 04/05 era um sorteio.** 28 das 98 linhas instáveis a
   temperatura 0,8, e mais da metade das não emergências oscilando. Qualquer
   número daquela rodada tem uma incerteza de vários pontos, e comparações
   contra ele como valor exato não eram válidas. Nota metodológica para o
   artigo.
5. **A instabilidade do pipeline completo está medida: 33 de 98 linhas.**
   Confirma e quantifica o que a rodada anterior viu em um caso. Enquanto a
   seed da etapa de consulta não for fixada, nenhuma rodada com o pipeline
   completo é reproduzível. Trilho B1, três linhas de correção.
6. **O prompt novo trocou um erro por outro, e o novo é o grave.** Falsos
   urgentes caíram de 22 para 2, mas falsos não urgentes subiram de 3 para
   8. Em triagem, deixar passar uma emergência é pior que exagerar. A troca
   é defensável pelo saldo, mas precisa ser dita — e é o alvo da próxima
   entrega.
7. **As regras triviais continuam ganhando de tudo.** "Só sintomas leves"
   acerta 98 de 98. Nenhuma conclusão sobre capacidade de triagem geral pode
   sair deste conjunto. Time e especialista.
8. **A etapa de consulta custa 60% da latência** e, hoje, prejudica o
   resultado. Desligá-la melhora acurácia e tempo ao mesmo tempo.

## Deixado para depois

| Item | Por quê | O que faria voltar |
|---|---|---|
| **Relatos em português** | A base indexada está em português e os relatos de avaliação em inglês, o que provavelmente limita a recuperação. Traduzir exige mapear 194 strings de sintoma, várias com erro de grafia no dataset original ("Anoxeria", "Seizuers", "Week Pulse"), e isso pede revisão de quem entende de clínica | Um arquivo de mapeamento revisado pela especialista, versionado, e uma rodada própria comparando os dois idiomas — nunca misturados na mesma comparação |
| **Braços de Chain-of-Thought e Self-Refine** | Ainda não implementados; as chaves existem e a API recusa com erro 400 de propósito, para não gerar linha de ablação sem significado | As entregas 5 e 6 do trilho |
| **Métricas do framework RAGAs** | Previstas no artigo. Dependem de a ancoragem estar estável primeiro, e hoje a recuperação ainda erra a ordenação | Ordenação da busca resolvida pelo trilho A |
| **Métrica de sinal alucinado** | A rodada anterior notou o modelo citando "sangue na urina" num relato que não mencionava sangue. Comparar sinais da resposta com o texto do relato é medível, mas exige decidir como tratar sinônimos | Quando o Self-Refine entrar, porque é a métrica que mostraria se ele ajuda |

## Próximo passo

**Chain-of-Thought**, a chave que hoje a API recusa de propósito. O alvo é o
falso não urgente: pedir ao modelo que percorra os sinais um a um antes de
concluir deve reduzir a chance de ele rebaixar um caso grave por comparação
com o contexto — o mecanismo medido aqui.

A linha de base para comparar já existe e é determinística: prompt novo, sem
RAG, 0,893 de acurácia balanceada e 8 falsos não urgentes.
