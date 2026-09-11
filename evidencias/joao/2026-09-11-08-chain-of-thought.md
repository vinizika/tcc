# Chain-of-Thought estruturado

**Data:** 11/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 8 ·
**Commits:** c94969e (backend), e4da997 (régua), + este

> **Nota de processo, escrita antes de tudo.** O padrão desta pasta manda
> criar o arquivo da rodada **antes de codar**, com o "Resultado esperado"
> preenchido. Eu não fiz: comecei pelos schemas e criei este arquivo depois
> do backend pronto, já com cinco relatos testados contra o modelo. As
> previsões abaixo **não** foram escritas agora de memória — são cópia literal
> do [plano aprovado](https://github.com/vinizika/tcc) antes de qualquer
> código, e o que já foi observado está separado, na seção "O que os cinco
> relatos mostraram". Nenhuma medição da régua foi executada até aqui.
> O desvio fica registrado porque a regra existe justamente contra a memória
> seletiva — a [rodada 4](2026-09-04-05-runner-de-avaliacao.md) é a prova:
> as duas previsões principais saíram erradas, e foi disso que veio o achado.

## O que foi feito

A chave `cot_enabled`, que até agora era recusada com erro 400 de propósito,
passa a funcionar. Com ela ligada, o modelo preenche um campo de raciocínio
**antes** de classificar, seguindo um checklist fixo; sem ela, nada muda.

Entram quatro formatos de saída, dois prompts de sistema, a chave
`cot_position` (que move o raciocínio para depois da conclusão, no braço de
controle) e a recusa de `cot_enabled` junto de `structured_output_mode=json`.

## Por quê

**O erro que mais importa é o falso não urgente**, e ele é o item
[B-06](../backlog.md#b-06): deixar passar como leve um animal que precisava
de atendimento. No melhor braço de hoje são 8 em 71; com RAG, 30 em 71.

**Ele tem uma forma conhecida.** Lendo as justificativas das oito linhas
erradas da linha de base (`llm_only`, 04/09), aparecem duas naturezas:

| Linhas | Natureza | O que o modelo fez |
|---|---|---|
| 16, 43, 66 | **Falha de regra** | listou o sinal grave e **depois** rebaixou o caso por "faltam informações sobre a gravidade ou a duração" |
| 42, 56, 58, 64, 69 | **Rótulo discutível** | casos dermatológicos, crônicos ou de via aérea alta, que o conjunto marca como emergência |

O denominador comum do primeiro grupo é tratar **falta de informação como
prova de leveza** — e o prompt já manda responder INCERTO nesse caso. É
contra isso que o checklist foi desenhado.

**Por que checklist, e não "pense passo a passo".** Num teste direto com este
modelo, antes de escrever qualquer código, o raciocínio livre produziu
"condição médica grave… risco de choque" e **mesmo assim** classificou como
NAO_EMERGENCIA. Raciocinar antes, sozinho, não aplica a regra. O checklist
termina com a regra de decisão explícita sobre o que foi marcado.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Checklist estruturado: uma linha por sinal (`sinal — risco à vida? sim/não/não sei`), uma por trecho quando há contexto (`[n] — descreve o caso deste relato?`), e uma conclusão aplicando a regra | O raciocínio livre chegou à conclusão errada no teste de portão. O limite é **estrutural** (uma linha por item), e não "até N frases": um modelo de 3B não conta frases de forma confiável |
| 2 | `raciocinio` declarado **primeiro**, em classes independentes e não subclasses | O conversor de gramática do Ollama emite os campos na ordem declarada — verificado em chamada real. Subclassificar poria o campo novo no fim, que é o oposto do desejado |
| 3 | Teto de 1500 caracteres no `raciocinio` | Rede de segurança contra repetição degenerada: cortado pela gramática, o modelo ainda emite a decisão. Sem teto, o retry dobraria o orçamento, repetiria o mesmo prefixo e devolveria JSON inválido. Verificado que a gramática respeita o teto à letra |
| 4 | Braço de **controle** com o raciocínio por último (`cot_position=last`) | Separa "a ordem importa" de "a rubrica importa". Se o controle empatar com o principal, a afirmação defensável no TCC é "checklist estruturado", não "chain-of-thought" |
| 5 | Dois prompts completos por braço, montados a partir dos existentes | A descrição do campo precisa aparecer na mesma posição em que o schema o declara; e o passo dos trechos não faz sentido sem contexto |
| 6 | `cot_enabled` com `structured_output_mode=json` devolve 400 | Sem a gramática a ordem não é garantida — e a ordem é o experimento. O braço não mediria nada |
| 7 | `v0_legacy` força `cot_enabled=False` | Aquele braço reproduz a medição de 04/05, feita sem raciocínio nenhum |
| 8 | O raciocínio **não** aparece na resposta ao tutor | Decisão do João: é pensamento interno de um modelo de 3B, com especulação clínica. Fica em `triage.raciocinio`, para auditoria e para a régua |
| 9 | `num_predict=1024` nos presets CoT, sem setting nova | O raciocínio é mais verboso. A linha de base nunca passou de 238 tokens com teto de 600, então o teto nunca mordeu e ela segue comparável |
| 10 | O critério do B-06 é **de engenharia**; McNemar entra como guarda contra superinterpretar | Com 8 falsos não urgentes, mesmo o sucesso total são 8 linhas discordantes. No cenário realista o valor-p fica acima de 0,12 — pré-registrar evita afirmar no TCC uma melhora que o próprio instrumento nega |

## Resultado esperado

_Cópia literal do plano aprovado antes de qualquer código. Nenhuma rodada da
régua foi executada até aqui._

| # | Rodada | Repetições | Esperado |
|---|---|---|---|
| M0 | `llm_only` no commit atual | 1 | **Idêntica à de 04/09, linha a linha** — a etapa de decisão é determinística. Se diferir, o refactor mexeu no prompt sem querer e eu paro tudo |
| M1 | `llm_only_cot` | 3 | Instabilidade entre 0 e 4 linhas. Saídas inválidas: zero. **Falsos não urgentes de 8 para 5 ± 1** (as três falhas de regra); falsos urgentes até 4; balanceada acima de 0,89. Saída de ~300 tokens, geração de ~3,5 s |
| M2 | `llm_only_cot_posthoc` | 1 | **Igual ou pior que M1.** Se empatar, o ganho veio da rubrica e não da ordem |
| M3 | `naive_rag` no commit atual | 1 | Idêntica à de 04/09, mesma razão de M0 |
| M4 | `naive_rag_cot` | 1 | **Efeito maior que em M1**: dos 30 falsos não urgentes com RAG, 23 são induzidos pelo contexto, e o passo dos trechos mira neles. Espero de 30 para algo entre 15 e 22 |

**Contrastes pré-registrados:** primário M1 contra M0; secundário M4 contra
M3; exploratório M1 contra M2.

**Pré-condições para a leitura valer:** saídas inválidas em zero, como na
linha de base — uma emergência que vire JSON inválido sai da conta de falsos
não urgentes e o braço "passa" por engano. E a instabilidade precisa ser
menor que o efeito medido, senão o que se está lendo é ruído.

**O teto realista, dito antes:** o critério oficial do B-06 é falsos não
urgentes até 4. Como cinco das oito linhas são de rotulagem discutível, e
17 das 27 não emergências contêm lesão de pele, atingir 4 provavelmente
exige a revisão dos rótulos ([B-05](../backlog.md#b-05)), não o CoT. A
expectativa honesta é 5.

## O que os cinco relatos mostraram

_Observado **depois** do backend pronto e **antes** de qualquer rodada da
régua. Cinco linhas escolhidas a dedo não são medição; estão aqui porque
uma delas mudou o código._

**As três linhas-alvo foram corrigidas.** A linha 66 (gata com náusea,
vômito e abdômen distendido), que a linha de base classificava como não
emergência, passou a sair como emergência, com o raciocínio marcando
`Vomiting — risco à vida? sim`.

**Um defeito de formato apareceu e foi corrigido antes de medir.** Na linha
43 o modelo escreveu a resposta inteira **dentro** do campo de raciocínio,
repetindo ali classificação, justificativa e recomendação. Custava 371
tokens e poluía a auditoria. A correção foram duas linhas no prompt dizendo
que aquele campo contém apenas a análise. Depois dela, nenhum vazamento, e a
linha 43 passou a acertar com a conclusão explícita.

Registro isto como **correção de clareza, não ajuste de desempenho**, e é uma
distinção que o TCC precisa sustentar: o defeito era de formato, aparecia na
estrutura da saída, e a correção não olhou para acurácia.

**Um efeito novo, ainda sem tamanho.** As duas não emergências testadas
passaram a sair como **INCERTO**, usando a saída "não sei" do checklist. É
clinicamente mais seguro e metricamente pior, porque abstenção conta como
erro em todas as acurácias. **Parei de ajustar aqui de propósito**: continuar
mexendo no prompt com base em cinco linhas seria calibrá-lo no conjunto de
teste. O tamanho disso é pergunta para a rodada completa.

**Isso corrige uma previsão minha que nasceu incompleta.** Eu havia
pré-registrado medir "emergência que virou incerto", o erro seguro. Os
relatos mostraram o movimento contrário — não emergência virando incerto,
que é abstenção em caso fácil. A métrica vai contar **as duas direções**.

## Resultado obtido

**O Chain-of-Thought atingiu o alvo do B-06 e inutilizou o sistema.** Os
falsos não urgentes caíram de 8 para 1 em 71 — o critério pedia 4 ou menos.
No mesmo movimento, a classe não emergência foi a **zero**: das 27 linhas
leves, nenhuma foi classificada corretamente. A acurácia balanceada caiu de
0,856 para 0,408.

É um resultado negativo, e ele é o achado desta rodada.

### As cinco rodadas

Todas com 98 linhas, base de 18 trechos (`eeba9f51…`), árvore limpa,
commit `e4da997`.

| Braço | Balanceada | Estrita | FNU | FU | E→INC | N→INC | Cobertura |
|---|---:|---:|---:|---:|---:|---:|---:|
| [M0 `llm_only`](../../data/evaluation/cited/20260911-144739_m0_llm_only/report.md) | 0,856 | 0,857 | 8 | 4 | 2 | 0 | 0,980 |
| [M1 `llm_only_cot`](../../data/evaluation/cited/20260911-145537_m1_llm_only_cot/report.md) | **0,408** | 0,592 | **1** | **16** | 12 | 11 | 0,765 |
| [M2 controle post-hoc](../../data/evaluation/cited/20260911-151445_m2_posthoc/report.md) | 0,664 | 0,796 | 3 | 17 | 0 | 0 | 1,000 |
| [M3 `naive_rag`](../../data/evaluation/cited/20260911-145110_m3_naive_rag/report.md) | 0,768 | 0,663 | 30 | 0 | 3 | 0 | 0,969 |
| [M4 `naive_rag_cot`](../../data/evaluation/cited/20260911-152057_m4_naive_rag_cot/report.md) | 0,389 | 0,398 | 22 | 0 | 20 | 17 | 0,622 |

`E→INC` e `N→INC` são as abstenções por classe, a métrica que nasceu nesta
rodada. `FNU` e `FU` são os falsos não urgentes e os falsos urgentes.

O número que resume tudo está no recall por classe do M1:

| | Recall EMERGENCIA | Recall NAO_EMERGENCIA |
|---|---:|---:|
| M0, sem raciocínio | 0,859 | 0,852 |
| M1, com raciocínio | 0,817 | **0,000** |

**Contraste primário, M1 contra M0:** −44,7 pontos de acurácia balanceada.
McNemar pareado 29 contra 3, valor-p abaixo de 0,0001. Intervalo de 95% da
diferença de acurácia estrita: de −36,7 a −16,3 pontos. Não é ruído.

### Por que aconteceu

O checklist tem uma regra: um sinal marcado como risco à vida leva a
emergência; nenhum risco e alguma dúvida levam a incerto. A regra está
correta. **O problema é que o modelo de 3 bilhões de parâmetros não sabe
julgar "risco à vida" de forma calibrada.**

Contando como ele marcou os cinco sinais que definem a classe leve, no M1:

| Sinal | "sim" | "não sei" | "não" |
|---|---:|---:|---:|
| **Lameness** (mancar) | **20** | 2 | 3 |
| Eye discharge | 1 | 5 | 18 |
| Skin lesions | 1 | 5 | 13 |
| Sneezing | 0 | 4 | 15 |
| Nasal discharge | 1 | 0 | 15 |

**Mancar é julgado risco à vida em 20 de 25 vezes.** Quatro dos cinco sinais
ele marca bem, mas a regra "um sim basta" transforma um único erro de
marcação em emergência — e claudicação aparece em boa parte das linhas leves.

A segunda perda vem do "não sei". Ele aparece de 4 a 5 vezes em cada sinal
leve, e a regra converte qualquer hesitação em abstenção. Daí as 11 não
emergências que viraram incerto.

Ou seja: **a regra amplifica fielmente um julgamento clínico que o modelo não
tem.** Um checklist é tão bom quanto quem o preenche.

### A ordem não ajudou. Atrapalhou.

Era a hipótese central: escrever o raciocínio **antes** faria a conclusão
seguir a análise. O controle, com o raciocínio depois, existia para separar
o efeito da ordem do efeito da rubrica.

| | Balanceada | FNU | FU | Cobertura |
|---|---:|---:|---:|---:|
| M1, raciocínio antes | 0,408 | 1 | 16 | 0,765 |
| M2, raciocínio depois | **0,664** | 3 | 17 | **1,000** |

O controle foi **melhor**, por 25,6 pontos, com McNemar 20 contra 0 e p
abaixo de 0,0001. A hipótese está refutada com o contraste que foi desenhado
para testá-la.

O mecanismo é visível: no M2 a cobertura é 1,000, não há uma única abstenção.
Escrevendo a conclusão primeiro, o modelo decide como decidia antes e o
raciocínio vira justificativa do que já foi decidido. Escrevendo o raciocínio
primeiro, ele **obedece** à própria marcação — inclusive quando ela está
errada.

**Mas o controle também piorou** em relação a não usar raciocínio nenhum:
0,664 contra 0,856, com os falsos urgentes subindo de 4 para 17. Então a
rubrica sozinha, mesmo sem a ordem, já empurra o sistema para a urgência. O
texto do prompt pesa mais do que a posição do campo.

### Com RAG, o formato degenera

No M4 o checklist tem um passo a mais, que julga cada trecho recuperado. Ele
aparece em **17 de 98 linhas**. Nas outras, o modelo abandona o formato e
responde "não sei" em série:

```
Fever — não sei
Diarreia — não sei
Vômito — não sei
Perda de peso — não sei
Desidratação — não sei
```

O resultado é a pior rodada já medida no projeto: balanceada 0,389, com 20
emergências viradas incerto e 17 não emergências também. A cobertura cai para
0,622 — o sistema se recusa a decidir em mais de um terço dos casos.

Vale registrar o que **não** aconteceu: os falsos não urgentes caíram de 30
para 22, e os falsos urgentes seguem em zero. O passo dos trechos pode ter
ajudado onde foi executado; não dá para saber, porque ele foi executado em
menos de um quinto das linhas.

### As previsões, uma a uma

| # | Previsão | Resultado |
|---|---|---|
| M0 idêntica à de 04/09 | ❌ **Errada**, mas por pouco: 96 de 98 linhas iguais. Ver o achado sobre determinismo abaixo |
| M1: FNU de 8 para 5 ± 1 | ❌ Errada. Deu **1** — melhor que o previsto, e é justamente o problema |
| M1: FU até 4 | ❌ **Errada, e é o centro do achado.** Deu 16 |
| M1: balanceada acima de 0,89 | ❌ Errada por larga margem. Deu 0,408 |
| M1: instabilidade até 4 linhas | ✅ Certa: 3 linhas, concordância 0,969 |
| M1: saídas inválidas em zero | ✅ Certa, e não por acaso — ver o teto abaixo |
| M2 igual ou pior que M1 | ❌ Errada. O controle foi **melhor**, refutando a hipótese da ordem |
| M4 com efeito maior que M1 | ❌ Errada. Foi a pior rodada do projeto |

Sete de oito erradas. A previsão que mais importava — falsos urgentes até 4 —
errou por 12 linhas, e é ela que transforma "o CoT funcionou" em "o CoT
inutilizou o sistema".

### Dois achados colaterais

**1. O teto de 1500 caracteres se pagou.** O comprimento do raciocínio no M1
tem mediana 173 caracteres, mas p95 de 1464 e máximo de **exatamente 1500** —
o teto mordeu. As linhas longas são repetição degenerada, com o modelo
repetindo o mesmo sinal com respostas diferentes:

```
Eye Discharge — risco à vida? não / Eye Discharge — risco à vida? não sei /
Skin Lesions — …
```

Sem o teto, essas linhas teriam consumido o orçamento de tokens, disparado o
retry e voltado como saída inválida. Com ele, a decisão ainda é emitida:
**saídas inválidas em zero nas cinco rodadas**. Era a decisão 3 do plano, e
foi a única precaução que o resultado confirmou.

**2. A etapa de decisão não é determinística entre sessões.** Comparando M0
com a rodada de 04/09, mesmo modelo, mesmo prompt, mesma base, mesma seed:

| | |
|---|---|
| Linhas com saída **byte a byte** idêntica | 31 de 98 |
| Linhas com a mesma classificação | **96 de 98** |

A rodada 6 mediu que a decisão era determinística **dentro** de uma mesma
execução, com zero exceções. Este é outro recorte: entre execuções separadas
por sete dias. O texto muda em dois terços das linhas, e a classificação
sobrevive em quase todas.

É a mesma assinatura de ruído numérico de GPU da hipótese H1 da rodada 6, e
ela não poupa a etapa de decisão — apenas raramente inverte o resultado. Vai
para o backlog, porque muda o que "reproduzir uma rodada" significa.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/schemas/triage_output.py` | quatro formatos de saída com raciocínio, dois por posição do campo |
| `backend/app/schemas/triage.py` | chave `cot_position` nas opções e na configuração efetiva |
| `backend/app/pipeline/config_resolver.py` | `cot_enabled` sai dos não implementados; legado força desligado; 400 sem gramática |
| `backend/app/prompts/triage.py` | o checklist, montado a partir dos prompts existentes |
| `backend/app/pipeline/chat_pipeline.py` | `_modelo_de_saida` escolhe o formato pelos três eixos |
| `backend/app/services/fingerprint_service.py` | três hashes de prompt novos |
| `scripts/run_evaluation.py` | grava `raciocinio` e `len_raciocinio`; `cot_position` nas opções válidas |
| `scripts/evaluation_metrics.py` | abstenção por classe; p95 e máximo dos tokens; tamanho do raciocínio |
| `scripts/report_evaluation.py` | compara só as chaves que as duas rodadas registram |
| `scripts/presets.json` | `llm_only_cot`, `llm_only_cot_posthoc`, `naive_rag_cot` |
| `data/evaluation/cited/` | as cinco rodadas desta campanha |
| testes | backend 109 → 123; scripts 68 → 71 |

Commits: `c94969e` (backend), `e4da997` (régua), e o desta evidência.

## Observações

**1. O critério do B-06 estava incompleto, e isso é culpa do critério.** Ele
pede falsos não urgentes até 4 **mantendo** falsos urgentes até 5. O CoT
entregou 1 e 16. Lido só pela primeira metade, "o CoT resolveu o B-06". A
segunda metade existia justamente para impedir essa leitura, e funcionou. Um
critério de um número só teria aprovado um sistema que classifica quase tudo
como urgente.

**2. O erro seguro tem limite, e ele é prático.** Mandar para o veterinário
todo animal que chega é clinicamente seguro e inútil: o projeto existe para
reduzir o gargalo das clínicas, e um triador que nunca diz "pode esperar" não
reduz gargalo nenhum. O M1 erra pouco no que é grave e erra tudo no que é
leve. Vale para o texto do TCC: acurácia balanceada não é preciosismo
estatístico, é o que impede chamar isso de melhoria.

**3. A rubrica pesa mais que a posição do campo.** O controle post-hoc
mostrou os dois efeitos separados: a ordem custou 25,6 pontos, e a rubrica
sozinha já custava 19,2 em relação a não ter raciocínio. Era a pergunta que o
braço de controle existia para responder, e ele respondeu.

**4. O checklist é uma aposta sobre o modelo, não sobre a técnica.** Um
modelo que soubesse julgar "risco à vida" seria ajudado pela regra. Este
marca claudicação como risco à vida em 20 de 25 vezes. A literatura de
Chain-of-Thought reporta ganhos em modelos grandes; um resultado nulo, ou
negativo, num modelo de 3 bilhões de parâmetros é resultado, não fracasso de
implementação. Esta é a leitura honesta para o artigo.

**5. Uma tentativa de ajuste foi feita e desfeita.** Depois de um smoke de 12
linhas mostrar que a conclusão faltava em 10 delas, o João autorizou ajustar
o prompt. O ajuste foi feito, medido nas mesmas 12 linhas, e **piorou**: a
conclusão passou a faltar em 9, mas o eco das opções subiu de 1 para 5 e os
acertos caíram de 6 para 5. Mais instrução na mesma frase confundiu o modelo
em vez de guiá-lo. Revertido para o estado commitado, conferido pelo hash do
prompt. Fica registrado como tentativa medida, não como algo não feito.

**6. A conclusão do checklist falta na maioria das linhas.** Em 33 de 98 ela
aparece. O modelo marca os sinais e pula a etapa que aplica a regra — embora
a classificação saia coerente com as marcações. Não afeta a acurácia; afeta a
auditoria, que era metade do valor do raciocínio.

**7. Duas linhas de 04/09 mudaram de classificação sem nada ter mudado.** As
linhas 843 e 845, ambas não emergências, viraram emergência. Com 96 de 98
iguais, é ruído e não regressão — mas é o mesmo ruído que faz uma rodada não
ser reproduzível ao pé da letra.

**8. O braço com RAG não conseguiu executar o checklist.** 17 de 98 linhas
julgaram os trechos. Com 1131 tokens de prompt médio, mais o checklist, o
modelo perde o formato. Se o passo dos trechos for retomado, provavelmente
precisa ser uma chamada separada, não um item a mais na mesma lista.

## Deixado para depois

**Testar o checklist com uma âncora de calibração** ([B-41](../backlog.md#b-41)).
O erro raiz é o modelo não calibrar "risco à vida" — marca claudicação como
risco em 20 de 25 vezes. Uma lista curta de exemplos no prompt ("mancar não é
risco à vida; convulsão é") ataca a causa, e não o sintoma. Ficou de fora
porque seria a quarta versão do prompt nesta rodada, e a terceira já foi
medida e revertida: sem um conjunto de desenvolvimento separado do de
avaliação, continuar ajustando é calibrar no conjunto de teste.

**Medir o CoT com um modelo maior** ([B-42](../backlog.md#b-42)). A hipótese
"a técnica não serve" e a hipótese "o modelo não sustenta a técnica" fazem a
mesma previsão nesta rodada. Um modelo de 8 bilhões rodando o mesmo prompt
separa as duas, e é a diferença entre o TCC dizer "CoT não ajuda triagem" e
"CoT não ajuda com modelo pequeno". Ficou de fora porque o projeto é
local-first com `llama3.2:3b` declarado, e trocar o modelo é decisão do time.

**Quantificar o ruído entre sessões** ([B-43](../backlog.md#b-43)). Sei que
67 de 98 linhas geram texto diferente e 2 mudam de classe, entre duas
execuções separadas por sete dias. Não sei se 2 é o número típico ou se deu
sorte. Repetir o `llm_only` em dias diferentes daria a faixa. Adiado por não
bloquear nada hoje: o efeito do CoT foi 20 vezes maior que esse ruído.

**Ler o raciocínio das 39 linhas que mudaram entre M0 e M1.** A leitura
qualitativa que fiz cobriu os cinco sinais leves e as linhas do braço com
RAG. Falta o caminho completo das linhas que o CoT virou, que é material
direto para a seção de resultados do artigo. Adiado por tempo, não por
dúvida; os dados estão em `cited/`.

## Próximo passo

**O CoT não entra no sistema.** A chave `cot_enabled` fica implementada,
desligada por padrão e medida — que é o que a matriz de ablação de outubro
precisa. O melhor braço do projeto continua sendo o prompt atual sem
recuperação, com 0,856 de acurácia balanceada.

O [B-06](../backlog.md#b-06) continua **aberto**. Ele não foi resolvido: a
técnica que estava planejada para resolvê-lo foi medida e reprovada. As duas
rotas que sobram estão no backlog como B-41 (âncora de calibração) e B-42
(modelo maior), e nenhuma delas é a entrega seguinte.

A entrega 6 do trilho é o **Self-Refine**, e esta rodada muda o desenho dele.
A ideia original era o modelo revisar a própria resposta e corrigi-la; o que
acabou de ser medido é que este modelo, quando recebe uma regra explícita e a
aplica, aplica mal — porque o julgamento clínico que a regra pressupõe não
está lá. Um Self-Refine que peça "revise sua decisão" tende ao mesmo
resultado. O que sobrevive do plano é a **trava de segurança**: a parte que
compara a revisão com o rascunho e recusa mudanças sem evidência literal no
relato ou nos trechos. Essa trava é código determinístico, não depende do
julgamento do modelo, e é a única parte do desenho que esta rodada não
enfraqueceu.
