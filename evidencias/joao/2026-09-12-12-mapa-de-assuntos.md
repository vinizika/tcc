# Mapa de assuntos: os 61 quadros que a base deve cobrir

**Data:** 12/09/2026 · **Trilho:** B2, para as duas frentes · **Rodada:** 11 ·
**Commit:** este

> **Rodada de construção, não de medição.** Não há esperado × obtido: o
> produto é um artefato — o mapa — e o que se registra aqui são as decisões,
> o que a pesquisa mudou no desenho, e o que **não** foi possível verificar.
> Os números da rodada são de cobertura e de checagem, não de acurácia.

## O que foi feito

Uma planilha com os quadros clínicos que a base deve cobrir e sobre os quais a
prova deve perguntar: [`data/curadoria/mapa-de-assuntos.csv`](../../data/curadoria/mapa-de-assuntos.csv),
61 linhas, cada uma com espécie, classe, urgência, os sinais que o tutor
relata, o **par de confusão** (a gêmea leve que usa as mesmas palavras do
quadro grave), a **pergunta que separa os dois**, a referência publicada e o
estado na fila. Mais o roteiro do agente que a constrói
([`agentes/cartografo.md`](../../agentes/cartografo.md)), as referências com o
grau de verificação de cada uma, dois arquivos de checagem contra os datasets,
e um teste de 18 asserts que trava a forma do arquivo.

É a peça comum das duas frentes do [plano](../../docs/plano-base-e-prova.md):
o pesquisador busca fonte por linha; o `compare` do agente 2 mede cobertura
contra as linhas; o Ryu escolhe o que a prova pergunta e o que fica fora.

## Por quê

O bloqueio 11 do meu planejamento diz: **a base não cobre os assuntos que a
prova pergunta**. Base e prova foram montadas por caminhos independentes, e a
[rodada 11 da régua](2026-09-12-11-regua-de-recuperacao.md) mediu um pedaço
disso — quatro dos dezoito casos tratam de quadros que nenhum protocolo cobre.
Sem uma lista comum, ampliar a base e refazer a prova em paralelo reproduz o
problema com mais documentos.

E porque "emergências veterinárias" não é critério de busca: devolve duzentas
possibilidades. O mapa é o que transforma "ampliar a base" em uma fila de 61
tarefas com prioridade.

## Como foi construído: o que a pesquisa mudou no desenho

O João pediu fundamentação em medicina veterinária de emergência. Antes de
escrever uma linha, levantei três coisas com fonte — referências publicadas
de triagem e casuística de pronto-socorro, o que é específico do Brasil, e os
sinais que separam "pode esperar" de "emergência" para cada queixa que um
tutor traz. Cinco achados mudaram o desenho em relação ao que estava no plano:

| Achado | Fonte | O que mudou |
|---|---|---|
| **Existe um classificador de três níveis pronto, com sinais observáveis pelo tutor** — *imediato* / *veterinário em até 24 h* / *rotina* | MSD Veterinary Manual, tabela *When to See a Veterinarian* | Virou a coluna `urgencia`. O sistema segue binário + INCERTO; o mapa preserva a nuance |
| **O que mais chega ao pronto-socorro**: cães — vômito/diarreia, dispneia, trauma, convulsão, letargia; gatos — **dispneia** e **disúria** no topo | Lee et al. 2014, 3.180 atendimentos | Define a prioridade A. Coincide com o que a base já tinha — e diz que obstrução uretral é a causa nº 1 em gatos |
| **O eixo toxicológico do Brasil não é o americano**: "chumbinho" = **50% das intoxicações em gatos** na USP (46 de 96); diclofenaco é o medicamento nº 1 em cães; paracetamol em gato sempre dado pelo próprio tutor | Catozo 2022 · de Paula 2022 · Xavier 2002 · Medeiros 2009 | Três linhas de toxicologia com prioridade A que nenhuma lista importada (ASPCA, AAHA) traria |
| **22 pares de confusão, cada um com a pergunta que separa** — "sai alguma coisa quando vomita e a barriga está dura?", "sai urina quando faz força?", "apoia a pata?" | MSD, VCA, PDSA, Cornell, International Cat Care | A coluna `discriminador`. É a inteligência clínica que serve à base **e** à prova |
| **"É gato?" é a pergunta de maior poder isolado**: muda a urgência em boca aberta, não comer 24 h, esforço urinário, paracetamol, permetrina, lírio, queda de altura | PDSA · Cornell · International Cat Care | Cobertura conferida **por espécie**; a permetrina em gato entrou na etapa 1 como a única linha exclusiva de gato |

