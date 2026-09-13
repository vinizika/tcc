# Primeiro lote de calibração da prova nova

**Data:** 13/09/2026 · **Trilho:** B1 (Consulta), agora também dono da **frente prova** ·
**Rodada:** 4 · **Commit:** este

> **Rodada de construção com calibração, não a medição oficial.** O produto é
> o formato da prova nova e um primeiro lote de 18 casos. A régua oficial —
> ~150 relatos, dev/teste separados, validados pelos especialistas — vem
> depois. O "esperado" desta rodada é qualitativo (onde os erros deveriam se
> concentrar), não um número de acurácia pré-registrado: calibração testa o
> **formato**, não mede o **sistema**.

## O que foi feito

Três peças, em [`data/prova/`](../../data/prova/):

| Peça | O que é |
|---|---|
| [`README.md`](../../data/prova/README.md) | O formato de cada caso, a referência de triagem escolhida e como a muralha foi respeitada |
| [`casos_calibracao.csv`](../../data/prova/casos_calibracao.csv) | 18 relatos de tutor em português, com gabarito rastreável |
| [`calibracao/2026-09-13_llm_only.json`](../../data/prova/calibracao/2026-09-13_llm_only.json) | Os 18 casos rodados contra a API hoje, com manifesto (commit, config, digest do modelo, hash do prompt) |

## Por quê

Do [plano das duas frentes](../../docs/plano-base-e-prova.md), seção 9: a
frente prova é inteira minha, e o item desta semana (seção 8) é escolher a
referência de triagem e escrever um primeiro lote pequeno para calibrar,
antes do lote de ~150. A prova atual mede vocabulário, não triagem — "só
sintoma leve" acerta 98 de 98 sem modelo nenhum ([B-05](../backlog.md#b-05))
— e foi a causa raiz do fracasso do Chain-of-Thought medido pelo João
([autópsia, 12/09](../joao/2026-09-12-09-autopsia-do-cot.md)).

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **Referência de triagem: o classificador de três níveis do MSD**, o mesmo que o mapa de assuntos já usa (`imediato`/`ate_24h`/`rotina`), colapsado igual (`imediato`→EMERGENCIA; resto→NAO_EMERGENCIA) | A *Veterinary Triage List* (Ruys et al.) é o padrão "correto" da literatura, mas sua tabela de discriminadores está atrás de paywall — nem o João conseguiu ler o original. Usar dois padrões clínicos diferentes entre mapa e prova reproduziria, do lado do rótulo, o mesmo risco que a muralha previne do lado do conteúdo |
| 2 | Usar `data/curadoria/mapa-de-assuntos.csv` como fonte dos quadros, mas **não** ler `data/curadoria/fontes/` nem `backend/data/documents/` | É a peça comum, feita para as duas frentes. Ler as fontes capturadas ensinaria meu texto a copiar a linguagem delas — o mesmo eco que a régua de recuperação evita ao escrever os casos antes de ler a fonte |
| 3 | **Nunca copiar a coluna `sinais_que_o_tutor_relata`** do mapa palavra por palavra | É exatamente o que reintroduziria a separabilidade por vocabulário que a prova nova existe para eliminar |
| 4 | **7 pares de confusão desenhados de propósito**, um por discriminador do mapa | É o requisito mais importante da seção 5.3 do plano: "casos difíceis dos dois lados" — sem eles, qualquer acurácia alta pode ser um atalho lexical, como a rodada 9 mostrou que a linha de base atual é |
| 5 | Um caso "calma grave" (`p07`) e um "alarme leve" (`p06`), no mesmo par | Testa diretamente se o sistema julga pelo **tom** do tutor ou pelo **sinal clínico** — pergunta que nenhum instrumento do projeto respondia ainda |
| 6 | Um caso fora do domínio clínico inteiro (`p16`, comportamental) | Nenhum dos 98 relatos atuais testa isso. Mede se o sistema força uma leitura de urgência onde não há sinal, não só se ele erra a gravidade |
| 7 | `split=calibracao` em toda a planilha, não `dev`/`teste` | Nada aqui é o lote oficial. Escrever com a intenção de "só calibrar" e depois promover a `dev` sem reescrever seria a mesma armadilha que o congelamento da prova existe para evitar |
| 8 | Rodar com `retrieval_enabled=false` | É a configuração hoje mais bem medida do sistema (0,893 de balanceada, sem CoT). Calibrar o formato da prova contra um braço instável (RAG, CoT) misturaria dois problemas |

## O que eu esperava encontrar

_Escrito antes de rodar, qualitativo — não é o formato "esperado × obtido"
das rodadas de medição oficial._

Esperava que os acertos se concentrassem nos dois casos-âncora (`p01`,
`p17`) e nos pares em que o discriminador é lexicalmente óbvio (`p02`/`p03`:
"equilíbrio" some), e que os erros, se houvesse, se concentrassem nos três
casos desenhados para confundir por tom ou por ausência de palavra de
alarme: `p07` (calma grave), `p08` (obstrução uretral sem a palavra "dor")
e possivelmente `p05` (efeito de remédio, sem palavra clássica de emergência
como "convulsão" ou "sangue").

## Resultado obtido

**15 de 18 (0,833 de acurácia estrita)**, rodando `llm_only` (sem RAG, sem
CoT), commit `17f1eeb`. Manifesto completo, com o digest do modelo e o hash
do prompt, em
[`calibracao/2026-09-13_llm_only.json`](../../data/prova/calibracao/2026-09-13_llm_only.json).

