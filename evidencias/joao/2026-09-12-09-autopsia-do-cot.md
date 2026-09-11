# Autópsia do Chain-of-Thought

**Data:** 12/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 9 ·
**Commits:** _(a preencher)_

> Rodada de **análise**, sem código. Nenhum arquivo do sistema foi alterado
> e nenhuma medição nova foi executada: tudo aqui sai dos dados já gravados
> nas cinco rodadas de 11/09.

## O que foi feito

Uma releitura completa da [rodada 8](2026-09-11-08-chain-of-thought.md),
motivada por três perguntas do João: por que exatamente o Chain-of-Thought
falhou; o que no estado atual do projeto contribuiu para isso; e quais
caminhos existem, com ganhos e perdas de cada um.

A releitura incluiu uma **revisão adversarial** da minha própria análise, e
a comparação do que foi construído com o que o
[artigo do TCC1](../../docs/anotacoes.md) prometia. Ela achou seis
afirmações erradas na rodada 8 — corrigidas no
[adendo](2026-09-11-08-chain-of-thought.md#adendo-de-1209--correções-após-a-autópsia)
daquele arquivo — e cinco achados que mudam a leitura do projeto inteiro.

**Método**, para os números serem reproduzíveis: primeira repetição de cada
rodada; uma marcação por sinal por linha (a primeira, quando o modelo
repete); leitura por expressão regular sobre o campo `raciocinio` dos
`predictions.jsonl` em `data/evaluation/cited/20260911-*`.

## Por quê

A rodada 8 respondeu **o que** aconteceu: a acurácia balanceada caiu de
0,856 para 0,408 e a classe não emergência foi a zero. Não respondeu **por
que**, e a resposta que ela deu ("o modelo não calibra risco à vida") estava
incompleta — como o adendo mostra, ela explica uma parte e erra o resto.

Sem a causa correta, as três decisões seguintes seriam tomadas no escuro: o
que fazer com o Chain-of-Thought, como desenhar a entrega 6, e o que o TCC
pode afirmar. Uma delas é irreversível: o texto do artigo final.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Corrigir a rodada 8 por **adendo datado**, sem editar o texto original | O padrão da pasta diz que rodada fechada não se reescreve. E a trilha do erro tem valor: quatro das seis correções erravam a favor da minha própria leitura, o que é exatamente o viés que o registro existe para expor |
| 2 | Submeter minha análise a uma **revisão adversarial** antes de escrever | Numa autópsia o risco é se convencer da primeira explicação. Foi ela que achou as seis afirmações erradas — inclusive a causa principal, que eu tinha invertido |
| 3 | Verificar **cada** contestação nos dados antes de aceitar | Uma revisão também erra. Todas as afirmações checáveis se confirmaram; as contagens ficaram com o método declarado |
| 4 | Não mexer no prompt nesta rodada | Já foram três versões medidas nos mesmos 98 relatos. Continuar é ajustar ao conjunto de teste — o problema que virou [B-45](../backlog.md#b-45) |
| 5 | Ler o artigo do TCC1 de ponta a ponta e comparar com o construído | Metade das perguntas do João era sobre fidelidade ao plano. E a comparação revelou o achado 1 |

## O que eu esperava encontrar

_Escrito antes da releitura._

Esperava confirmar a explicação da rodada 8 e detalhá-la: que o modelo de 3
bilhões não calibra "risco à vida", que a regra "um sinal basta" amplifica
esse erro, e que claudicação é o termo mais responsável. Esperava também que
o braço com RAG tivesse falhado por excesso de contexto.

Não esperava descobrir que a causa principal fosse **outra**, nem que a
linha de base que eu vinha chamando de "melhor braço" fosse frágil, nem que
os braços com RAG não tivessem medido recuperação nenhuma.

## Por que o Chain-of-Thought falhou

Cinco camadas, da mais importante para a menos.

### 1. A rubrica pergunta o que o dado não tem

Os 98 relatos de avaliação são listas de sintomas: `Animal: Cat. Sintomas
observados: Nausea, Appetite Loss, Vomiting, Firm, Distended Stomach.`
**Não há gravidade, duração, intensidade ou evolução.** Perguntar "vômito
ameaça a vida?" sobre esse dado não tem resposta correta — depende de há
quanto tempo, com que frequência, com ou sem sangue.

O prompt de sistema já dizia, desde a rodada 3: *"se o relato não trouxer
informação suficiente para decidir, responda INCERTO"*. Essa frase é
**literalmente verdadeira nas 98 linhas**. O prompt anterior ao CoT nunca
tropeçava nela porque decidia pelo conjunto, sem se perguntar sinal a sinal.
O checklist obrigou o modelo a encarar cada sintoma isolado, e ele concluiu
o que a instrução mandava concluir.

A prova está na origem das abstenções:

| De onde vieram as 23 abstenções do braço principal | Linhas |
|---|---:|
| Tinha um "sim" marcado (a regra mandava EMERGENCIA) | **16** |
| Todas as marcações "não" (a regra mandava NAO_EMERGENCIA) | 5 |
| Só por "não sei" | 2 |

Em 21 das 23, o modelo **contrariou a própria regra do checklist** para
seguir a cláusula do prompt de sistema. Não foi desobediência aleatória: foi
obediência à instrução mais verdadeira das duas.

**A rubrica não era incompatível com o modelo. Era incompatível com o
formato da entrada.**

### 2. A regra só é obedecida na direção da urgência

| A regra, aplicada às marcações do modelo, aponta para | Linhas | Obedecida |
|---|---:|---:|
| EMERGENCIA | 89 | 73 (82%) |
| NAO_EMERGENCIA | 6 | **1 (17%)** |

O texto que escrevi tem três frases empurrando para a urgência — *"mesmo que
pareça exagerada"*, *"«não sei» nunca significa «não»"*, *"a ausência de
outros sintomas não torna o caso leve"* — e **nenhuma** na direção oposta.
As duas primeiras são minhas, do CoT; a terceira veio do prompt da rodada 3,
onde tinha sentido, porque lá o alvo eram os falsos não urgentes.

Consequência para o desenho: mesmo que o modelo marcasse todos os sinais
corretamente, a classe leve continuaria quebrada, porque o caminho até
"caso leve" está bloqueado por instrução.

### 3. Um termo derruba a classe leve inteira

Claudicação é marcada como risco à vida em **24 de 25** ocorrências. O
modelo a traduz como "dificuldade para andar", o que soa neurológico. Os
outros quatro termos leves ele marca bem: espirro 15 "não" contra 3 "sim",
secreção ocular 16 contra 3, secreção nasal 15 contra 6, lesão de pele 13
contra 3.

O problema é a combinação com a regra: **21 das 27 linhas leves contêm
claudicação**, e "um sinal de risco basta". Um único termo mal julgado
contamina 78% da classe.

O contrafactual mede o teto do desenho. Aplicando a regra **em código** às
marcações do próprio modelo, sem nenhuma desobediência:

| As 27 linhas leves, se a regra fosse aplicada em código | |
|---|---:|
| Classificadas como EMERGENCIA | 22 |
| Classificadas como INCERTO | 2 |
| **Corretas (NAO_EMERGENCIA)** | **3** |

Ou seja: com obediência perfeita, o resultado seria 3 acertos em 27. **O
teto do desenho já era ruim antes de o modelo desobedecer.**

### 4. As marcações não são julgamento — são racionalização

Este é o achado mais forte da rodada, e ele veio do braço de controle, que
existia exatamente para isso. O controle usa o mesmo prompt, mas escreve o
raciocínio **depois** da classificação.

| Sintoma | "sim" com raciocínio **antes** | "sim" com raciocínio **depois** |
|---|---:|---:|
| Fever | 2 de 23 | **22 de 23** |
| Diarrhea | 6 de 17 | 12 de 12 |
| Vomiting | 10 de 18 | 13 de 13 |

Mesmo modelo, mesmo sintoma, mesma pergunta. A marcação **inverte conforme a
classe que ele já escolheu**. Quando decide primeiro, ele escreve as marcas
que combinam com a decisão; quando marca primeiro, obedece às próprias
marcas.

Isso significa que **não existe uma escala clínica estável sendo
amplificada**. O que parecia julgamento é texto gerado para ser coerente com
o resto da resposta. É o fenômeno que a literatura chama de raciocínio
infiel, e ele **contradiz diretamente o que o artigo do TCC1 prometia** do
Chain-of-Thought: *"justificativas clínicas mais coerentes e transparentes
para os tutores"*. Coerentes, sim. Transparentes, não: elas descrevem uma
decisão que já estava tomada.

### 5. Sob prompt longo, o formato colapsa

No braço com recuperação, o passo que julga cada trecho aparece em **17 de
98** linhas. Nas outras, o modelo abandona o formato e responde em série:

```
Fever — não sei
Diarreia — não sei
Vômito — não sei
Perda de peso — não sei
```

O prompt desse braço tem 1437 tokens de média, contra 432 do braço base.
Some-se o vazamento de formato (21 de 98 linhas do braço principal, com a
resposta inteira dentro do campo de raciocínio) e o quadro é de um modelo
pequeno perdendo a estrutura conforme a instrução cresce.

## O Chain-of-Thought do artigo nunca foi testado

O artigo do TCC1 descreve o Chain-of-Thought em três passos:

> *"Essa abordagem busca estruturar a análise clínica de forma sequencial,
> envolvendo a identificação dos sintomas relatados, **a correlação com as
> evidências recuperadas** e a definição do possível nível de urgência."*

O passo do meio é a razão de o desenho fazer sentido com um modelo pequeno.
A lógica do artigo é: o modelo não precisa saber se vômito é grave, porque o
protocolo recuperado sabe; o raciocínio serve para ligar um ao outro.

**Esse passo nunca rodou.** No braço sem recuperação, por construção. No
braço com recuperação, porque a busca não trouxe nada relevante — e o passo
que julgaria os trechos apareceu em 17 de 98 linhas.

O que foi medido em 11/09 foi o julgamento clínico do modelo **sozinho**,
sem a muleta que o artigo desenhou para ele. Isso muda a frase que o TCC
pode escrever: não é "o Chain-of-Thought não funciona para triagem
veterinária"; é "o Chain-of-Thought sem conhecimento recuperado não funciona
neste modelo".

## Duas descobertas colaterais, e as duas são incômodas

### A linha de base é um atalho lexical

Venho chamando o braço sem RAG de "melhor configuração do projeto", com
0,856 de acurácia balanceada. Ele é frágil.

Das 27 linhas leves, **18 contêm espirro**. E o acerto depende disso:

| Braço | Linhas leves **com** espirro | **sem** espirro |
|---|---:|---:|
| Base (sem raciocínio) | 17 de 18 | 6 de 9 |
| Controle (com a rubrica) | 10 de 18 | **0 de 9** |

Os 4 falsos urgentes da linha de base são **todas** as combinações de lesão
de pele com claudicação. Ou seja: a classe leve, na prática, testa dois
tokens — o modelo aprendeu que espirro é leve e que claudicação é grave.

Isso não invalida as medições, mas muda o que elas significam. Junto com a
limitação já conhecida (a regra "só sintomas leves" acerta 98 de 98 sem
modelo nenhum), o que se pode dizer é: **o conjunto mede vocabulário, não
triagem**. Nem "a linha de base funciona" nem "o CoT falha" generalizam. O
que generaliza é a evidência de mecanismo — as marcações infiéis e a
obediência assimétrica.

### Os braços com RAG mediram ruído, não conhecimento

Este é o achado com maior consequência para o projeto inteiro.

| No braço `naive_rag`, sobre as 98 linhas | |
|---|---:|
| Similaridade máxima média | **0,574** |
| Linhas em que algum trecho passou do limiar de 0,70 | **0 de 98** |
| Linhas que receberam 3 trechos no prompt | **98 de 98** |

A busca **nunca** encontrou um trecho que ela própria considerasse
relevante. E, mesmo assim, três trechos entraram em todos os prompts, porque
o corte configurado (`context_min_score`) é **zero**.

Portanto, quando as evidências do projeto dizem "com a base atual, ligar o
RAG degrada o sistema em 20 pontos", o que foi medido é: **injetar três
trechos irrelevantes no prompt degrada o sistema em 20 pontos**. Com o corte
aplicado, o braço com RAG seria idêntico ao braço sem RAG.

Isso reenquadra o [B-01](../backlog.md#b-01) e torna o
[B-11](../backlog.md#b-11) urgente: enquanto o corte for zero e a base não
cobrir os assuntos do conjunto, **nenhuma medição com RAG mede recuperação**.

## O que teria mudado o resultado

| Fator | Teria salvado o CoT? | Por quê |
|---|---|---|
| **Base com protocolos relevantes** ([B-03](../backlog.md#b-03)) | É o pré-requisito do desenho do artigo | Sem ela o passo do meio não existe. Mas sozinha não basta: com 1437 tokens o formato colapsa neste modelo |
| **Corte de relevância maior que zero** ([B-11](../backlog.md#b-11)) | Pré-requisito para medir qualquer coisa com RAG | Hoje o sistema injeta ruído por configuração |
| **Relatos reais, com gravidade e duração** ([B-05](../backlog.md#b-05)) | **É a raiz da causa 1** | Com duração e intensidade, "isso ameaça a vida?" passa a ter resposta. Hoje não tem |
| **Relatos em português** ([B-15](../backlog.md#b-15)) | Parcialmente | A tradução de claudicação atrapalha, mas a linha de base lê o mesmo termo e acerta 17 de 21. Efeito maior na busca, onde consulta em inglês procura base em português |
| **Conjunto de desenvolvimento separado** ([B-45](../backlog.md#b-45)) | Não salvaria, mas tornaria as tentativas honestas | O prompt da rodada 3 foi afinado nos mesmos 98 relatos, de 0,572 para 0,893. O CoT teve duas iterações. Comparar prompt afinado com prompt cru, no conjunto da afinação, favorece o primeiro |
| **Modelo maior** ([B-42](../backlog.md#b-42)) | Desconhecido — é a única pergunta que só medição responde | Duas hipóteses fazem a mesma previsão nos dados atuais: "a técnica não serve" e "o modelo não sustenta a técnica" |

## As opções, com ganhos e perdas

| Opção | Ganho | Perda / risco | Custo |
|---|---|---|---|
| **Re-análise dos logs** (feita nesta rodada) | Cinco achados e seis correções, direto para o TCC | Nenhuma | Zero |
| **Teste limpo da ordem** ([B-46](../backlog.md#b-46)) | Isola "a ordem importa" com **uma** variável: mover `sinais_de_alerta` para antes de `classificacao`, sem tocar no texto. A comparação de 11/09 mudou texto, campo e tamanho juntos | Responde pouco se o efeito for pequeno | ~4 min |
| **Modelo maior, como diagnóstico** | Separa técnica de modelo; é a frase que a banca vai cobrar | Não é implantável (o artigo declara o modelo pequeno); com o conjunto separável, o braço sem CoT tende ao teto e sobra pouco espaço para mostrar ganho | ~1 h, 5 GB, **decisão do time** |
| **Âncoras de calibração no prompt** | Atacaria a causa de claudicação | **Inviável neste conjunto**: os 5 termos leves *são* a classe leve, então qualquer exemplo que os cite é vazamento por construção. Depende do B-45 e do B-05 | — |
| **Camada de decisão determinística** | O modelo só extrai e normaliza sinais; uma lista de sinais de alerta, tirada dos protocolos e validada pela especialista, decide. É o que o próprio artigo defende ao citar que listas estruturadas superam a triagem intuitiva | Neste conjunto colapsa na regra trivial que acerta 98 de 98 — avaliação circular. O valor real só aparece com relatos livres | Média |
| **Traduzir os relatos** | Testa a hipótese de claudicação; ajuda mais a busca | Efeito parcial na decisão | Baixa, depende de revisão da especialista |
| **Arrumar o RAG antes de tudo** | Sem isso, nenhum braço com recuperação mede o que diz medir | É trilho A, não meu | — |

## O que é defensável dizer no TCC

**Pode-se afirmar**, com os dados:

> Em `llama3.2:3b`, um Chain-of-Thought estruturado com rubrica por sinal e
> agregação do tipo "um sinal de risco basta" degradou a triagem de relatos
> em formato de lista, sem informação de gravidade ou duração. Quatro
> mecanismos foram medidos: (i) a rubrica exige um julgamento que a entrada
> não permite, e o modelo abstém-se em 21 das 23 vezes contrariando a
> própria regra; (ii) a regra é seguida em 82% das vezes quando aponta para
> urgência e em 17% quando aponta para caso leve; (iii) no braço de
> controle, as marcações invertem conforme a classe já decidida (febre como
> risco à vida: 2 de 23 contra 22 de 23), o que indica racionalização e não
> julgamento; (iv) 21 de 98 respostas apresentaram colapso de formato.

**Não se pode afirmar:** que o Chain-of-Thought não ajuda em triagem
veterinária (o desenho do artigo, com evidências recuperadas, nunca foi
testado); que o modelo pequeno é a causa (sem o diagnóstico comparativo);
nem que a linha de base "funciona" (ela é um atalho lexical).

**Deve-se registrar:** que o conjunto de avaliação mede vocabulário, e que
os braços com recuperação mediram injeção de ruído.

## Ressalvas estatísticas

- **Granularidade.** Uma linha leve vale 1,85 ponto de acurácia balanceada.
  O ruído entre sessões, sem nenhuma mudança, já custou 3,7 pontos
  ([B-43](../backlog.md#b-43)). Diferenças abaixo de ~5 pontos não se
  distinguem de ruído; os 45 desta campanha, sim.
- **Independência.** O teste de McNemar assume pares independentes, e as 27
  linhas leves são 15 combinações quase duplicadas, 21 delas com o mesmo
  termo. A significância não está em questão; a **generalização** está.
- **Direção do erro.** Abstenção conta como erro nas duas classes, mas
  abster-se diante de uma emergência é o erro seguro. Os dois números estão
  separados no relatório desde a rodada 8.

## O que mudou no repositório

Nenhuma linha de código. Apenas documentação:

| Arquivo | Mudança |
|---|---|
| `evidencias/joao/2026-09-11-08-chain-of-thought.md` | adendo com as seis correções; **nada acima dele foi editado** |
| `evidencias/joao/2026-09-12-09-autopsia-do-cot.md` | **novo** — esta rodada |
| `evidencias/backlog.md` | B-01, B-03, B-05, B-06, B-11 e B-41 atualizados; B-44, B-45 e B-46 criados |
| `evidencias/joao/planejamento.md` | três bloqueios novos; entrega 6 a decidir |
| `evidencias/joao/README.md` | linha desta rodada |

## Observações

**1. A revisão adversarial se pagou, e é o processo que recomendo repetir.**
Ela achou seis afirmações erradas, e **quatro delas erravam a favor da minha
própria leitura**. Sem ela, o TCC afirmaria que a regra "amplifica
fielmente" um julgamento — uma frase elegante e falsa. Numa autópsia, quem
escreveu o código não é o melhor juiz do que aconteceu.

**2. Três versões de prompt foram medidas no conjunto de avaliação.** A
terceira foi revertida por piorar. Isso é ajuste ao conjunto de teste, e
contamina qualquer comparação futura no mesmo conjunto. Virou
[B-45](../backlog.md#b-45), e é pré-requisito de qualquer tentativa nova.

**3. O achado do RAG é maior que o do CoT.** Que a busca nunca passe do
próprio limiar, e que o sistema injete três trechos assim mesmo, afeta todas
as medições com recuperação do projeto — inclusive as do Marco 1, em
setembro. O [B-11](../backlog.md#b-11) está aberto desde 04/09.

**4. O artigo promete coisas que o código não tem**, e isso precisa de um
parágrafo no TCC2, não de uma correção de código: LangChain, LightRAG e
grafo de conhecimento, re-ranking por modelo de relevância cruzada, RAGAs, e
os datasets como fonte de conhecimento. Virou [B-44](../backlog.md#b-44).
Sobre o último item, vale registrar que **a divergência foi uma melhoria**:
os datasets são a prova, e usá-los como base faria o sistema acertar
copiando.

**5. Um cuidado para a curadoria da base.** Os 5 sintomas leves do conjunto
foram escolhidos pela especialista. Se algum protocolo da base disser
"estes 5 são leves", o RAG passa a acertar a prova por construção, e a
medição perde o sentido. Protocolos reais sobre quadros leves, sim; a chave
de resposta, não.

**6. A rodada 8 continua de pé no essencial.** Os números centrais não se
moveram. O que mudou foi a explicação — e a diferença entre "o modelo não
calibra" e "a rubrica pergunta o que o dado não tem" é a diferença entre
tentar consertar o prompt e tentar consertar o conjunto.

## Deixado para depois

**O teste limpo da ordem** ([B-46](../backlog.md#b-46)), já aprovado pelo
João. Ficou fora desta rodada porque ela é de análise e não roda modelo;
entra na próxima entrega de código.

**A leitura qualitativa das 39 linhas que mudaram entre a base e o CoT.**
Cobri os cinco termos leves, as abstenções e o braço com RAG. O caminho
completo linha a linha é material direto para a seção de resultados do
artigo, e os dados estão em `cited/`. Adiado por tempo, não por dúvida.
Entra no [B-44](../backlog.md#b-44), junto da escrita.

## Próximo passo

**A decisão sobre a entrega 6 fica com o João**, com esta análise na mão,
como ele pediu. As duas alternativas mudaram de peso:

- **Self-Refine como planejado** perdeu força. Ele pede ao modelo que revise
  a própria decisão, e esta rodada mostra que o que o modelo escreve sobre a
  própria decisão é racionalização (achado 4). A trava de segurança, que é
  determinística, continua valendo.
- **Camada de decisão determinística** ganhou força, e o próprio artigo a
  sustenta ao citar que listas estruturadas de critérios superaram a triagem
  intuitiva de profissionais. Mas ela não pode ser **avaliada** neste
  conjunto sem circularidade.

Em qualquer um dos caminhos, o mesmo pré-requisito aparece: enquanto a base
não cobrir os assuntos do conjunto e o corte for zero, medir o sistema
completo mede ruído. Isso é trilho A, e é o que o João leva ao time.


---

## Adendo de 12/09 — as três correções, em linguagem simples, e uma hipótese em espera

> Escrito no mesmo dia, depois de fechar a rodada, a partir da conversa em
> que o João e eu chegamos à conclusão sobre prioridades. Nada acima foi
> editado. Este adendo existe por dois motivos: a conclusão sobre a **ordem**
> das correções não estava escrita em lugar nenhum, e uma das correções
> tinha o dono errado no backlog — o dono era eu.

### A analogia que organiza tudo

O sistema é um **aluno** fazendo uma **prova** de 98 questões, com direito a
consultar um **livro**. Um **bibliotecário** procura no livro as três páginas
mais parecidas com cada questão e entrega ao aluno antes de ele responder.

Nessa analogia, os três problemas são:

| Peça | O que está errado hoje | Item |
|---|---|---|
| O livro | Não tem os capítulos que a prova pergunta | [B-03](../backlog.md#b-03) |
| O bibliotecário | Entrega três páginas mesmo quando nenhuma tem a ver com a questão | [B-11](../backlog.md#b-11) |
| A prova | Dá para gabaritar sem saber veterinária, só pelo vocabulário | [B-05](../backlog.md#b-05), [B-45](../backlog.md#b-45) |

### Correção 1 — o livro: cobertura, não tamanho

O livro tem sete capítulos, todos sobre emergências, todos sintéticos, nenhum
validado. Nas 98 questões da prova, **nenhuma página passou da nota mínima
de parecença**. O livro não fala dos assuntos da prova.

A frase "aumentar a base" é a frase errada. O artigo científico sobre
insolação, já preparado, é o exemplo: acrescentaria 186 páginas ao livro e
**nenhuma questão da prova tem insolação**. Setenta protocolos de emergência
não ajudariam mais que sete. O que falta é: capítulos sobre os assuntos que
aparecem nas 98 questões, **incluindo os quadros leves**, em português,
validados pela especialista. Quinze capítulos certos valem mais que cem
errados.

Um cuidado, repetido de propósito: os cinco sintomas leves da prova foram
escolhidos pela especialista. Um capítulo que diga "estes cinco são leves"
faz o aluno acertar a prova copiando a chave de resposta. Capítulos reais
sobre quadros leves, sim; a lista dos cinco, não.

**Dono:** trilho A e a especialista. **Custo:** semanas, e a agenda da
especialista é o gargalo.

### Correção 2 — o bibliotecário: o corte em zero, e metade dele é meu

O bibliotecário tem uma régua de parecença de 0 a 1 e um combinado: **só
vale entregar página que passe de 0,70**. Nas 98 questões, a melhor página
ficou em média em 0,57. Pelo combinado, ele deveria voltar de mãos vazias
em todas.

Mas ele entrega três páginas mesmo assim, sempre. Por dois motivos, em dois
lugares:

1. **Do meu lado**, a configuração `CONTEXT_MIN_SCORE` está em **zero**. Eu
   a coloquei assim de propósito, na rodada 3, e o motivo está escrito no
   código: naquele dia nenhum documento passava do limiar, e descartar todos
   faria o braço "com livro" ficar idêntico ao braço "sem livro". Deixei as
   páginas entrarem e mandei registrar a nota de cada uma, para a decisão
   virar evidência depois. Virou — esta rodada é a evidência.
2. **Do lado do trilho A**, a busca tem uma trava parecida: quando nada passa
   de 0,70, ela devolve os mais próximos assim mesmo, com um aviso no log.

O efeito colateral, que só agora ficou visível em número: o aluno recebe
três páginas que não têm a ver com a questão e as lê como se tivessem. É
isso que derruba a nota dele em 20 pontos. **"O RAG piora o sistema" mede
"entregar três páginas aleatórias piora o sistema."** Consulta ao livro
nunca aconteceu.

A correção é o bibliotecário voltar a respeitar o combinado: nada passou,
nada entra. É uma linha do meu lado e uma trava do lado dele. Mas tem um
custo que precisa estar escrito **antes** de alguém aplicar: com o livro
atual, ele vai voltar de mãos vazias em 98 de 98, e **o braço com RAG
desaparece das medições**, porque vira idêntico ao braço sem RAG. Parece
perda. É o retrato verdadeiro do estado de hoje.

Por que esta correção vem **antes** da base: enquanto o corte for zero,
qualquer base nova será medida junto com o ruído, e não dá para separar
quanto foi o livro e quanto foi o lixo que entrou.

**Dono:** B2 e trilho A, meia parte cada. **Custo:** uma configuração de
cada lado. **Decisão do time:** o que o classificador recebe quando não há
nada relevante — a resposta proposta é "nada".

### Correção 3 — a prova: questões que não se gabaritem por vocabulário

Das 98 questões, as 27 de "não emergência" foram montadas com as mesmas
cinco palavras. As 71 de emergência usam 192 palavras diferentes. A regra
"se só tem palavra da lista de cinco, é leve" acerta **98 de 98** sem saber
nada de veterinária.

Consequência: quando o aluno tira 0,856, não dá para saber se ele aprendeu
triagem ou se aprendeu que espirro é leve. Esta rodada mostrou que foi o
segundo: ele acerta 17 das 18 questões leves com espirro e 6 das 9 sem.

E é isso que faz a prova ser irmã gêmea da base. Se o livro ficar perfeito e
o aluno tirar 0,95, **a prova continua a mesma**, e continuamos sem saber se
o número significa triagem. A base destrava construir; a prova destrava
saber se construiu certo.

Foi também a prova que derrubou o Chain-of-Thought em primeiro lugar: o
formulário perguntava "isso ameaça a vida?" sintoma por sintoma, e a questão
dizia só "vômito", sem há quanto tempo nem como. O aluno respondeu "não dá
para saber" e estava certo.

O que resolve: relatos de tutor reais, com duração e intensidade, em
português, e um conjunto de desenvolvimento separado do de avaliação, para o
ajuste de prompt parar de ser feito na prova. Os 18 relatos em português que
o trilho B1 escreveu para o benchmark de voz são uma semente.

**Dono:** time e a especialista, o mesmo gargalo. **Custo:** semanas, em
paralelo com a base.

### A ordem, e o que não fica parado

| Quando | O quê | Quem |
|---|---|---|
| Agora | Corte: sem relevância, sem trechos | B2 + A, decisão do time |
| Esta semana | Régua de recuperação, com os sete protocolos que existem | A |
| Próximas semanas | Livro com cobertura dos assuntos da prova, quadros leves incluídos | A + especialista |
| Em paralelo | Prova nova, com gravidade e duração, em português | Time + especialista |
| Depois | Virada da base, remedição dos braços com RAG, e só então o CoT como o artigo desenhou | Cada trilho |

O que **não** depende disso e pode andar: o Whisper e o trilho de voz; a
régua de recuperação, que pode nascer com os sete protocolos; meu
instrumento; o diagnóstico com modelo maior ([B-42](../backlog.md#b-42)); o
teste limpo da ordem ([B-46](../backlog.md#b-46)).

### Hipótese em espera: uma camada de decisão determinística

> **Status: stand-by.** Não é decisão nem candidata em disputa. É uma
> possibilidade avistada durante a autópsia, registrada para não se perder.
> O João avaliou que é cedo para decidir sobre ela. Ela volta à mesa em dois
> casos: se as três correções acima não bastarem para o sistema decidir bem,
> ou como um braço a mais na ablação do artigo, para fundamentá-la.

**Não estava no artigo.** O desenho do artigo é o modelo decidir, apoiado na
busca, com CoT e Self-Refine melhorando o raciocínio dele. A hipótese nasceu
de três coisas: do resultado desta rodada (o modelo lista os sinais bem e
julga a gravidade mal e de forma inconsistente); da trava de segurança que o
Self-Refine já previa em código, levada até o fim; e das próprias referências
do artigo, que citam uma lista estruturada de critérios vencendo a triagem
intuitiva de veterinários.

**O que é.** Hoje o modelo faz dois trabalhos na mesma resposta: entender o
relato e julgar a gravidade. A hipótese separa os dois. O modelo continua
fazendo o primeiro — extrai os sinais num vocabulário fixo — e para de fazer
o segundo: uma tabela de sinais de alerta, escrita pela especialista a partir
dos protocolos da base, decide em código, sempre da mesma forma. O modelo
volta no fim só para explicar ao tutor a decisão já tomada, citando o
protocolo de onde veio o critério. É a enfermeira de triagem: ela escuta,
mas o cartão de critérios decide.

**O que mudaria.** Pouco nos arquivos, bastante no significado. Só a etapa
de decisão muda: uma extração estruturada, um módulo de regras pequeno, uma
tabela que mora junto da base, uma chave para ligar e desligar. Voz,
consulta, busca e resposta ficam iguais. A régua ganharia uma métrica nova e
não circular: se o modelo extraiu os sinais certos, verificável direto
contra os sintomas de cada linha da prova. A história do projeto mudaria de
ênfase, de "o modelo decide com apoio da base" para "o modelo entende, a
regra decide, a base fundamenta" — e isso é decisão do orientador, não só
nossa.

**O que ela não resolve.** Na prova atual, colapsa na regra trivial que
acerta 98 de 98: avaliação circular. Um sinal fora da tabela vira "incerto",
o que é seguro mas reduz cobertura. E se o modelo ler o sinal errado, a regra
decide sobre o sinal errado. Ela **depende** das três correções acima —
principalmente do livro, de onde a tabela sairia — e não as substitui.

**Como encaixaria sem quebrar o artigo, se um dia for retirada da espera:**
como braço da ablação, "decisão por regra sobre sinais extraídos pelo
modelo", medida lado a lado com "decisão pelo modelo", que é o desenho
original. Os dois continuam existindo; o número decide.
