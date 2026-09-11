# Endurecimento do instrumento antes do Chain-of-Thought

**Data:** 11/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 7 ·
**Commits:** _(a preencher ao fechar)_

## O que foi feito

Duas coisas, em sequência.

**1. Revisão do que os outros trilhos entregaram entre 07 e 08/09**, antes
de retomar o planejamento do Chain-of-Thought. Quatro commits, 65 arquivos:
a ingestão nova do trilho A (PyMuPDF, seções, chunks por tokens, modo
`--inspect`, o paper de heatstroke) e duas entregas do B1 (upload de voz
endurecido, Whisper único com WER medido). A revisão cobriu evidências,
backlog, código, contratos, testes nos dois lados e o estado da base local.

**2. Três correções no instrumento de medição**, todas do B2, decididas a
partir da revisão e feitas antes do CoT:

| # | Correção | Onde |
|---|---|---|
| a | O runner passa a **conferir a base** no preflight: aborta se a busca estiver ligada e a base estiver vazia; com `--expect-base-hash`, aborta se a base não for a esperada | `scripts/run_evaluation.py` |
| b | O fingerprint passa a identificar o **embedder, os parâmetros de chunking e um hash do conteúdo** da base, e o `compare` passa a avisar quando o **commit** das duas rodadas difere | `backend/app/services/fingerprint_service.py`, `scripts/report_evaluation.py` |
| c | O README raiz deixa de prometer "18 trechos" e passa a avisar sobre a virada da base | `README.md` |

## Por quê

**Porque as linhas de base do CoT ficaram frágeis sem ninguém ter errado.**
As rodadas citadas em `data/evaluation/cited/` dependem de uma base de 18
chunks, e o algoritmo que a gerava foi substituído em 07/09. A base antiga só
existe nas máquinas que já a tinham; um clone limpo que siga o README produz
outra, com cerca de 259 chunks, 186 deles de um paper em inglês. O trilho A
registrou nas evidências dele que **não** reindexou de propósito, e é
verdade — mas isso é convenção, não algo que o código garanta.

