# Confirmação do determinismo da etapa de consulta (B-04)

**Data:** 05/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 6 ·
**Commits:** _(a preencher ao fechar)_

## O que foi feito

Rodada de **medição**, não de implementação. O código medido não é meu: o
trilho B1 corrigiu o item [B-04](../backlog.md#b-04) no commit `b907d6e`,
fazendo as três chamadas ao modelo em `query_client.py` (`rewrite`,
`generate_queries`, `generate_hypothetical_document`) enviarem
`options=default_options()`. O que faço aqui é usar a régua do B2 para
responder à pergunta que o backlog deixou em aberto: **o pipeline completo
voltou a ser reproduzível?**

O critério de aceitação registrado no backlog é numérico e não ambíguo: o
preset `rag_query`, com `--repeat 2` sobre os 98 relatos, chegando a **zero
linhas instáveis**. O Ryu não pôde executá-lo — o ambiente dele não tinha
Ollama — e registrou isso na
[rodada 1 dele](../ryu/2026-09-04-01-reprodutibilidade-da-consulta.md), no
"Deixado para depois".

Rodada executada: `rag_query`, subset `full`, `--repeat 2`, 196 requisições.

## O segundo teste com a régua

Este é o **segundo uso da régua de avaliação** desde que ela existe. O
primeiro foi em 04/09, na [rodada 4](2026-09-04-05-runner-de-avaliacao.md),
que fechou o Marco 1. Os dois medem o mesmo sistema com o mesmo instrumento,
mas respondem a perguntas de naturezas diferentes, e essa diferença muda o
desenho de cada um:

| | **Primeiro teste** (04/09, rodada 4) | **Segundo teste** (05/09, esta rodada) |
|---|---|---|
| Pergunta | "O que o sistema faz hoje?" | "A correção do B-04 funcionou?" |
| Natureza | **Exploratório** — mapear o terreno sem saber o que se vai achar | **Confirmatório** — critério numérico declarado antes, resposta sim ou não |
| Braços | 6 (`legacy`, `legacy` determinístico, `llm_only`, `naive_rag` com 3 trechos, `naive_rag` com 1 trecho, `rag_query`) | 1 (`rag_query`) |
| Repetições | de 1 a 3, conforme o braço | 2, em ambas as passagens das 98 linhas |
| Requisições ao sistema | cerca de 700 | 196 |
| Métrica que decide | acurácia balanceada, com McNemar entre braços | `n_unstable_rows`, que precisa ser **zero** |
| Código sob teste | antes de `b907d6e` | depois de `b907d6e` |
| O que produziu | o Marco 1: o prompt vale +32 pontos, o RAG custa 20 | _(a preencher)_ |

A diferença de fundo é essa: o primeiro teste **descreveu** o sistema, e por
isso precisou de muitos braços e nenhuma hipótese fechada — as duas previsões
principais daquela rodada, aliás, saíram erradas, e foi disso que veio o
achado. O segundo **verifica uma afirmação específica** feita por outro
trilho, com o critério de aceitação escrito no backlog antes de existir
código para testá-lo. Um teste confirmatório com um critério declarado de
antemão não permite ajustar a régua depois de ver o resultado, e é por isso
que ele vale como evidência de que a correção funcionou.

**As medições antigas continuam onde estavam.** As seis rodadas do primeiro
teste seguem versionadas em `data/evaluation/cited/`, sem alteração — em
particular a R3b (`20260904-024433_r3b_variancia`), que é o "antes" deste
"depois". Nada foi sobrescrito nem regerado: uma rodada citada é um registro
histórico do que o sistema fazia naquele commit, e perde o sentido se for
atualizada. O que muda é a **leitura** dela, que passa a carregar a data de
validade — o número descreve o sistema anterior a `b907d6e`, não o atual.

Para o TCC isso vale por si: ter os dois testes preservados permite mostrar
o antes e o depois de uma correção pontual, com o resto do sistema
comprovadamente idêntico (mesma base, mesmo modelo, mesmos prompts).

## Por quê

**Porque a única medição que temos do pipeline completo descreve um sistema
que não existe mais.** A [rodada 4](2026-09-04-05-runner-de-avaliacao.md)
mediu o braço `rag_query` (R3b) com a etapa de consulta rodando a
temperatura 0,8 e seed aleatória. Aquele número — 0,701 de acurácia
balanceada, 36 falsos não urgentes em 71 — está citado no README da raiz, no
README da avaliação e no índice desta pasta. No instante do commit `b907d6e`
ele virou histórico. Deixá-lo circulando como número corrente seria levar
para o TCC uma medição de um sistema anterior.

**E porque a próxima entrega precisa de chão firme.** O planejamento diz que
a próxima entrega do B2 é o Chain-of-Thought, e ele será medido contra uma
linha de base. Se um dos braços de comparação for o pipeline completo, essa
linha precisa ser estável **antes**, ou o efeito do CoT vai ser lido em cima
de ruído. Medir agora custa 20 minutos; descobrir em outubro, montando a
matriz de ablação, que o pipeline ainda oscila custaria a matriz inteira.

Há ainda um motivo de processo: este é o primeiro item do backlog a
atravessar dois trilhos de ponta a ponta — nasceu numa medição do B2, foi
corrigido pelo B1 e volta ao B2 para confirmação. Vale registrar o ciclo
fechado, porque é o modelo de como os outros itens devem andar.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Medir isto **antes** do Chain-of-Thought, contrariando a ordem do planejamento | Dois motivos somados: a R3b virou número obsoleto no instante do commit do Ryu, e o CoT precisa de linha de base estável. Nenhum dos dois melhora esperando |
| `--repeat 2`, não 3 | O critério do backlog é *zero* linhas instáveis. Com temperatura zero, duas execuções idênticas já expõem qualquer não determinismo — a terceira só aumentaria a chance de flagrar evento raro, ao custo de mais 9,5 minutos. Se der zero em duas, subo para três antes de declarar o item resolvido |
| Reproduzir exatamente as condições da R3b | O contraste só isola o código da consulta se todo o resto for idêntico. Conferido **antes** de rodar, pelo `/health/fingerprint`: hash da base `eeba9f51…` igual, digest do modelo `a80c4f17…` igual, hashes dos três prompts de triagem iguais. Mesmo preset, mesmo subset |
| Não passar `--base-seed` | Com temperatura zero o runner mantém a seed configurada em todas as repetições, que é exatamente o teste desejado. Passar `--base-seed` variaria a seed por repetição e mediria dispersão, não determinismo |
| Não tocar em nada do pipeline durante a rodada | Uma segunda requisição ao modelo competiria pela GPU e contaminaria as latências medidas |

## Resultado esperado

_Escrito com a rodada em execução, antes de qualquer número._

**1. Determinismo — espero zero linhas instáveis** (contra 33 na R3b) e
concordância exata de 1,000 (contra 0,663). Confiança alta: a etapa de
consulta era a única fonte de não determinismo conhecida, e os braços que
não a usam (R2, R3) já mediram zero mudanças entre execuções idênticas, o
que mostra que a GPU a temperatura zero não introduz variação por conta
própria. **Se sobrar instabilidade**, existe uma segunda fonte que ninguém
mapeou — e aí o achado vale mais que o item, porque comprometeria toda a
matriz de ablação de outubro.

**2. Acurácia — aqui a previsão é fraca, e prefiro registrar a dúvida.** O
raciocínio fácil é "a correção fixa a variância, não mexe na qualidade", e
esperar a balanceada dentro da faixa da R3b (0,663 a 0,732). Mas há um
mecanismo que contraria isso: as consultas antes eram geradas a temperatura
0,8 e agora saem a 0. Texto a temperatura zero é o mais provável — tende ao
literal e ao genérico; a 0,8 é mais variado e às vezes mais específico.
Ou seja, **a correção pode ter deslocado o ponto central, não só reduzido a
dispersão**, porque o texto das consultas enviadas à busca mudou. Aposto na
faixa da R3b, mas sem convicção. Se sair fora dela, a explicação estará no
texto das consultas, e não no acaso.

**3. Falsos não urgentes — espero continuar alto, entre 30 e 36 de 71.** O
mecanismo descrito em [B-01](../backlog.md#b-01) — contexto irrelevante
recalibrando o limiar de gravidade para baixo — não foi tocado por esta
correção. Se cair muito, parte do que atribuí ao RAG na rodada 4 era, na
verdade, ruído da consulta, e a leitura daquela rodada precisa de ajuste.

**4. Um efeito colateral a verificar.** `default_options()` envia **quatro**
parâmetros, não dois: além de `temperature` e `seed`, entraram
`num_ctx=4096` e `num_predict=600`, que nas chamadas de consulta antes
ficavam no padrão do servidor. Espero que não morda — o prompt do HyDE pede
"um único parágrafo curto" —, mas se o documento hipotético estiver sendo
cortado em 600 tokens, a busca passa a receber uma âncora truncada, e o
efeito seria atribuído por engano ao determinismo. Vou medir o tamanho do
que o HyDE gera.

## Resultado obtido

Rodada [`20260905-133840_b04_confirmacao`](../../data/evaluation/cited/20260905-133840_b04_confirmacao/report.md)
· preset `rag_query` · 98 linhas · 2 repetições · 196 requisições · 19 min.

### A resposta à pergunta central: não, o critério não foi atingido

| | R3b (04/09, antes) | Esta rodada (05/09, depois) |
|---|---|---|
| Linhas instáveis | 33 de 98 | **6 de 98** |
| Concordância exata | 0,663 | **0,939** |

**A instabilidade caiu 82%, mas não chegou a zero.** O critério de aceitação
do [B-04](../backlog.md#b-04) exige zero linhas instáveis, então o item
**continua aberto** — com uma causa nova, identificada abaixo, que não é do
trilho B1 e provavelmente não tem solução completa.

Minha previsão nº 1 estava **errada**, e é dela que veio o achado desta
rodada. Eu havia escrito que a etapa de consulta era "a única fonte de não
determinismo conhecida". Era a única *conhecida*; não era a única.

### Onde a variação sobrevive, etapa por etapa

Comparando as duas repetições nas 98 linhas, campo a campo:

| Etapa | Varia em | Tamanho típico da saída |
|---|---|---|
| Reescrita (`rewrite`) | 8 de 98 (8%) | uma frase |
| Multi-queries (`generate_queries`) | 17 de 98 (17%) | três linhas curtas |
| **Documento HyDE** (`generate_hypothetical_document`) | **30 de 98 (30%)** | 66 a 154 palavras (mediana 89) |
| Trechos recuperados pela busca | 24 de 98 (24%) | — |
| **Classificação final** | **6 de 98 (6%)** | — |

**A taxa de variação cresce com o comprimento da geração** — 8%, 17%, 30% —
e essa é a assinatura de não determinismo numérico de GPU em decodificação
gulosa. Com temperatura zero o modelo escolhe sempre o token mais provável,
mas quando dois candidatos têm probabilidades quase idênticas, uma diferença
de arredondamento em ponto flutuante (que depende da ordem de redução das
operações na GPU, e não da seed) basta para inverter a escolha. Quanto mais
tokens gerados, maior a chance acumulada de isso acontecer ao menos uma vez;
e a partir da primeira divergência o texto segue outro caminho.

### Por que isso não é falha da correção do B1

A hipótese concorrente seria "a seed não está sendo aplicada". Os dados a
refutam: **se a correção não tivesse efeito, a reescrita variaria em
praticamente 100% das linhas**, porque antes ela rodava a temperatura 0,8
com seed aleatória. Ela varia em 8%. A correção fez o que prometia; o que
sobrou é ruído numérico, de outra natureza.

### A etapa de decisão (trilho B2) é determinística

Dois cruzamentos que isolam a responsabilidade de cada trilho:

| Verificação | Resultado |
|---|---|
| Linhas com **mesmo contexto** e classificação diferente | **0** |
| Linhas com contexto diferente e **mesma** classificação | 18 de 24 |

O primeiro número é o que me interessa diretamente: **a etapa de
classificação não introduz variação nenhuma**. Dado o mesmo relato e os
mesmos trechos, a decisão é sempre a mesma. Toda a instabilidade residual do
sistema nasce antes dela.

O segundo diz que o sistema **absorve 75% do ruído da busca**: das 24 linhas
em que os trechos recuperados mudaram, só 6 mudaram de decisão. Isso é
tolerância a ruído, e é uma propriedade desejável — mas tem um lado
incômodo, tratado nas Observações.

### Desempenho: nada mudou de forma detectável

| Métrica | R3b (antes) | Agora | Diferença |
|---|---|---|---|
| Acurácia balanceada | 0,7324 | 0,7042 | −2,8 pp |
| Acurácia estrita | 0,6122 | 0,5714 | −4,1 pp |
| Falsos não urgentes | 36/71 | 40/71 | +4 |
| Falsos urgentes | 0/27 | 0/27 | 0 |

**McNemar pareado: 12 contra 8, p = 0,503** (mid-p = 0,383). Intervalo de
confiança de 95% da diferença de acurácia estrita: **[−0,133; +0,051]**, que
contém zero. Com 98 linhas só detectamos diferenças a partir de ~6 pontos,
e esta não chega lá: **a correção mudou a reprodutibilidade, não o
desempenho** — que era exatamente o esperado de uma mudança que fixa
parâmetros de amostragem.

Vale notar que 20 linhas mudaram de classificação entre a R3b e esta rodada,
mas em direções opostas que quase se anulam (12 pioraram, 8 melhoraram).
Comparar um braço estável com um braço que oscilava é comparar um ponto com
um sorteio; a leitura correta é que o novo valor caiu **dentro** da faixa que
a R3b percorria (0,663 a 0,732), como eu previra na previsão nº 2.

### As previsões, uma a uma

| # | Previsão | Resultado |
|---|---|---|
| 1 | Zero linhas instáveis | ❌ **Errada.** Seis sobraram, por uma causa que eu não tinha mapeado |
| 2 | Balanceada dentro da faixa da R3b (0,663–0,732) | ✅ Certa: 0,704. A dúvida que registrei (se o ponto central se deslocaria por causa da mudança de temperatura nas consultas) se resolveu: não se deslocou de forma detectável |
| 3 | Falsos não urgentes entre 30 e 36 | ❌ Errada por pouco: 40. A diferença para os 36 da R3b não é significativa, mas minha faixa foi estreita demais — eu deveria tê-la ancorado na variação conhecida do braço, não no valor pontual |
| 4 | O teto de `num_predict=600` não morde no HyDE | ✅ Certa: o HyDE mais longo tem 154 palavras (~200 tokens), bem abaixo do teto. O efeito colateral não se materializou |

Duas de quatro erradas. A previsão nº 1 é a que valeu a rodada.

## O que mudou no repositório

Rodada de medição: **nenhuma mudança de comportamento no código.**

| Arquivo | Mudança |
|---|---|
| `evidencias/joao/2026-09-05-06-determinismo-da-consulta.md` | **novo** — esta rodada |
| `data/evaluation/cited/20260905-133840_b04_confirmacao/` | **novo** — a rodada promovida, com as 196 previsões, o manifesto e as métricas |
| `scripts/presets.json` | descrições de `rag_query` e `naive_rag` atualizadas (ver Observações) |
| `evidencias/backlog.md` | B-04 atualizado; itens novos B-24, B-25 e B-26 |
| `evidencias/joao/planejamento.md` | bloqueio 4 atualizado com o resultado |
| `evidencias/joao/README.md` | tabela de rodadas e números de referência |
| `README.md`, `data/evaluation/README.md` | número do pipeline completo com data de validade |

## Observações

**1. O critério do B-04 talvez seja inatingível como está escrito.** "Zero
linhas instáveis" pressupõe que todo não determinismo vem de configuração. A
parte que vinha de configuração foi corrigida e rendeu 82% de redução; o que
sobra é aritmética de ponto flutuante em GPU, que nem seed nem temperatura
controlam. Insistir no zero pode significar manter o item aberto para sempre.
A proposta que registro para o time é trocar o critério por um que diga o que
realmente importa: **a instabilidade residual não pode inverter nenhuma
conclusão da matriz de ablação** — o que se garante rodando os braços com
repetição e reportando a faixa, não um ponto. Decisão do time, não minha;
entra como [B-24](../backlog.md#b-24).

**2. O `compare` não percebeu que o sistema mudou.** Ele imprimiu
"diferenças de configuração: nenhuma" comparando uma rodada de antes com uma
de depois do commit `b907d6e`. Está correto no que checa — configuração,
dataset, modelo, base, prompts de triagem — e é justamente aí o furo: o
fingerprint não cobre o **código do pipeline** nem os **prompts da etapa de
consulta**. Como o B1 vai mexer nos dois (B-08 e B-10), rodadas minhas podem
mudar de resultado sem nenhum aviso do instrumento. O commit fica no
manifesto e o compose monta `./backend:/app`, então o git sha descreve mesmo
o código executado — só falta o `compare` compará-lo. Vira
[B-25](../backlog.md#b-25), e é meu.

**3. O runner não grava o documento do HyDE.** Para chegar à tabela de
propagação precisei inferi-lo como "o último elemento de `queries` com mais
de 200 caracteres". Funciona, mas é frágil e depende de uma convenção que
ninguém documentou. A etapa mais cara e mais variável da consulta é a única
sem registro próprio. Vira [B-26](../backlog.md#b-26).

**4. O braço completo nunca erra para o lado seguro.** Falsos urgentes: 0 de
27, nas duas rodadas. Falsos não urgentes: 40 de 71. Ou seja, quando o RAG
entra, o sistema não fica "mais cauteloso e menos preciso" — fica
**sistematicamente menos cauteloso**. Num produto de pré-triagem essa é a
direção errada do erro: mandar para casa um animal que precisava de
atendimento é o dano que o projeto existe para evitar. Reforça a prioridade
Alta do [B-01](../backlog.md#b-01) e é o argumento mais forte para não ligar
o RAG por padrão enquanto a base for a atual.

**5. A ancoragem continua fraca, e piorou de leve.** Linhas com ao menos uma
citação: 27,6% na R3b, 18,4% agora. Linhas sem nenhum trecho acima de 0,70:
60,2% antes, 64,3% agora. Score máximo médio 0,676. Nenhuma dessas
diferenças é grande o bastante para significar algo com 98 linhas, mas o
patamar é o mesmo de ontem: **o modelo decide quase sempre sem citar o que
leu** — 80 das 98 linhas citam zero fontes.

**6. Uma pista sobre a absorção de ruído.** Das 24 linhas em que a busca
trouxe trechos diferentes, 18 mantiveram a decisão. Poderia ser robustez, e
em parte é: 11 dessas 18 citaram fontes e ainda assim decidiram igual. Mas 7
delas não citaram nada em nenhuma das duas execuções — e nessas, "absorver o
ruído" e "ignorar o contexto" são indistinguíveis pelos dados.

**7. A consulta continua dominando a latência.** Cerca de 4,0s de 6,0s por
relato, ou 67% — agora com número deste braço inteiro, e não só do exemplo
isolado da rodada 3 ([B-07](../backlog.md#b-07)).

**8. As descrições dos presets ficaram obsoletas com o commit `b907d6e`.**
`rag_query` dizia "não é determinístico hoje" e `naive_rag` dizia ser
determinístico "porque a etapa de consulta ainda usa seed aleatória" — o
que, além de desatualizado, estava trocado: o `naive_rag` é determinístico
porque a consulta está **desligada**. Corrigidas nesta rodada.

### Hipóteses que nascem daqui

**H1 — a instabilidade residual é função do comprimento da geração.**
Sustentada pelo gradiente 8% / 17% / 30%. É testável de forma barata: rodar
`naive_rag --repeat 2` (nenhuma chamada de consulta) deve dar **zero** linhas
instáveis, e `rag_query` com HyDE desligado deve ficar num patamar
intermediário. Se o `naive_rag` também oscilar, a hipótese cai e o problema é
maior do que a etapa de consulta.

**H2 — o HyDE pode estar atrapalhando a recuperação, não ajudando.** É a
saída mais longa, a mais variável (30%) e a mais inventada das três: um
parágrafo de protocolo fabricado pelo modelo, que entra na busca com o mesmo
peso das consultas derivadas do relato real. Não dá para decidir isso com a
régua atual, que mede a classificação final; depende da régua de recuperação
do trilho A ([B-09](../backlog.md#b-09)) ou de uma ablação com HyDE ligado e
desligado neste mesmo braço.

### Hipóteses que esta rodada confirmou

- **A etapa de decisão é determinística** — zero linhas com mesmo contexto e
  decisão diferente. Era premissa da minha régua; agora é medição.
- **O mecanismo do [B-01](../backlog.md#b-01) segue intacto**: contexto pouco
  relevante, quase nenhuma citação, rebaixamento sistemático de emergências.
- **A correção do B1 funcionou no que prometia**: se a seed não estivesse
  valendo, a reescrita variaria em ~100% das linhas, e não em 8%.

## Deixado para depois

**Rodar `naive_rag --repeat 2` para testar a H1.** São cerca de 7 minutos e
daria a prova direta de que a instabilidade residual vem da etapa de
consulta. O cruzamento "mesmo contexto, mesma decisão, zero exceções" já é
forte, mas é prova indireta. Ficou de fora porque a pergunta desta rodada era
o critério do B-04, e misturar dois objetivos numa rodada é o que a regra de
uma mudança por rodada evita. Volta junto da próxima medição do trilho.

**Repetir com `--repeat 3`.** O critério do backlog fala em duas execuções, e
foi o que rodei. Com três daria para estimar se as 6 linhas instáveis são
sempre as mesmas ou se o conjunto muda a cada par de execuções — o que
distingue "6 linhas frágeis" de "6 sorteadas entre muitas candidatas".
Adiado por custo (mais 9,5 min) e porque não muda a conclusão: o critério de
zero já falhou.

**Investigar se `num_ctx=4096` mudou algo na consulta.** Verifiquei o
`num_predict` (não morde) mas não o tamanho de contexto, que antes ficava no
padrão do servidor. Só importaria se algum prompt de consulta passasse do
limite anterior, o que é improvável com relatos de duas linhas.

## Próximo passo

O B-04 volta ao time com resposta e com uma pergunta nova: o critério muda,
ou o item fica aberto? Enquanto isso não se decide, **a próxima entrega do B2
é a que já estava planejada — Chain-of-Thought** ([B-06](../backlog.md#b-06)),
e esta rodada não a atrapalha: o CoT será medido contra o preset `llm_only`,
que não usa a etapa de consulta e por isso é imune à instabilidade encontrada
aqui. A linha de base continua sendo 0,893 de acurácia balanceada, com 8
falsos não urgentes em 71.

O que muda para o CoT é uma cautela a mais, vinda da H1: se o raciocínio
passo a passo tornar a saída do classificador bem mais longa, ele pode
introduzir **na etapa de decisão** o mesmo não determinismo que hoje só
existe na consulta — justamente na etapa que esta rodada mostrou ser estável.
Por isso vou medir `llm_only + cot` com `--repeat 2` **antes** de comparar
acurácia, para não atribuir ao CoT um ganho que seja ruído.
