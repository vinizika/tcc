# Prova nova

Trilho **B1** (Ryu). Contexto completo em
[`docs/plano-base-e-prova.md`](../../docs/plano-base-e-prova.md), seção 5
("Frente prova").

Dois arquivos, dois papéis:

- **`casos_calibracao.csv`** — os 18 casos originais que calibraram o
  formato (rodada 4, 13/09). `split` sempre `calibracao`. Não entra em
  nenhuma medição oficial; existe só como registro de como o formato nasceu.
- **`casos_oficiais.csv`** — a prova de verdade, dividida por `split` em
  `dev` (~50 casos, para iterar à vontade) e `teste` (~100 casos, que
  congela por hash quando estiver completo). **Hoje só tem o lote `dev`**
  (rodada 10, 21/09) — o lote `teste` é o próximo passo.

## Por que existe

A prova atual (`data/dataset1_clean.csv` e afins, usada pelo runner) é uma
lista de sintomas em inglês, trivialmente separável ("só sintoma leve" acerta
98 de 98 sem modelo — [B-05](../../evidencias/backlog.md#b-05)) e foi a causa
raiz do fracasso do Chain-of-Thought medido pelo João
([rodada 9](../../evidencias/joao/2026-09-12-09-autopsia-do-cot.md)): sem
gravidade nem duração no texto, o modelo não tem como julgar risco.

## A referência de triagem escolhida

**O mesmo classificador de três níveis do MSD Veterinary Manual que o mapa de
assuntos já usa** (`imediato` / `ate_24h` / `rotina`), colapsado do mesmo
jeito que `data/curadoria/mapa-de-assuntos.csv` já colapsa para o sistema:
`imediato` → `EMERGENCIA`; `ate_24h` e `rotina` → `NAO_EMERGENCIA`.

**Por que esta e não outra.** A *Veterinary Triage List* (Ruys et al. 2012),
citada no TCC1, é o padrão "correto" da literatura de triagem veterinária,
mas a tabela completa dos 68 discriminadores está atrás de paywall — o
próprio João não conseguiu ler o artigo original, só um resumo secundário
(registrado na [rodada 12](../../evidencias/joao/2026-09-12-12-mapa-de-assuntos.md)).
Usar o MSD, que já está por trás de toda coluna `urgencia` do mapa, evita
que **base e prova apontem para dois padrões clínicos diferentes** — o
próprio risco que a "muralha" existe para prevenir do lado do conteúdo, e que
aqui eu previno do lado do rótulo.

`EMERGENCIA` / `NAO_EMERGENCIA` / `INCERTO` continuam sendo as classes do
sistema (decisão do time, seção 2 do plano); o nível fino do MSD vira coluna
extra (`expected_urgency`), para quem quiser recolapsar diferente depois.

## O formato de cada caso

| Coluna | O que é |
|---|---|
| `id` | `p01`, `p02`… — prefixo `p` para não colidir com os `b01`-`b18` da régua de recuperação |
| `text` | O relato do tutor, em português, texto livre, escrito a partir do **cenário clínico** — nunca copiando a coluna `sinais_que_o_tutor_relata` do mapa palavra por palavra |
| `species` | `cao` ou `gato` — sempre declarada, porque um tutor real diz a espécie |
| `expected_class` | `EMERGENCIA` / `NAO_EMERGENCIA` / `INCERTO` |
| `expected_urgency` | `imediato` / `ate_24h` / `rotina` — vazio quando `expected_class = INCERTO` |
| `topic` | O `id` do [mapa de assuntos](../curadoria/mapa-de-assuntos.csv), quando o caso corresponde a um quadro do mapa; vazio quando o caso é deliberadamente **fora do mapa** |
| `confusion_pair_id` | O `id` do caso par nesta mesma planilha, quando os dois formam um par de confusão desenhado de propósito |
| `difficulty_tag` | `controle_emergencia` / `controle_leve` (âncoras fáceis) · `par_confuso` · `alarme_leve` (tem palavra de risco, é leve) · `calma_grave` (tom calmo, é grave) · `fora_do_mapa` (não corresponde a nenhum dos 61 quadros — ver nota abaixo) · `informacao_insuficiente` |
| `note` | Justificativa clínica da rotulagem e o que o caso testa |
| `source_reference` | Aponta para a linha do mapa de assuntos que fundamenta o quadro (que por sua vez carrega a referência publicada) |
| `marked_by` | Quem marcou — hoje sempre eu, **provisório até validação de especialista**, mesmo padrão do `data/retrieval/cases.csv` |
| `split` | `calibracao` (só em `casos_calibracao.csv`) · `dev` / `teste` (em `casos_oficiais.csv`) |

**Sobre o `fora_do_mapa` ter substituído o `fora_da_base` do lote de
calibração:** o lote de calibração (13/09) tinha um caso "fora da base, mas
dentro do mapa" (acidente ofídico) — media se o sistema fica quieto diante de
um quadro real ainda sem documento indexado. Isso envelheceu rápido: em
20/09 o próprio quadro ganhou fonte aprovada (seção 5.3 do plano já avisava
que isso aconteceria). O lote oficial usa `fora_do_mapa` com um sentido mais
forte e mais estável: o caso não corresponde a **nenhum dos 61 quadros**
listados, então nunca vai "ganhar cobertura" por a base crescer — é sempre
uma pergunta legítima (nutrição, calendário vacinal) sem urgência clínica
nenhuma por trás.

## A muralha, e como foi respeitada nesta rodada

Escrevi os 18 casos usando **apenas** `data/curadoria/mapa-de-assuntos.csv`
(a peça comum entre as duas frentes, não um documento da base) e
conhecimento clínico geral. **Não abri** nenhum arquivo de
`data/curadoria/fontes/` nem `backend/data/documents/` para escrever isto —
ler as fontes capturadas antes de escrever o relato faria a busca "acertar"
por eco depois.

## O que o lote cobre, e por quê

18 casos: **9 emergência, 8 não emergência, 1 incerto** — bem mais perto de
50/50 que os 72/28 da prova atual.

- **7 pares de confusão**, cada um testando um discriminador específico do
  mapa: otite × síndrome vestibular; indiscrição alimentar × intoxicação por
  remédio humano; vômito isolado × dilatação-torção gástrica; obstrução
  uretral × cistite (o par de maior letalidade do mapa); piometra × cio
  normal; paralisia aguda × artrose; emergência ocular × conjuntivite leve.
- **1 caso "alarme leve"**: contém a palavra "vomitou", mas é episódio único
  — testa se o sistema reage à palavra ou ao quadro.
- **1 caso "calma grave"**: tom calmo do tutor, quadro grave (torção
  gástrica) — o oposto do alarme leve.
- **1 caso fora da base, mas dentro do mapa**: acidente ofídico/aracnídeo,
  quadro real (etapa 2 do mapa) sem documento hoje.
- **1 caso genuinamente incerto**: sem sinal, duração ou contexto nenhum.
- **1 caso fora do domínio clínico inteiro**: questão comportamental, sem
  nenhum quadro correspondente no mapa — testa se o sistema não força uma
  leitura de urgência onde não há sinal clínico.
- **2 casos-âncora simples**: um emergência óbvia (convulsão por
  intoxicação), sem propósito de confundir — servem de referência de que o
  sistema não quebrou o básico.

Não incluí nenhum texto igual aos 18 relatos `b01`-`b18` da régua de
recuperação: são instrumentos diferentes (a régua mede busca; isto mede
classificação), e reaproveitar o texto arriscaria calibrar os dois
instrumentos com os mesmos vieses de escrita.

## Verificação informal de separabilidade

Não é o baseline formal do runner (isso é trabalho da próxima rodada — seção
5.4 do plano), mas uma conferência manual antes de gastar tempo calibrando
um formato ruim: **não há palavra isolada que separe as classes**. "Dor"
aparece tanto em emergência (`p12`, "gritando de dor") quanto negada em não
emergência (`p18`, "não parece sentir dor nenhuma"); "comendo e brincando"
aparece em não emergência (`p04`, `p06`) mas o caso grave `p07` também evita
qualquer palavra de alarme ("sem fazer escândalo"). O teste com os
baselines de saco de palavras fica para quando o lote for maior.

---

## O lote oficial `dev` (21/09) — `casos_oficiais.csv`, split `dev`

50 casos, escritos com a mesma disciplina do lote de calibração (muralha,
cenário clínico em vez da coluna de sinais, rótulo ancorado no MSD via o
mapa) — mas agora cobrindo o mapa de verdade, não só os 7 pares usados para
calibrar o formato.

**Balanço:** 25 emergência, 24 não emergência, 1 incerto — o par mais
próximo de 50/50 que o projeto já teve (a prova antiga era 72/28).

**Cobertura:** 47 dos 61 quadros do mapa, cada um em exatamente um caso —
nenhum tópico repetido dentro do lote `dev` (o lote `teste` é o lugar certo
para repetir tópico com apresentação diferente, já que sozinho ele tem o
dobro do tamanho).

**16 pares de confusão**, o dobro dos 7 da calibração, incluindo os que a
régua e o backlog já sinalizavam como interessantes: intoxicação por
cebola/alho × mesma ingestão sem sinal; dificuldade respiratória × espirro
leve; convulsão × tremor consciente; trauma × claudicação leve; **obstrução
uretral em cão × cistite** (o gap real que a régua achou, b15, nunca tinha
virado caso de prova); intermação × ofegação pós-exercício; torção gástrica
(tom calmo) × vômito único (tom calmo); paralisia aguda × artrose; picada
com anafilaxia × picada com reação local; insuficiência cardíaca × tosse dos
canis; emergência ocular (apresentação nova, olho fechado por dor — não
proptose, que já apareceu na calibração) × conjuntivite leve; distocia ×
parto normal.

**3 casos fora do mapa**, nenhum repetindo a exposição dos dois já usados na
calibração (ração emagrecedora, calendário de vacina, e um "incerto" com
detalhe diferente do `p15`).

**Verificações automáticas rodadas antes de gravar:** nenhum `id` duplicado,
todo `confusion_pair_id` aponta para um `id` que existe e a relação é
sempre recíproca (se `p20` aponta para `p44`, `p44` aponta de volta para
`p20`), nenhum texto duplicado dentro do lote nem repetido do lote de
calibração, todo `topic` existe no mapa, e `expected_class`/
`expected_urgency`/`species` batem exatamente com as colunas `classe`/
`urgencia`/`especie` do mapa para o tópico citado — o rótulo não é opinião
solta, é derivado mecanicamente da peça comum.

---

## O lote `teste` (21/09) — 100 casos, `casos_oficiais.csv`, split `teste`

Completa os ~150 do plano. Cobre os 14 tópicos que o `dev` não tinha tocado
(inclui o par reservado `pyometra` × `normal_estrus`) e repete boa parte dos
tópicos do `dev` com espécie, idade ou apresentação diferente — inclusive
casos de segunda profundidade que testam nuance (ex.: convulsão que dura
mais que o normal num cão já epiléptico; apetite reduzido bem no limite das
24h que o mapa usa como corte para gato adulto).

**Balanço do arquivo inteiro (dev + teste, 150 casos):** 77 emergência / 70
não emergência / 3 incerto — 51%/47%/2%, o mais perto de 50/50 que o projeto
já teve (a prova antiga: 72/28).

**Cobertura: 61 de 61 tópicos do mapa**, todos com pelo menos um caso.

**23 pares de confusão** no arquivo inteiro, incluindo 3 pares que atravessam
os dois lotes (ex.: `p77`, do lote `teste`, forma par com `p47`, do lote
`dev` — a régua de recuperação e a prova de classificação não precisam
nascer no mesmo lote pra se testarem).

**O passo automático da regra 4 da muralha existe agora:**
[`backend/app/database/check_prova_overlap.py`](../../backend/app/database/check_prova_overlap.py)
compara os 150 casos contra os documentos reais da base (via os chunks já
extraídos na coleção do ChromaDB, não abrindo os PDFs/TXT de novo) por
sobreposição de sequências de 6 palavras. Rodado contra a coleção de 3.481
chunks do trilho A: **nenhum dos 150 casos compartilha 6 palavras seguidas
com nenhum documento.**

**Verificação informal de separabilidade, honesta sobre o que achou:** nas
150 linhas, cinco palavras de conteúdo aparecem concentradas demais numa
classe só — `"agora"` e `"repente"` só em casos de emergência, `"comendo"`
só em não emergência. `"repente"` e `"comendo"` fazem sentido clínico (início
súbito é um discriminador real do MSD; "comendo normal" é a frase padrão de
tranquilidade) — não são bugs, mas são exatamente o tipo de atalho que um
baseline de saco de palavras vai explorar. Registrado aqui para quando os
baselines triviais novos (seção 5.4 do plano) forem construídos: é esperado
que eles peguem algum sinal nessas palavras, e isso não invalida a prova —
só significa que a acurácia do baseline não vai ser zero, e o critério do
B-05 (abaixo de 0,90) segue sendo o que decide se é problema.

## Próximo passo

**Congelar o lote `teste` por hash**, agora que as verificações automáticas
(id, pares, sobreposição interna, sobreposição com a base, rótulo batendo
com o mapa) estão todas limpas — falta uma decisão do time (ou minha,
seguindo o pedido do Vinicius) sobre o momento exato de congelar, já que
depois disso nenhuma linha do `teste` pode ser reescrita mesmo se o sistema
errar nela.

**Baselines triviais novos** (saco de palavras com validação cruzada,
palavra de alarme, comprimento do relato) — agora há amostra (150 casos)
suficiente para calibrá-los. É o próximo item da seção 5.4 do plano.
