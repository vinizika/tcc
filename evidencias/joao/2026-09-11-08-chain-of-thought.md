# Chain-of-Thought estruturado

**Data:** 11/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 8 ·
**Commits:** _(a preencher ao fechar)_

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

_(a preencher)_

## O que mudou no repositório

_(a preencher)_

## Observações

_(a preencher)_

## Deixado para depois

_(a preencher — e cada item vai também ao backlog)_

## Próximo passo

_(a preencher)_