E duas coisas que eu **não** tinha visto e a pesquisa mostrou: corrimento
vulvar em fêmea inteira é emergência unânime, não zona cinzenta (piometra
entrou na etapa 1); e a Resolução CFMV 1.465/2022 define *emergência* e
*urgência* e **proíbe teleconsulta em ambas** — o artigo precisa posicionar o
sistema como orientação e encaminhamento, não como teleconsulta.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | **O `id` da linha é o `topic` da ficha JSON** | O `compare` mede cobertura por igualdade exata. Uma linha, um assunto indexável |
| 2 | **Duas colunas de classificação**: `classe` (binária) e `urgencia` (três níveis), com regra de colapso fixa — `imediato` → emergência, o resto → pode esperar | Segue as definições que o prompt já usa. As linhas `ate_24h` são a zona cinzenta, marcadas para os especialistas |
| 3 | **Coluna `discriminador`** | A pergunta que separa o par é o que o documento precisa responder e o relato da prova precisa conter |
| 4 | **Pares atravessam as classes, muitos-para-um** | Uma linha leve pode ser gêmea de várias emergências; "vomitou" abre para quatro quadros. O teste recusa par que não atravessa |
| 5 | **Dois estados, não um**: `cobertura` (tem documento?) e `validacao` (especialista concordou?) | Misturar os dois confunde "a base cobre" com "está certo" |
| 6 | **Prioridade por regra escrita** (A/B/C) e **etapa como corte móvel**, decidido numa porta com critérios pré-registrados | O João não quis ficar preso a 61 nem a 31: a velocidade e o `compare` decidem. Porta sem critério vira "achamos que foi bem" |
| 7 | **Primeira convulsão = imediato** (Cornell), não observação em casa (PDSA) | Em pré-triagem de leigo, o erro grave é o falso não urgente |
| 8 | **Gato fazendo força para urinar vai agora, mesmo que saia um pouco** | PDSA: "never wait to see if your cat improves"; Cornell: morte em menos de 24–48 h. A linha leve ficou só para urina saindo normalmente |
| 9 | **Referências em arquivo próprio, com grau de verificação** (`direta` / `resumo` / `bloqueada`) | A honestidade sobre o que foi lido fica num lugar só; 40 referências, 6 delas não lidas de verdade |
| 10 | **Datasets são vocabulário, nunca rótulo** | O `dataset1` é a prova atual; usar suas combinações para montar a base é olhar a chave de resposta |
| 11 | **Sinais sem frases completas** | A coluna alimenta a base; se a prova copiasse daqui, a busca acertaria por eco |
| 12 | **`SEM_FONTE` é permitido e visível** | Declarar lacuna é melhor que inventar referência, e um `grep` a encontra |

## A revisão crítica, no mesmo dia

O primeiro rascunho tinha 25 linhas na etapa 1. O João pediu revisão
criteriosa, e ela achou problemas reais:

- **O maior buraco era colapso e apatia.** Letargia está entre as cinco
  queixas mais frequentes do PS nas duas espécies; gengiva pálida é item da
  AAHA; e **oito termos do dataset** tinham ficado "inespecíficos" só porque
  não havia linha. Entraram `collapse_and_pale_gums` e sua gêmea
  `reduced_appetite_no_other_signs`.
- **Inconsistência com a própria régua**: o caso b11 (conjuntivite leve) não
  tinha linha. Entrou o par ocular.
- **Parvovirose estava na etapa 2 com prioridade A** — contradição. Subiu.
- **O par de maior letalidade estava permissivo**: minha linha leve aceitava
  "sai um pouco de urina". Verificado nas fontes e reescrito (decisão 8).
- **O teste pegou dois erros meus**: síndrome vestibular e ferida de briga de
  gato estavam como "emergência" com urgência "até 24 h" — contradição com a
  regra que eu mesmo escrevi. Vestibular virou imediato (leigo não distingue
  a forma periférica da central); briga de gato virou pode esperar com a
  janela de 6 h anotada.
- **Duas lacunas fechadas**: sapo (Sonne et al. 2008, Ciência Rural, UFRGS)
  e hipoglicemia de filhote toy (Veterinary Partner — bloqueada, mas existe).
  **Uma linha nova**: exposição à raiva por morcego ou animal silvestre,
  porque o termo `Hydrophobia` do dataset não tinha para onde apontar.
- **Permetrina em gato subiu** a pedido do João: a etapa 1 não tinha nenhuma
  linha exclusiva de gato.

Etapa 1 final: **31 linhas** — 20 emergências e 11 leves. Inespecíficos no
vocabulário: de 40 para 32.

## O que a rodada produziu, em números

| | |
|---|---|
| Linhas no mapa | **61** — 38 emergências, 23 pode esperar |
| Etapa 1 (escrita por inteiro) | **31** — 20 emergências, 11 leves; 8 já com documento (7 sintéticos + heatstroke) |
| Etapa 2 (esqueleto) | 30 |
| Referências | 40, com grau de verificação; 3 `bloqueada`, 9 `resumo` |
| Termos do conjunto de avaliação mapeados | **162 de 194**; 32 inespecíficos, cada um com motivo |
| Doenças do `dataset2` | 34 com linha, 14 excluídas com motivo |
| Linhas com `SEM_FONTE` | 1 (doença do carrapato — só TCC como fonte) |
| Testes | scripts 92 → **110** |

