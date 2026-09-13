# Prova nova — primeiro lote de calibração

Trilho **B1** (Ryu). Contexto completo em
[`docs/plano-base-e-prova.md`](../../docs/plano-base-e-prova.md), seção 5
("Frente prova"). Este diretório é onde a prova nova vai morar; hoje só tem o
**lote de calibração** — não é ainda o conjunto de desenvolvimento nem o de
teste, que vêm depois de calibrar o formato com o time.

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
| `difficulty_tag` | `controle_emergencia` / `controle_leve` (âncoras fáceis) · `par_confuso` · `alarme_leve` (tem palavra de risco, é leve) · `calma_grave` (tom calmo, é grave) · `fora_da_base` (quadro real, sem documento hoje) · `informacao_insuficiente` · `fora_do_dominio_clinico` |
| `note` | Justificativa clínica da rotulagem e o que o caso testa |
| `source_reference` | Aponta para a linha do mapa de assuntos que fundamenta o quadro (que por sua vez carrega a referência publicada) |
| `marked_by` | Quem marcou — hoje sempre eu, **provisório até validação de especialista**, mesmo padrão do `data/retrieval/cases.csv` |
| `split` | `calibracao` em todo o lote — nenhuma linha daqui entra no conjunto de desenvolvimento ou de teste sem ser reescrita como parte do lote oficial |

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

## Próximo passo

Rodar este lote contra a API (registrado na evidência da rodada,
`evidencias/ryu/`) para ver como o sistema **hoje** — sem CoT, sem RAG —
se comporta nos pares difíceis, antes de escrever o lote grande (~150
casos). Depois: levar o formato ao time para validação, e só então escrever
o restante.