| Classe esperada | Acertos |
|---|---:|
| EMERGENCIA (9) | 6 de 9 |
| NAO_EMERGENCIA (8) | 8 de 8 |
| INCERTO (1) | 1 de 1 |

**As três divergências são as três que eu esperava**, e as três são falsos
não urgentes — o erro grave do projeto:

| Caso | Par | O que o modelo disse |
|---|---|---|
| `p05` — remédio humano em gato, gengiva arroxeada | `p04` | Listou "vômito" e "arroxeamento das gengivas" como sinais, e mesmo assim concluiu: *"não indicam uma emergência imediata (...) informação adicional ajudaria"* |
| `p07` — dilatação-torção gástrica, tom calmo | `p06` | Listou "vomitar várias vezes" e "barriga estufada", mas justificou a classificação leve por *"está sem fazer escândalo e não há outros sinais de doença"* |
| `p08` — obstrução uretral em gato | `p09` | **Não extraiu nenhum sinal de alerta** e leu o quadro como comportamental: *"é possível que o gato esteja apenas se esforçando para sair da caixinha"* |

**O achado mais forte é o `p07`.** O modelo extraiu corretamente os dois
sinais que definem o quadro grave, e mesmo assim decidiu pela ausência de
drama no relato — é a mesma hipótese "o modelo julga pelo tom, não pelo
sinal" da rodada de calibração, agora com um caso desenhado para isolar
exatamente essa variável, e ela se confirmou.

**`p08` é o mais grave clinicamente.** É o par que o próprio mapa de
assuntos chama de "maior letalidade" — obstrução uretral felina pode matar
em 24 a 48 horas — e o modelo não reconheceu nenhum sinal de risco na
descrição de um gato fazendo força repetida com pouca urina, tratando como
comportamento normal.

**Zero falsos urgentes.** Nenhum caso leve foi classificado como emergência,
incluindo o caso fora do domínio clínico (`p16`) e o alarme leve (`p06`).

## O que isto valida, e o que não valida

**Valida o formato.** Os pares de confusão fizeram exatamente o que
deveriam: separaram acerto de acaso. Um lote sem eles teria mostrado 100%
(os dois casos-âncora e os pares "fáceis" acertaram) e escondido as três
falhas reais.

**Não valida — ainda — a referência de triagem nem os rótulos.** Os 18
casos são meus, provisórios, no mesmo estado que os `b01`-`b18` da régua de
recuperação estavam antes da revisão do trilho A: precisam da validação de
um especialista antes de qualquer número entrar no artigo.

**Não é medição do sistema.** 18 casos não têm poder estatístico nenhum —
é o mesmo aviso que o João registrou para a régua de recuperação. O valor
desta rodada é o **padrão qualitativo** (falha por tom, falha por ausência
de sinal extraído), não o 0,833.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `data/prova/README.md` | **novo** — formato da prova, referência de triagem, registro da muralha |
| `data/prova/casos_calibracao.csv` | **novo** — 18 casos |
| `data/prova/calibracao/2026-09-13_llm_only.json` | **novo** — resultado com manifesto |

Nenhum código do backend ou dos scripts mudou nesta rodada.

## Observações

**1. As três falhas apontam para o mesmo mecanismo que o CoT expôs.** A
rodada 9 do João encontrou "o modelo não calibra risco à vida" no braço com
raciocínio estruturado. Aqui, no braço **sem** raciocínio nenhum, o mesmo
padrão aparece de outra forma: o modelo às vezes extrai o sinal certo (`p07`)
e ainda assim erra a decisão, guiado pelo tom do relato em vez do sinal. Não
é um problema do CoT — é um problema do julgamento do modelo, e o CoT só o
tornou visível de um jeito diferente.

**2. O par `p08`/`p09` é o mais valioso do lote.** Testa exatamente o
discriminador que o mapa de assuntos chama de mais perigoso, e o modelo
falhou do lado que mata. Vale ser um dos primeiros casos revisados pela
especialista.

**3. `retrieval_enabled=false` foi a escolha certa para calibrar o
formato.** Rodar com RAG teria misturado "o formato do caso é bom?" com "a
base atual tem ruído?" — duas perguntas diferentes, e a segunda já está
sendo respondida por outra frente do projeto.

## Deixado para depois

**Levar o formato ao time.** Antes de escrever os ~150 casos do lote
oficial, vale confirmar com o João e o Vinicius que a estrutura de colunas e
a referência de triagem servem — principalmente porque `topic` cria um
vínculo direto com o mapa de assuntos, que os dois também usam.

**Adaptar o runner** (seção 5.4 do plano) para ler a coluna `text` em vez
das cinco colunas de sintoma, registrar `--relato-lang` e calcular os
baselines triviais novos (saco de palavras, palavra de alarme, comprimento).
Ainda rodei este lote manualmente, sem o runner — aceitável para 18 casos,
não para 150.

**Validação clínica dos 18 casos e da referência escolhida.** Nenhum rótulo
aqui vale para o artigo sem isso.

## Próximo passo

Levar `data/prova/README.md` e os três casos que falharam para os outros
dois trilhos, e decidir se o formato está pronto para escrever o lote
grande — ou se algum ajuste (por exemplo, mais casos por par, ou um segundo
"calma grave") deveria entrar antes de escalar para ~150.
