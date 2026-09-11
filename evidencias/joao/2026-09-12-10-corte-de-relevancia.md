# O corte de relevância deixa de ser zero

**Data:** 12/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 10 ·
**Commits:** 9a1ec45 (código), + este

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

As duas medições confirmaram o esperado, e a primeira foi mais limpa do que
eu previra.

### C1 — o braço com RAG e o corte valendo

Rodada [`20260911-192018_c1_naive_rag_com_corte`](../../data/evaluation/cited/20260911-192018_c1_naive_rag_com_corte/report.md)
· preset `naive_rag` · 98 linhas · corte 0,70.

| Verificação | Resultado |
|---|---|
| Linhas que receberam algum trecho | **0 de 98** |
| Busca silenciosa | **100%** |
| Trava de auditoria violada | 0 linhas |
| Nota máxima média da busca | 0,574 |

E o teste de regressão, que era o ponto da rodada:

| Comparação | Linhas com classificação diferente |
|---|---|
| C1 contra `m0_llm_only` (ontem) | **2** — as linhas 843 e 845 |
| C1 contra `r2_linha_de_base` (04/09) | **0 de 98** |

**Zero diferenças contra a linha de base de 04/09.** As duas diferenças
contra a rodada de ontem são exatamente as linhas 843 e 845, as mesmas que o
[B-43](../backlog.md#b-43) já registrou como ruído entre sessões — não são
efeito da correção. Isso era o esperado: sem trecho no prompt, o braço com
RAG **é** o braço sem RAG, e a acurácia sobe de 0,856 para 0,893 só porque
deixa de carregar o ruído.

O relatório emitiu o aviso automático sozinho:

> A busca ficou silenciosa em todas as linhas. Nenhum trecho passou do corte
> de relevância, então o classificador decidiu sem contexto em 100% dos
> casos: esta rodada mediu o mesmo que o braço sem recuperação.

### C2 — o preset que reproduz setembro

Rodada [`20260911-192335_c2_naive_rag_sem_corte`](../../data/evaluation/cited/20260911-192335_c2_naive_rag_sem_corte/report.md)
· preset `naive_rag_sem_corte` · corte 0,0 · **98 de 98** linhas com trecho.

Contra a `m3_naive_rag` de ontem: **3 linhas diferentes** (12, 24, 68),
balanceada 0,775 contra 0,768, falsos não urgentes idênticos em 30, McNemar
1 contra 2 com p = 1,0. Dentro do ruído entre sessões. O preset reproduz o
braço antigo.

### O que os dois juntos mostram

| Braço | Balanceada | FNU | FU | Trechos no prompt |
|---|---:|---:|---:|---:|
| Com corte (C1) | **0,893** | 8 | 2 | 0 de 98 |
| Sem corte (C2) | 0,775 | 30 | 0 | 98 de 98 |

A diferença entre as duas linhas é **só** o corte, e ela custa 11,8 pontos
de acurácia balanceada e 22 falsos não urgentes. Este é o número mais
honesto que o projeto tem sobre o RAG hoje: **injetar três trechos
irrelevantes custa 22 emergências classificadas como leves**. Não é o RAG
que degrada; é o ruído.

### As duas previsões

| # | Previsão | Resultado |
|---|---|---|
| C1: busca silenciosa em 100%, idêntica ao braço sem RAG | ✅ **Certa, e melhor**: 0 diferenças contra 04/09, 2 contra ontem (as do ruído conhecido) |
| C2: idêntica à rodada de ontem | ✅ Certa: 3 linhas, dentro do ruído, mesmas métricas clínicas |

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/core/config.py` | `CONTEXT_MIN_SCORE` de 0,0 para `DEFAULT_SCORE_THRESHOLD`; comentário com a história inteira |
| `backend/app/schemas/triage.py` | `RetrievalInfo` com `context_min_score` e `used_below_min_score` |
| `backend/app/pipeline/chat_pipeline.py` | `_retrieve` preenche os dois campos |
| `scripts/evaluation_metrics.py` | `share_rows_with_context`, `share_rows_rag_silent`, `rows_used_below_min_score` |
| `scripts/report_evaluation.py` | as métricas no relatório, com aviso automático de busca silenciosa |
| `scripts/run_evaluation.py` | corte e trava gravados por linha |
| `scripts/presets.json` | preset `naive_rag_sem_corte` |
| `backend/tests/*`, `scripts/tests/*` | scripts 71 → 76, backend 123 → 129 |
| `data/evaluation/cited/` | C1 e C2 |

Commits: `9a1ec45` (código) e o desta evidência.

## Observações

**1. O braço com RAG não desapareceu — virou dois braços.** Eu havia
avisado que ele sumiria das medições. Na prática ficou melhor: o par C1 e C2
**é** a medição, e ela isola o efeito do ruído com uma variável só. A
ablação do artigo ganha uma linha que não tinha: "com corte" contra "sem
corte", 11,8 pontos de diferença.

**2. O `compare` acusou duas diferenças de configuração, e ele está certo.**
Entre C1 e `m0_llm_only` mudaram `context_min_score` **e**
`retrieval_enabled` — porque o braço sem RAG desliga a busca, enquanto o C1
liga a busca e descarta o resultado. São caminhos diferentes que produzem o
mesmo prompt. Vale para a leitura: o número é idêntico, a configuração não.

**3. Um campo do retrato do sistema virou ruído no aviso.** O `compare`
alertou que `model.loaded_in_vram_bytes` diferia entre as rodadas: 2,5 GB
contra nulo. É a memória de vídeo ocupada no instante da chamada, que muda
conforme o modelo já estava carregado. Não descreve o sistema, descreve o
momento. Vai para o backlog como [B-47](../backlog.md#b-47).

**4. A nota máxima média da busca é a mesma nos dois braços: 0,574.** Ela
não depende do corte, porque o corte age depois. Serve como número de
referência para o trilho A: é a distância entre o que a busca encontra hoje
e o que ela considera relevante.

**5. O limiar continua sem fundamento medido.** 0,70 é o valor que o sistema
já reportava, e agora ele decide. O número certo sai da régua de recuperação
([B-11](../backlog.md#b-11)). Enquanto isso, a escolha é defensável por
coerência interna, não por evidência.

## Deixado para depois

**Medir o limiar certo.** É a régua de recuperação, e virou a rodada
seguinte ([B-11](../backlog.md#b-11)). Um ensaio dela, feito nesta sessão
sem código, já mostrou que o protocolo certo vem em primeiro em 5 de 11
casos e que "Trauma, quedas e hemorragias" aparece em primeiro em 8 de 18 —
o protocolo-ímã, que é o [B-02](../backlog.md#b-02) com número.

**Limpar o retrato do sistema do que é estado de momento**
([B-47](../backlog.md#b-47)). A memória de vídeo ocupada não descreve a
versão; ela faz o `compare` avisar sem motivo, o que gasta a atenção que o
aviso deveria receber.

## Próximo passo

**A régua de recuperação**, construída em nome do trilho A, como o João
decidiu. Ela é o gargalo de dois trilhos — o A não amplia a base sem ela, o
B1 não mede as técnicas de consulta sem ela — e é ela que vai dizer o limiar
que esta rodada deixou provisório.
