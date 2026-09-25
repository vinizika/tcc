# Fontes para as frases sem fonte das fichas de busca

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2, na curadoria do time ·
**Rodada:** 27 · **Commits:** este

> Rodada de **curadoria**, feita em paralelo com as rodadas 23 a 26 por quatro
> agentes de IA pesquisadores, num worktree separado. Nenhum texto de ficha
> muda: a rodada procura, para as frases que os autores das fichas de busca
> marcaram como conhecimento geral, uma fonte que as sustente. Quem aprova
> cada fonte são os especialistas.

## O que foi feito

1. **As 53 frases `geral`** das fichas de busca
   ([rodada 19](2026-09-24-20-fichas-em-duas-camadas.md)), em 27 fichas,
   quase todas da etapa 2. São frases sem trecho de documento, que hoje só a
   certificação dos especialistas sustenta
   ([`CERTIFICACAO.md`](../../data/curadoria/fichas/CERTIFICACAO.md)).
2. **Quatro agentes pesquisadores**, com o roteiro do time
   ([`agentes/pesquisador.md`](../../agentes/pesquisador.md)), um grupo de
   tópicos cada. Por tópico, procuram fonte de autoridade alta ou média, de
   preferência escrita para tutor, abrem, julgam pela régua de aptidão (com
   citação literal) e capturam com o script do time
   ([`scripts/capturar_fonte.py`](../../scripts/capturar_fonte.py)), no máximo
   duas por tópico.
3. **Por frase**, o trecho literal da captura que a sustenta, ou "não
   encontrado" com as buscas feitas.
4. **A integração:** as capturas e os sidecars em
   `data/curadoria/fontes/capturas/`, uma seção nova no dossiê de cada tópico,
   uma linha por fonte em `PARA-VALIDAR.md` e, nas fichas, a frase que ganhou
   trecho deixa de ser `geral`.

## Por quê

- **O atendente não lê a ficha de busca, mas a busca depende dela.** As
  frases `geral` ajudam a achar a ficha certa (são o jeito do tutor contar), e
  nenhuma delas tem documento por trás. A certificação dos especialistas fica
  mais curta e mais segura quando cada frase já chega com o trecho que a
  sustenta.
- **A etapa 2 é onde falta fonte.** 48 dos 53 itens são da etapa 2, e cinco
  tópicos somam 22 deles (mordida de gato 7, corpo estranho 6, insuficiência
  cardíaca 3, tosse dos canis 3, cobra 3). São justamente os quadros em que o
  mapa ainda não tem sinais nem discriminador.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| **A frase não muda**, mesmo quando a fonte diz um pouco diferente | O número da réplica (rodadas 24 e 26) depende do texto das fichas. Divergência entre frase e fonte fica anotada para o especialista, que decide |
| A frase que ganhou trecho vira `origem: documento`, com `fonte` apontando a captura em `data/curadoria/fontes/capturas/` e `aprovacao: pendente` | Distingue, sem mudar o formato, o trecho de documento aprovado do trecho de fonte que ainda espera o especialista |
| A coluna `cobertura` do mapa **não** muda | Os 27 tópicos já estão `fonte_aprovada`; `fonte_encontrada` seria rebaixar. A fonte nova nasce `pending_specialist` no sidecar e aparece em `PARA-VALIDAR.md` |
| Nada é copiado para `backend/data/documents/` e nada é reindexado | Indexar é o passo do agente de ingestão, depois do aval |
| O `--inspect` da ingestão (passo 7 do roteiro) não roda | As fontes sustentam frases de ficha; não vão virar trechos da coleção acadêmica agora. Se um dia forem indexadas, o passo roda antes |
| Direitos autorais não bloqueiam; o sidecar registra o que o site declara | Combinado com o João (as capturas ficam na curadoria, fora da base) |

## Resultado esperado

_Escrito antes de os agentes começarem._

- **Pelo menos 60% dos 53 itens** com trecho literal de fonte de autoridade
  alta ou média. Menos nos itens de "como o tutor conta" (o jeito do tutor
  falar raramente está numa fonte autoritativa) do que nos sinais de alarme.
- **No máximo 2 fontes por tópico**, todas abertas e capturadas pelo script.
- **Nenhuma frase de ficha muda**: o `sync_fichas.py --check` da
  [rodada 23](2026-09-25-24-fichas-de-busca-e-de-leitura.md) continua limpo, e
  o texto de busca das 61 fichas fica idêntico.

## Resultado obtido

_(preenchido ao integrar)_

## O que mudou no repositório

_(preenchido ao integrar)_

## Observações

_(preenchido ao integrar)_

## Deixado para depois

_(preenchido ao integrar)_

## Próximo passo

_(preenchido ao integrar)_
