# Endurecimento do instrumento antes do Chain-of-Thought

**Data:** 11/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 7 ·
**Commits:** c1a6a07 (revisão e backlog), + este

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

As três correções ficaram de pé e as quatro previsões se confirmaram. Nada
de métrica mudou, como esperado de uma rodada de instrumentação.

### 1. O runner confere a base

| Cenário | Antes | Agora |
|---|---|---|
| Busca ligada, base vazia | rodava até o fim e saía como sucesso | **aborta no preflight**, com o comando de ingestão na mensagem |
| Busca desligada, base vazia | rodava | roda (correto: `llm_only` não usa a busca) |
| `--expect-base-hash` diferente | não existia | **aborta antes do aquecimento**, imprimindo os dois hashes |

Verificado de ponta a ponta contra a API:

```
$ python scripts/run_evaluation.py --preset llm_only --subset smoke \
    --limit 2 --expect-base-hash base-que-nao-existe
A base vetorial não é a esperada.
  esperado: base-que-nao-existe
  na API  : eeba9f51d239e2f6167d18ffe87ef5e6f505de0497b222555a3cb953dd12a914
```

Com o hash certo, o smoke de duas linhas roda normalmente, e o manifesto
passa a registrar `expected_base_hash` — a rodada guarda que foi conferida.

A checagem da busca usa o `config` **efetivo** ecoado pelo aquecimento, e
não o pedido: o modo `v0_legacy` desliga a recuperação no servidor, e ali
base vazia não é problema nenhum.

### 2. O retrato do sistema ficou completo

`GET /health/fingerprint`, em `vector_store`, agora traz:

| Campo | O que pega | Valor nesta máquina |
|---|---|---|
| `chunk_ids_sha256` | mudança de **recorte** (o campo antigo, intacto) | `eeba9f51…` |
| `content_sha256` | mudança de **texto ou metadados**, mesmo com o id igual | `89a215ac…` |
| `embedding_model` | qual modelo transformou texto em vetor | `…/paraphrase-multilingual-MiniLM-L12-v2` |
| `chunking` | target 96, overlap 16, limite 128 | — |

O `chunk_ids_sha256` continua idêntico ao das seis rodadas citadas, que era
a condição para elas seguirem comparáveis.

**Custo da chamada: 19 ms** (0,092 s na primeira, fria). O risco que eu
havia registrado — o hash de conteúdo lê a coleção inteira — não se
materializou com 18 chunks. Com os ~259 da base nova ainda deve ser
irrelevante; com dezenas de milhares valeria um cache por contagem.

### 3. O `compare` enxerga mudança de código

O caso que passou batido na rodada 6, agora:

```
$ python scripts/report_evaluation.py compare \
    data/evaluation/cited/20260904-024433_r3b_variancia \
    data/evaluation/cited/20260905-133840_b04_confirmacao

--- diferenças de configuração ---
  nenhuma

  Aviso: as rodadas rodaram commits diferentes (a95f895 -> ad7c7b8).
  Mudanças no código do pipeline ou nos prompts de consulta não aparecem
  no fingerprint.

  Aviso: ao menos uma das rodadas foi executada com alterações locais não
  commitadas.
```

O commit `ad7c7b8` é exatamente o merge da correção do Ryu, que mudou o
comportamento da etapa de consulta. O segundo aviso é um brinde que não
estava previsto: quatro das seis rodadas citadas rodaram com a árvore suja,
e isso enfraquece a rastreabilidade delas. Fica registrado nas Observações.

A comparação do fingerprint passou a olhar **apenas as chaves presentes nos
dois manifestos**. Sem isso, toda rodada anterior a hoje acusaria diferença
contra toda rodada nova, por causa dos campos que acabaram de nascer — e um
aviso que aparece sempre deixa de ser lido.

### Testes

| Suíte | Antes | Depois |
|---|---:|---:|
| Scripts (host) | 57 | **68** |
| Backend (container) | 102 | **109** |

Os 11 novos dos scripts cobrem os quatro cenários da conferência de base, o
fingerprint indisponível, e as quatro situações da comparação de retratos.
Os 7 do backend cobrem o hash de conteúdo: texto reescrito muda o hash e o
dos ids não; metadado reescrito muda; a ordem de leitura e a ordem das
chaves não mudam; um dublê sem documentos não quebra; e a base indisponível
não derruba a rota.