## O que não foi possível verificar

Registrado para ninguém achar que foi lido:

- **A lista integral dos 68 discriminadores da VTL** (Ruys 2012, Tabela 1) —
  paywall. O mapa usa as 8 subcategorias confirmadas em fonte secundária.
  Vale acesso institucional CAPES.
- **AVMA e AAHA** bloqueiam leitura automatizada; o conteúdo veio de resumo de
  buscador e bate entre fontes, mas o texto original não foi lido.
- **International Cat Care e Blue Cross** — idem.
- **Caderno Técnico UFMG nº 87 (Emergência)** — erro de certificado; é o
  candidato mais próximo de referência brasileira institucional.
- **Casuística brasileira de escorpião e aranha em pets** — não encontrada.
- **Estudo brasileiro do setor de emergência de hospital universitário com
  percentuais por queixa** — não localizado em periódico indexado. É lacuna
  da literatura, não falha de busca.

E o mais importante: **não sou veterinário**. Errei dois gabaritos em dezoito
na régua lendo com atenção; neste mapa, o teste pegou duas contradições
minhas no mesmo dia. Cada linha carrega a referência exatamente para o
especialista discordar de **uma** sem refazer o resto.

## Observações

**1. O Brasil não cabe numa lista importada.** As listas de emergência para
tutores (AAHA, ASPCA, RSPCA) são boas e foram usadas — mas nenhuma traria
chumbinho, dipirona de balcão, cinomose em cão não vacinado, sapo no quintal
ou leptospirose. Metade das intoxicações felinas da USP é uma substância que
não aparece em nenhuma delas. Um sistema para tutores brasileiros precisa da
casuística brasileira, e ela existe — em SciELO, em revistas de CRMV, em
hospitais universitários.

**2. Cinco das onze linhas leves da etapa 1 são "até 24 h".** O sistema vai
dizer "não emergência" para elas, e a mensagem precisa dizer *consulta hoje ou
amanhã*, não *não precisa de veterinário*. Isso é do prompt, não do mapa —
mas é o mapa que mostra o tamanho da zona cinzenta.

**3. O par de confusão é onde o sistema vai ser testado de verdade.** Com os
pares todos na base, "vomitou" recupera quatro documentos legítimos, e qual
vem em primeiro decide o enquadramento. A ordenação de hoje casa com a
palavra literal (chocolate → vômito, na régua). É por isso que a porta de
decisão olha o `compare` antes de deixar a base crescer.

**4. Os 32 inespecíficos são informação, não resto.** Febre, dor, cansaço,
apatia: sinais que sozinhos não apontam quadro. Um tutor que só diz "está
apático" não pode receber "emergência" nem "pode esperar" — pode receber
INCERTO, ou uma pergunta. O mapa mostra onde o sistema precisa **perguntar**
em vez de decidir.

**5. Duas emergências sem gêmea leve.** Filhote que não mama e remédio humano
não têm versão leve honesta. O campo ficou vazio; inventar uma seria pior.

## Para os outros trilhos

- **Trilho A**: o vocabulário de `species` nas fichas tem três grafias
  ([B-53](../backlog.md#b-53)); o `compare` vai normalizar até fechar. E o
  `id` do mapa é o `topic` — documento novo entra com o `topic` de uma linha.
- **Ryu**: os casos "fora da base" da prova precisam vir de **fora do mapa**,
  porque a cobertura pode chegar a 61. O mapa diz o que está coberto; a prova
  escolhe o que não está. O caso b16 da régua continua apontando para
  `respiratory_distress` até haver documento de anafilaxia — o `compare`
  avisa quando for hora de mudar.

## Deixado para depois

**Validação pelos especialistas** ([B-50](../backlog.md#b-50)) — as 61
linhas de uma vez; classe e urgência estão em todas. Onde a atenção deles
rende mais: as `ate_24h`, a primeira convulsão, a espécie da piometra, os
tóxicos brasileiros, a raiva.

**Completar a etapa 2** — sinais e discriminador das 30 linhas, no dia em que
a porta de decisão disser "vai". Não antes.

**Casos de régua para os quadros novos** — cada linha da etapa 1 sem caso
precisa de 1 a 3 relatos, escritos a partir do mapa e **antes** de ler a
fonte, senão a busca acerta por eco.

**Os outros roteiros** ([`agentes/`](../../agentes/README.md)): pesquisador,
redator de lacuna, ingestão. E o `compare` ([B-51](../backlog.md#b-51)), que é
o que a porta de decisão lê.

## Próximo passo

Levar o mapa aos outros dois para revisão, e aos especialistas para validação.
Enquanto eles leem: o roteiro do pesquisador — a primeira linha da fila é
`gastric_dilatation_volvulus`, prioridade A, sem documento, com caso na régua.
