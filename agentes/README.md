# Agentes de construção

Roteiros para trabalhos que fazemos **uma vez** durante o desenvolvimento e
que ganham em velocidade e consistência quando um modelo de linguagem ajuda:
encontrar fontes para a base, organizar o que falta, preparar a ingestão.

**Estes agentes não fazem parte do sistema.** Não entram no `docker compose`,
não aparecem na matriz de ablação, não são citados na arquitetura do artigo.
Eles ajudam três pessoas a construir o projeto; quando a curadoria terminar,
param de ser usados. O que fica é o que produziram — as fontes, o mapa, a base
— e o registro de como foram usados.

O plano que deu origem a eles está em
[`docs/plano-base-e-prova.md`](../docs/plano-base-e-prova.md).

## Por que roteiro versionado, e não "pedir para a IA"

Três pessoas trabalhando em máquinas diferentes, em horas diferentes,
precisam produzir **o mesmo tipo de artefato**. Um roteiro escrito garante
que a lista de fontes do João e a do Vinicius tenham as mesmas colunas, as
mesmas regras e as mesmas recusas — sem isso, a curadoria vira três
curadorias.

É o mesmo motivo pelo qual as rodadas de avaliação têm um runner em vez de
comandos digitados na hora.

## Estrutura

```
agentes/
  README.md              <- este arquivo
  cartografo.md          <- roteiro completo de cada papel
  pesquisador.md
  redator-de-lacuna.md
  ingestao.md
.claude/agents/
  <papel>.md             <- atalho de poucas linhas que carrega o roteiro
```

O arquivo em `agentes/` é a **fonte de verdade** e não depende de ferramenta:
serve para colar no Claude Code, no claude.ai ou em qualquer outro assistente.
O arquivo em `.claude/agents/` existe só para invocar o papel pelo nome em
quem usa Claude Code, e aponta de volta para cá. O conteúdo não é duplicado.

## Os papéis

| Papel | Roda | Recebe | Produz | Usa LLM? | Estado |
|---|---|---|---|---|---|
| **Cartógrafo** | uma vez por revisão do mapa | régua de recuperação, fichas da base, backlog, referências de triagem | `data/curadoria/mapa-de-assuntos.csv` + `referencias.md` | sim | [roteiro pronto](cartografo.md); mapa rascunhado em 12/09, 61 linhas |
| **Pesquisador** | uma vez por quadro clínico | uma linha do mapa | `data/curadoria/fontes/<topic>.md` + captura e ficha, pelo script | sim, com busca na web | [roteiro pronto](pesquisador.md); piloto em 12/09 |
| **Redator de lacuna** | só quando não há fonte utilizável | a fonte que existe sobre o quadro | resumo do time, marcado `document_type: team_summary` | sim | roteiro a escrever |
| **Ingestão e retorno** | uma vez por lote aprovado | fontes aprovadas pelos especialistas | base atualizada + `compare.md` da régua + rascunho da evidência | **em parte** — ver abaixo | roteiro a escrever |

O último é o único em que modelo e script dividem o trabalho, e a fronteira
importa: **o script calcula, o agente conversa.** Os seis passos do ciclo ficam
empacotados num comando só, porque a base precisa sair **igual nas três
máquinas e conferível por hash** — um modelo escolhendo comandos na hora, ou
decidindo seções e reescrevendo metadados, quebraria as duas coisas. O agente
roda esse comando, diagnostica quando quebra, lê o `compare.md` pronto,
explica em linguagem simples, liga o resultado ao backlog e rascunha a
evidência da rodada.

Duas regras entram no roteiro dele antes de qualquer outra: **se uma
conferência falhar, para e conta — nunca contorna** (o perigo não é errar
conta, é "ajudar" rodando de novo sem a flag que recusou); e **número citado
aponta para o arquivo, não para a conversa**. É o mesmo princípio que o
projeto já segue: onde não precisa de LLM, não se usa — e onde se usa, ele não
produz o número, comenta o número.

## O que todo roteiro precisa ter

1. **Entrada** — exatamente o que o agente recebe.
2. **Saída** — o arquivo, com template e colunas.
3. **Regras** — o que aceitar e o que recusar.
4. **O que ele não faz** — a seção mais importante. Exemplos já definidos:
   o pesquisador não decide se um quadro é emergência (isso é do mapa e dos
   especialistas), não resume conteúdo clínico (aponta a fonte) e não aceita
   referência cujo link não abre.

## Para o texto do artigo

> A curadoria da base foi assistida por modelos de linguagem, com roteiros
> versionados no repositório. A seleção de assuntos e a aprovação de cada
> fonte foram feitas por médicos-veterinários; os agentes não fazem parte do
> sistema avaliado.