**Uma falha continua no backend, e é anterior a esta rodada:**
`test_pdf_layout_extraction.py::test_regressao_do_paper_real…` espera o
extrator novo e recebe o fallback, porque a imagem Docker desta máquina não
tem `pymupdf`. O `requirements.txt` mudou em 07/09 e a imagem não foi
reconstruída — de propósito, conforme a decisão desta rodada. Não é
regressão do que fiz aqui: falhava igual antes, e o código que toquei não
passa por ali.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `scripts/run_evaluation.py` | `conferir_base()`, chamada no preflight em dois momentos; opção `--expect-base-hash`; `expected_base_hash` no manifesto |
| `scripts/report_evaluation.py` | `_diferencas_comparaveis()`; aviso de commit diferente e de árvore suja; comparação do fingerprint chave a chave |
| `backend/app/services/fingerprint_service.py` | `_hash_de_conteudo()`; `content_sha256`, `embedding_model` e `chunking` em `_base_vetorial` |
| `scripts/tests/test_run_evaluation.py` | 7 testes da conferência de base |
| `scripts/tests/test_report_evaluation.py` | 4 testes da comparação de retratos |
| `backend/tests/test_api_health.py` | 7 testes do hash de conteúdo e do embedder |
| `docs/CONTRATOS.md` | a linha do `/health/fingerprint` descreve os campos novos |
| `data/evaluation/README.md` | `--expect-base-hash` na tabela de opções |
| `README.md` | passo 4 avisa sobre a virada da base (commit anterior) |
| `evidencias/backlog.md` | B-25, B-29 e B-38 fechados; B-36, B-37 e B-38 criados (commit anterior) |

## Observações

**1. Quatro das seis rodadas citadas rodaram com a árvore suja.** O aviso
novo revelou isso de passagem: R2, R3, R3b, R1b e R3c têm `git.dirty: true`
no manifesto. Elas continuam válidas — o que elas mediram está nos
`predictions.jsonl` —, mas o commit delas não descreve exatamente o código
que rodou. Daqui para a frente, rodada que for citada roda com a árvore
limpa. Não vira item de backlog: é disciplina, não código.

**2. O `git.sha` do manifesto vem do host, não do container.** Ele descreve
o código que rodou porque o Compose monta `./backend:/app`. Se alguém rodar
uma imagem construída, sem o volume, o sha deixa de dizer a verdade e o
aviso novo passa a mentir em silêncio. Vale saber antes de mexer no
Compose; hoje não é problema.

**3. O `content_sha256` muda quando um metadado muda, de propósito.** Título
e fonte vão ao prompt do classificador; os demais descrevem a procedência do
trecho. Acrescentar um campo de metadado na ingestão vai acusar mudança de
base — é o comportamento correto, mas o trilho A precisa saber para não
levar susto.

**4. A conferência de base custa uma requisição a mais.** O fingerprint já
era buscado para o manifesto; agora ele é buscado **antes** do aquecimento,
e o valor é reaproveitado. A rodada não ficou mais lenta.

**5. O `--expect-base-hash` é opcional, e essa é a escolha frágil da
rodada.** Obrigar quebraria um smoke rápido, mas depender de disciplina é
exatamente o que falhou no B-37. Se em outubro alguém citar uma rodada sem
o hash, vale rever: tornar obrigatório quando `--subset full`, por exemplo.

**6. O que a revisão dos outros trilhos deixou para o time** está no
backlog: [B-36](../backlog.md#b-36) (o rótulo no `content`) e
[B-37](../backlog.md#b-37) (a virada da base). Os dois são do trilho A e
travam a próxima medição minha com RAG sobre a base nova.

## Deixado para depois

**Tornar o `--expect-base-hash` obrigatório para rodadas citáveis.** Hoje é
opcional e depende de disciplina (Observação 5). Ficou de fora porque a
regra certa ainda não está clara: obrigar em `--subset full` pegaria as
rodadas do artigo sem atrapalhar smoke, mas também impediria a primeira
medição de uma base nova, que por definição não tem hash conhecido. Volta
quando a base nova estabilizar. Item [B-39](../backlog.md#b-39).

**Conferir também o `content_sha256` no `--expect-base-hash`.** Hoje a
opção compara só o hash dos ids, que é o que liga às rodadas citadas. Duas
bases com o mesmo recorte e textos diferentes passariam. Adiado porque as
rodadas antigas não têm o campo — exigir agora as tornaria irreproduzíveis.
Volta quando todas as rodadas citadas tiverem o retrato novo. Item
[B-40](../backlog.md#b-40).

**Reconstruir a imagem Docker.** É o que falta para o teste do paper passar
nesta máquina, e será obrigatório quando a API precisar do extrator novo.
Adiado porque o rebuild resolve `torch` com CUDA e foi o que encheu o disco
do Vinicius. Volta junto de fixar a versão CPU do torch — parte do
[B-34](../backlog.md#b-34), sem item novo.

## Próximo passo

**Chain-of-Thought**, finalmente, com o instrumento endurecido: o runner
recusa base errada, o retrato identifica conteúdo e embedder, e o `compare`
avisa quando o código mudou. A linha de base continua sendo o preset
`llm_only` (0,893 de acurácia balanceada, 8 falsos não urgentes em 71), que
não usa a etapa de consulta e por isso é imune tanto à instabilidade da
rodada 6 quanto à virada da base.

Duas coisas que esta rodada muda no plano do CoT:

1. **Toda rodada do CoT roda com `--expect-base-hash`** e com a árvore
   limpa, para o par antes/depois ficar rastreável.
2. **O braço `naive_rag + cot` tem prazo.** Ele só é comparável com a R3
   enquanto a base for a de 18 chunks ([B-37](../backlog.md#b-37)). Ou mede
   antes da virada, ou refaz depois — decisão do João, com o trilho A.
