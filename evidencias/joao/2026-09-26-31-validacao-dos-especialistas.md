# A validação dos especialistas, registrada

**Data:** 26/09/2026 · **Trilho:** B2 · **Rodada:** 30 ·
**Commits:** este

> Rodada de **registro**, sem mudar o sistema. Depois da rodada noturna, a
> ASAVET validou, por intermédio do Vinicius, tudo o que estava esperando
> especialista: a folha de certificação das fichas, as fontes novas, os
> documentos aprovados que tratam de outro assunto e os rótulos da prova 2.
> Esta rodada põe essas respostas nos arquivos. Nenhum texto que o sistema lê
> muda aqui; levar o conteúdo certificado para a ficha de leitura é a próxima
> rodada, e ela é medida.

## O que foi feito

1. **A folha de certificação das fichas** (`data/curadoria/fichas/CERTIFICACAO.md`,
   [B-61](../backlog.md#b-61)): os 513 itens marcados como aceitos, com quem e
   quando no topo da folha. Os 61 rascunhos ganham o bloco `certificacao`, e as
   36 frases com fonte nova passam de `aprovacao: pendente` para `aprovada`.
2. **As 47 fontes que esperavam especialista** (`data/curadoria/fontes/PARA-VALIDAR.md`):
   as 45 da [rodada 27](2026-09-25-28-fontes-para-tutor-etapa-2.md) e as 2
   capturas CC BY de 20/09 (torção gástrica e vômito isolado). Veredito na folha
   e no sidecar de cada uma (`validation_status: approved_by_specialist`,
   `specialist: ASAVET`); no mapa, as duas linhas de 20/09 passam a
   `cobertura: fonte_aprovada`.
3. **Os seis documentos aprovados que tratam de outro assunto**
   ([B-72](../backlog.md#b-72)): confirmados como estão.
4. **Os 330 rótulos da prova 2** ([B-63](../backlog.md#b-63)):
   `data/prova2/validacao.json` registra a validação, o `prova2_montar.py`
   passa a escrever o `marked_by` a partir dele, e o `casos.csv` é gerado de
   novo.
5. **Backlog, README e planejamento do João.**

## Por quê

Eram as pendências de especialista de quatro itens do backlog, e a próxima
entrega depende delas: a prova 2 só pode ser dividida e congelada com os
rótulos validados, e o conteúdo da etapa 2 só pode ir para a ficha de leitura
depois de certificado.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Registrar agora; levar o conteúdo ao mapa numa rodada à parte | Os rascunhos da etapa 2 e os `por_que_importa` certificados viram texto da ficha de leitura, e o número do sistema depende desse texto: é rodada medida ([rodada 23](2026-09-25-24-fichas-de-busca-e-de-leitura.md)) |
| "Validado" = aceito como está, sem correção | É o que o João relatou: tudo validado, sem mudanças. Uma correção futura de especialista vira rodada própria |
| A data registrada é 26/09/2026 | É a data do registro. A validação foi feita entre 25 e 26/09; o dia exato não foi passado |
| As fontes novas continuam fora da base (`backend/data/documents/`) e com o `ingestion_scope` de antes | Falta a decisão de direitos ([B-75](../backlog.md#b-75)); é a mesma regra das validações de 16 a 20/09: o aval do especialista não ativa nada sozinho |
| Os relatos independentes e o piloto continuam com o rótulo dado pela IA | Não faziam parte do que ia para os especialistas; são diagnóstico, não prova |

## Resultado esperado

_Escrito antes de fazer._

- **Nenhum texto que o sistema lê muda**: os 61 textos de busca e os 61 de
  leitura com o mesmo sha256; as referências das fichas iguais (elas vêm só da
  base aprovada, que não muda). A coleção reindexada seria idêntica.
- No `backend/data/fichas.json` e no `retrieval_terms.json`, muda só o
  cabeçalho com os hashes das fontes (os rascunhos e o mapa mudaram de status).
- No `casos.csv` da prova 2, muda só a coluna `marked_by`, nas 330 linhas; os
  rótulos, os textos e os ids ficam iguais.
- `sync_fichas.py --check`, `sync_retrieval_terms.py --check` e
  `prova2_montar.py --check` limpos; suítes iguais às da rodada 29 (285 · 216 ·
  10), mais o teste novo do `marked_by`.

## Resultado obtido

**Registrado, e nada que o sistema lê mudou.**

| Conferência | Resultado |
|---|---|
| Os 61 textos de busca e os 61 de leitura, as referências e os títulos das fichas | **iguais**, comparados campo a campo com o `fichas.json` de antes |
| `backend/data/fichas.json` | só o cabeçalho (hash dos rascunhos e do mapa) |
| `backend/data/retrieval_terms.json` | só o `source_sha256` do mapa |
| `data/prova2/casos.csv` | só a coluna `marked_by`, nas 330 linhas; rótulos, textos e ids iguais. sha256 `937c8724…` → `f750c7c2…` (o validado está em `validacao.json`) |
| Folha de certificação | 513 itens marcados como aceitos; nenhum em aberto |
| Fontes | 47 sidecars `approved_by_specialist` (ASAVET, 26/09); 47 vereditos no `PARA-VALIDAR.md` |
| Mapa | torção gástrica e vômito isolado: `fonte_encontrada` → `fonte_aprovada` |
| Rascunhos das fichas | 61 com o bloco `certificacao`; 36 frases `aprovacao: aprovada` |

`sync_fichas.py --check`, `sync_retrieval_terms.py --check` e
`prova2_montar.py --check` limpos. **Suíte:** backend 285, scripts 216 →
**217** (o teste do `marked_by`), `mock/` 10.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `data/curadoria/fichas/CERTIFICACAO.md`, `README.md` | os 513 itens marcados; a nota da certificação no topo; o estado das fichas |
| `data/curadoria/fichas/<topic>.json` (61) | bloco `certificacao` (quem, quando, resultado); `aprovacao: aprovada` nas 36 frases com fonte nova |
| `data/curadoria/fontes/capturas/*.json` (47) | `validation_status`, `specialist` e, nas da rodada 27, a nota de curadoria |
| `data/curadoria/fontes/PARA-VALIDAR.md` | os 47 vereditos e a nota nas duas seções |
| `data/curadoria/fontes/README.md`, `gastric_dilatation_volvulus.md`, `single_vomiting_or_mild_diarrhea.md` | o estado das duas capturas CC BY |
| `data/curadoria/mapa-de-assuntos.csv` | `cobertura`, `validacao` e `observacoes` das duas linhas |
| `data/prova2/validacao.json` | **novo**: o registro da validação dos rótulos |
| `scripts/prova2_montar.py`, `scripts/tests/test_prova2_pedidos.py` | o `marked_by` sai do registro (`marcado_por()`), com teste |
| `data/prova2/casos.csv`, `README.md` | gerado de novo; o README diz que os rótulos estão validados |
| `backend/data/fichas.json`, `backend/data/retrieval_terms.json` | gerados de novo (só cabeçalho) |
| `evidencias/backlog.md` | B-61, B-62, B-63 e B-72 atualizados |
| `evidencias/joao/README.md`, `planejamento.md` | a rodada 30, o estado atual, a próxima entrega |

Commits: este.

## Observações

**1. As duas capturas CC BY de 20/09 estavam registradas de dois jeitos.** Os
sidecars da base (`backend/data/documents/`) já as davam como aprovadas pela
ASAVET em 20/09; a curadoria (o sidecar da captura, o dossiê, o mapa e o
`PARA-VALIDAR.md`) dizia que esperavam a validação do arquivo exato. É o mesmo
arquivo (mesmo sha256). Agora a curadoria registra a validação de 26/09 e anota
que a base já trazia 20/09; a base não foi tocada.

**2. A prova 1 continua com rótulo provisório** (`marked_by` = "Ryu -
provisorio, aguardando validacao de especialista", nas 150 linhas). Não estava
no pedido: o número final sai da prova 2.

**3. A prova 2 não ficou fácil para a busca.** Em 25/09, a pedido do João,
conferi se a pesquisa mais fraca dos autores
([rodada 28](2026-09-25-29-prova-2-geracao.md)) tinha deixado os relatos
parecidos demais com as fichas. Método: o bge-m3 da arquitetura (a mesma
revisão) nos 61 textos de busca, a posição da ficha certa para cada relato com
quadro do mapa. Validado antes contra os números conhecidos (piloto 16/40 e
32/40; independentes 74/122 e 94/122, iguais).

| Lote | Ficha certa em 1º | Entre as 3 |
|---|---|---|
| Prova 1 + régua | 83% | 95% |
| Relatos independentes | 61% | 77% |
| Piloto | 40% | 80% |
| **Prova 2 (305 relatos)** | **54%** | **79%** |

Não há correlação entre o número de fontes do caderno do autor e o acerto da
busca (Spearman ρ = −0,10, p = 0,46). Os lotes variam: os lotes 2 e 4 ficam
mais fáceis (70–72% em 1º) e os lotes 1 e 5 mais difíceis (33–38%). É um ponto
para a conferência do [B-63](../backlog.md#b-63).

**4. O B-71 apareceu de novo.** No Windows, o `sync_retrieval_terms.py`
regravou o `retrieval_terms.json` com CRLF (o arquivo inteiro aparecia como
mudado); normalizei para LF, como na rodada 23.

## Deixado para depois

- **Levar o conteúdo certificado à ficha de leitura** — as 60 células da etapa
  2 e a coluna `por_que_importa` no mapa —, medido contra a réplica
  ([B-61](../backlog.md#b-61)).
- **A prova 2 até o uso**: o resto da conferência, a divisão por assunto e o
  congelamento ([B-63](../backlog.md#b-63)).
- **As fontes validadas na base** (`backend/data/documents/`) e os ids `R..`,
  depois da decisão de direitos ([B-62](../backlog.md#b-62),
  [B-75](../backlog.md#b-75)).
- **A autoria dos seis sidecars** pelo Crossref ([B-72](../backlog.md#b-72)).

## Próximo passo

A rodada 31: preencher no mapa as colunas da etapa 2 e `por_que_importa` com
o texto certificado, regerar as fichas e a coleção
(`python scripts/sync_fichas.py`,
`python -m app.database.ingest_documents --profile fichas --activate`) e medir
com o Gemini e o qwen nos mesmos lotes da réplica, com o resultado esperado
escrito antes.
