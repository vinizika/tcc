# O corte de relevância deixa de ser zero

**Data:** 12/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 10 ·
**Commits:** _(a preencher ao fechar)_

> Arquivo criado **antes** de qualquer linha de código, com o resultado
> esperado preenchido — o padrão da pasta, que a rodada 8 não seguiu.

## O que foi feito

Uma configuração e a auditoria dela.

**A configuração.** O corte mínimo de relevância para um trecho entrar no
prompt do classificador (`CONTEXT_MIN_SCORE`) passa de **0,0 para 0,70**, o
mesmo limiar que a busca já usa para dizer se um trecho é relevante. Com
isso, quando a busca não encontra nada acima do corte, o classificador
recebe **nada** e o sistema responde como se estivesse sem RAG — que é o
caminho que já existia e já tinha teste.

**A auditoria**, em dois níveis, a pedido do João. Por requisição: a resposta
da API passa a dizer qual corte foi aplicado, e carrega uma trava que nunca
pode ser verdadeira — "algum trecho abaixo do corte entrou". Por rodada: o
relatório ganha uma linha que resume o andamento em um número, **em quantos
por cento dos casos o RAG de fato contribuiu**.

**A ablação preservada.** Um preset novo, `naive_rag_sem_corte`, reproduz o
braço antigo com corte zero, para o artigo poder comparar os dois lado a
lado, como prometeu fazer com cada componente.

## Por quê

**Porque os braços com RAG do projeto mediram ruído, não recuperação.** A
[rodada 9](2026-09-12-09-autopsia-do-cot.md) mostrou, sobre as 98 linhas do
conjunto: nota máxima de relevância média de **0,574**, **nenhuma** linha
com trecho acima de 0,70 — e mesmo assim **três trechos entraram em 98 de
98 prompts**. O sistema calculava e reportava "quantos trechos passaram de
0,70" em toda rodada e depois ignorava esse número na hora de decidir.

**Porque a decisão de deixar em zero foi minha, e virou evidência.** Na
[rodada 3](2026-09-04-04-geracao-ancorada.md) eu configurei o corte em zero
de propósito, e o motivo está no comentário do código: naquele dia nenhum
documento passava do limiar, e descartar todos faria o braço com RAG ficar
idêntico ao braço sem RAG — o que impediria medir qualquer coisa. Deixei os
trechos entrarem e mandei registrar a nota de cada um, para a decisão virar
evidência depois. Virou: é isto.

**Porque esta correção precisa vir antes da base.** Enquanto o corte for
zero, qualquer base nova que o trilho A construir será medida junto com o
ruído, e não dará para separar quanto foi a base e quanto foi o lixo que
entrou. É a primeira das três correções cuja ordem ficou registrada no
[adendo da rodada 9](2026-09-12-09-autopsia-do-cot.md#adendo-de-1209--as-três-correções-em-linguagem-simples-e-uma-hipótese-em-espera).

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **Corrigir no consumidor, não no fundo da busca.** O `retrieval_client` do trilho A continua devolvendo os mais próximos quando nada passa do corte | A busca tem **dois** clientes. A rota `/search/` alimenta a régua de recuperação que o trilho A está construindo, e ela precisa ver **tudo, com as notas** — para medir se o protocolo certo ficou em primeiro, inclusive quando ficou abaixo do corte. Se a busca devolvesse vazio, a régua nasceria cega. O corte é regra de quem consome; o lugar dela já existia no meu pipeline. Isto **corrige** a recomendação que dei ao João na conversa anterior ("um lugar só, no trilho A") |
| 2 | Padrão muda para 0,70 em vez de criar só um preset com corte | Decisão do João. O sistema fica correto por padrão; o frontend deixa de mostrar trechos irrelevantes ao tutor; rodadas antigas continuam reproduzíveis passando `context_min_score=0.0` explicitamente |
| 3 | O tutor **não** é avisado de que a busca não achou nada | Decisão do João. Expor um detalhe interno num momento de estresse soaria como falha do sistema. A auditoria fica na resposta técnica da API e no relatório do runner |
| 4 | 0,70 referencia a constante que a busca já usa, em vez de repetir o literal | Os dois cortes não podem divergir por acidente. Se o trilho A mudar o limiar da busca, o meu segue junto |
| 5 | O valor 0,70 é declarado **provisório** no código e no contrato | É tão arbitrário quanto o zero — o próprio [B-11](../backlog.md#b-11) diz desde 04/09 que a nota de semelhança deste embedder não separa relevância. É o **menos** errado dos dois: coerente com o que o sistema já reporta, e produz o comportamento defensável (não injetar o irrelevante). O valor certo sai da régua de recuperação do trilho A, não de discussão |
| 6 | Trava de auditoria `used_below_min_score` na resposta | Nunca deve ser verdadeira. Se um dia for, o filtro quebrou, e o runner pega na hora em vez de a evidência descobrir semanas depois |
| 7 | Duas medições, e as duas são **testes de regressão** | A correção não deve mudar nenhuma classificação: com a base atual, o braço com corte vira o braço sem RAG, e o preset sem corte vira o braço antigo. Se qualquer uma diferir além do ruído já medido, algo além do corte mudou |

## Resultado esperado

_Escrito antes de codar._

| # | Rodada | Esperado |
|---|---|---|
| C1 | `naive_rag`, corte 0,70 | **Nenhuma das 98 linhas recebe trecho** (`share_rows_rag_silent = 1,0`; `used_count = 0` em todas; `returned_count > 0` em todas — a busca rodou, nada passou). Previsões **idênticas linha a linha** às de `m0_llm_only` de 11/09, porque o prompt vira o mesmo. Tolerância: até 3 linhas diferentes, que é o ruído entre sessões já medido ([B-43](../backlog.md#b-43)). Mais que isso, paro |
| C2 | `naive_rag_sem_corte`, corte 0,0 | **Idêntica linha a linha à `m3_naive_rag`** de 11/09: mesmo prompt, mesma base, mesma seed, mesmo corte. Prova que o preset reproduz o braço antigo e que nada mais mudou no caminho. Mesma tolerância |

O `compare` vai acusar `context_min_score` como diferença de configuração
entre C1 e as rodadas antigas — **correto e desejado**, é a mudança que está
sendo medida.

**O que esta rodada não muda:** nenhuma métrica de acurácia. Se C1 sair
diferente de `m0_llm_only` em mais que o ruído, ou C2 diferente de
`m3_naive_rag`, o resultado desta rodada é **ruim**, não bom.

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