**Porque o instrumento não avisa quando o chão muda.** Na rodada 6 o
`compare` imprimiu "nenhuma diferença de configuração" entre duas rodadas que
rodaram código diferente ([B-25](../backlog.md#b-25)). O trilho A apontou o
mesmo buraco por outro lado: o fingerprint só olha os IDs dos chunks, não o
conteúdo nem o embedder ([B-29](../backlog.md#b-29)). E o runner nem confere
se a base está vazia antes de uma rodada com busca. Com dois colegas mexendo
em ingestão e consulta toda semana, medir o CoT sem fechar isso é medir em
cima de areia: qualquer diferença poderia ter vindo de outro lugar.

**Porque um detalhe da ingestão nova toca o meu prompt.** O chunk novo
carrega um rótulo em inglês colado na frente do texto (`Document title: …`,
`Section: …`), e é esse texto que chega ao classificador como `content`.
Não tem efeito hoje, porque a base não foi reindexada; terá no dia da virada.
Foi para o backlog como item do trilho A ([B-36](../backlog.md#b-36)).

## O que a revisão encontrou

### Do trilho A (Vinicius)

- **Auditoria honesta e útil.** Separou o que o time já sabia do que era novo
  e registrou sete achados que ninguém tinha visto, dois deles fora do trilho
  dele (upload de voz, healthcheck). Virou B-29 a B-35.
- **Ingestão nova bem testada**: 40 testes, paper real como regressão,
  `--inspect` que não toca no banco. A base local não foi reindexada — o
  fingerprint desta máquina bate com o das rodadas citadas (hash
  `eeba9f51…`, 18 chunks).
- **O rótulo dentro do `content`** (acima). Contrato A → B2 diz que `content`
  é "o texto que entra no prompt"; a semântica mudou sem aviso.
- **Os manuais divergem.** README raiz: "rode e veja 18 trechos". README do
  trilho A: "na migração use `--reset`". Evidências do trilho A: "não
  reindexe até a régua existir". Com ou sem `--reset` o comando gera a base
  nova; a opção só protege contra restos. A direção do trilho A está certa
  para o momento da virada; faltou alinhar o manual principal — e faltou
  notar que a base antiga não se regenera.
- **A imagem Docker precisa de rebuild** (`pymupdf`, `fonttools` entraram no
  `requirements.txt`) e a atual, de 11,7 GB, não os tem: 1 dos 102 testes do
  backend falha nesta máquina por isso. O rebuild puxa o torch com CUDA e foi
  o que derrubou o Docker do Vinicius. Registrado aqui como cuidado
  operacional, sem item novo — o time preferiu não tratar agora.
- **PDF de editora em repositório público e licença AGPL do PyMuPDF**: o
  João avaliou como não crítico para o contexto do TCC, e por isso não
  entrou no backlog. Fica o registro para o caso de o repositório ganhar
  visibilidade.

### Do trilho B1 (Ryu)

- **B-32 e B-13 fechados**, os dois primeiros da seção "Resolvidos" do
  backlog. O upload tinha *path traversal* real, e o Compose monta o
  repositório dentro do container, então um nome com `../` alcançava o código.
- **WER de 5,2%** em fala sintética, primeira medição de voz do projeto.
  Contradiz o 97,5% que o artigo cita; o texto do TCC vai precisar dizer isso.
- **Os 18 relatos PT-BR rotulados** do benchmark são a primeira semente de
  relatos leigos em português do projeto — úteis para leitura qualitativa do
  raciocínio do CoT, sem substituir o conjunto de avaliação
  ([B-15](../backlog.md#b-15)).
- A métrica "idioma detectado ≠ pt: 0" é verdadeira por construção, porque o
  `VoiceService` força `language="pt"`. O João avaliou como não prioritário;
  não entrou no backlog.

### Verificação

| Verificação | Resultado |
|---|---|
| `main` local | `16ce2ff`, alinhada com o remoto, árvore limpa |
| Testes dos scripts (host) | 57 aprovados |
| Testes do backend (imagem atual, sem rebuild) | 101 aprovados, 1 falha por `pymupdf` ausente na imagem |
| Base local | 18 chunks, hash `eeba9f51…` — igual ao das rodadas citadas |
| Modelo / prompts / Ollama | digest `a80c4f17…`, prompts `d04ad0f7…`, Ollama 0.33.3 — iguais aos citados |

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Fazer as três correções **antes** do CoT, contrariando a ordem do planejamento pela segunda vez | O CoT vai ser comparado com rodadas antigas. Se o instrumento não avisa que a base ou o código mudaram, o efeito do CoT fica indistinguível de qualquer outra mudança. Custa uma rodada curta; descobrir depois custa a medição inteira |
| **Não reindexar** a base desta máquina | É a única forma de manter comparáveis as rodadas R2, R3, R3c e R6. A virada é decisão do trilho A ([B-37](../backlog.md#b-37)) |
| **Não reconstruir** a imagem Docker agora | A API não importa os módulos novos de ingestão; só o teste do paper falha. O rebuild puxa o torch com CUDA e derrubou o Docker do Vinicius. Adiar até fixar a versão CPU, ou até precisar de fato do PyMuPDF nesta máquina |
| Tratar B-25 e B-29 juntos | São o mesmo buraco por dois lados: a identidade do sistema registrada em cada rodada está incompleta. Uma rodada só, um teste só |
| Levar ao backlog só o que o João validou | Dos sete apontamentos da revisão, o João julgou dois não críticos para o contexto do TCC (PDF e licença) e dois não prioritários (torch CPU, métrica de idioma). Ficam registrados aqui; não viram fila |
| O `--expect-base-hash` é opcional, não obrigatório | Obrigar quebraria o fluxo de quem só quer rodar um smoke. Mas toda rodada que vai ser citada passa a ser executada com ele |

## Resultado esperado

_Escrito antes de codar._

1. `run_evaluation.py --preset naive_rag` contra uma base vazia **aborta no
   preflight**, antes da primeira linha, com mensagem que diz o que fazer.
   Contra a base cheia, roda como hoje. Com `--expect-base-hash <hash>`
   diferente do real, aborta com os dois hashes na mensagem.
2. `/health/fingerprint` passa a trazer, dentro de `vector_store`, o nome do
   embedder, o target/overlap/limite de tokens do chunking e um hash do
   conteúdo (documentos + metadados). Mudar o texto de um chunk sem mudar o
   ID muda esse hash — é o critério do B-29, em teste automatizado com dublê.
3. `report_evaluation.py compare` entre a R3b (commit `a95f895`) e a rodada 6
   (commit `b907d6e`) passa a imprimir um **aviso de commit diferente** —
   hoje imprime "nenhuma".
4. Nenhuma métrica muda: as três correções são de instrumentação. Os 57 + 102
   testes continuam verdes, mais os novos.
5. O risco que enxergo: o hash de conteúdo exige ler documentos e metadados
   da coleção inteira a cada chamada do fingerprint. Com 18 chunks é nada;
   com 259 ainda é pouco; com milhares seria lento. Vou medir o tempo da
   chamada e registrar.

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
