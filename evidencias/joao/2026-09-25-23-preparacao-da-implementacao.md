# Preparação da implementação e o lote teste da prova 1 congelado

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2, olhando o sistema inteiro
(o congelamento é do instrumento do B1) · **Rodada:** 22 · **Commits:** este

> Primeira das oito rodadas que levam ao código a arquitetura decidida na
> [rodada 21](2026-09-24-22-arquitetura-proposta-contra-a-de-hoje.md). As
> rodadas 22 a 29 foram feitas numa madrugada só, num clone separado, com
> commits locais que o João revisa antes de qualquer push. Esta não muda
> código: fixa o ponto de partida e congela o lote que dá o número da prova 1.

## O que foi feito

1. **Ponto de partida.** Um clone novo do GitHub em `2d37a5e` (o commit que
   publicou as rodadas 14 a 21), numa branch própria. A suíte do CI roda
   inteira nele antes de qualquer mudança.
2. **Conferência dos dados.** Os lotes versionados (relatos independentes,
   piloto da prova 2, prova 1, calibração, régua e mapa) são comparados, caso a
   caso, com os arquivos que a autópsia 2 usou. Se forem os mesmos, os números
   das rodadas 14 a 21 são a referência que o código novo precisa reproduzir.
3. **O lote `teste` da prova 1 congelado por hash**, com o script do trilho B1
   ([`scripts/prova_freeze.py`](../../scripts/prova_freeze.py)), e o
   `data/prova/README.md` registrando o hash, a ressalva do
   [B-05](../backlog.md#b-05) e quantas vezes o lote foi usado.

## Por quê

- **Sem o ponto de partida conferido, a réplica não prova nada.** As rodadas
  seguintes mudam a busca, o prompt e o atendente, e o portão de cada uma é
  reproduzir um número medido na autópsia. Se o lote tivesse mudado entre a
  autópsia e o clone, uma diferença no número poderia ser do dado, e não do
  código.
- **O congelamento estava decidido e não feito.** O Ryu construiu a ferramenta
  e deixou a decisão de congelar para o time
  ([rodada 13 do Ryu](../ryu/2026-09-22-13-baselines-triviais-e-congelamento.md));
  a [rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md) decidiu congelar o
  lote e guardá-lo sem uso, como instrumento histórico com a sua ressalva. A
  implementação vai rodar muitas vezes na prova 1, e o `teste` precisa estar
  protegido antes disso.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Clone novo do GitHub, e não o repositório local do João | O repositório local é dele; a rodada noturna mexe em muito arquivo e não pode deixar nada pela metade ali. De manhã, os commits sobem um por um, sem reescrever nada |
| Checkout com as quebras de linha do repositório (LF), como no CI | Com a conversão para CRLF do Git no Windows, o `sync_retrieval_terms.py --check` falha num clone limpo: o hash do mapa é calculado sobre os bytes do arquivo (ver Observações) |
| Congelar o lote `teste` com a ressalva, sem esperar a diversificação de autoria | A diversificação que o Ryu propôs virou a prova 2 ([rodada 20](2026-09-24-21-prova-2-desenho-e-piloto.md)); a prova 1 fica como instrumento histórico, e o número final do TCC sai da prova 2 |
| Um contador de uso no README ("tocado: 0") | O valor de um lote teste é ser usado uma vez, pela configuração final. O hash impede que o lote mude; o contador torna visível quantas vezes ele foi olhado |
| O README da prova (trilho B1) muda em commit separado | É arquivo do Ryu; o commit avisa |

## Resultado esperado

_Escrito antes de rodar._

- **Suítes:** backend 242 e scripts 197 verdes; vocabulário e compilação
  limpos.
- **Dados:** os 122 relatos independentes e os 40 do piloto com id, texto,
  classe e tópico idênticos aos da autópsia; prova 1, calibração, régua e
  mapa iguais byte a byte (a menos da quebra de linha).
- **Lote teste:** 100 casos (52 emergências, 46 leves, 2 incertos), **nunca
  usado pela autópsia** (que mediu `dev`, calibração e régua: 134 casos). O
  `--freeze` grava o manifesto e a conferência sem `--freeze` passa.

## Resultado obtido

**Tudo como esperado.**

| Checagem | Resultado |
|---|---|
| `pytest backend/tests` (com `DEBUG=true`) | **242 passaram** |
| `pytest scripts/tests` | **197 passaram** |
| `sync_retrieval_terms.py --check` | limpo (depois do checkout com LF; ver Observações) |
| `compileall backend/app scripts` | limpo |
| Relatos independentes: CSV × JSON da autópsia | 122 de 122 iguais (id, texto, classe, tópico) |
| Piloto da prova 2: CSV × JSON da autópsia | 40 de 40 iguais |
| Prova 1, calibração, régua e mapa × cópia da autópsia | iguais byte a byte (sha256 `448f6d3b…`, `36978e48…`, `bd0f8f93…`, `440630fd…`) |
| Lote `teste` | 100 casos: 52 emergências, 46 leves, 2 incertos |

O congelamento:

```
$ python scripts/prova_freeze.py --cases data/prova/casos_oficiais.csv --split teste --freeze
Congelado: 100 linhas, sha256=d370a0a51d5974d124a9dbd3139710a73db3dbca1bf2185b8e6dce868fa18781
$ python scripts/prova_freeze.py --cases data/prova/casos_oficiais.csv --split teste
OK: 100 linhas batem com o congelamento de 2026-09-25T02:27:20.653066-03:00 (sha256=d370a0a5…8781).
```

Como os lotes são os mesmos, **os números das rodadas 14 a 21 são o alvo da
réplica** nas rodadas seguintes, sem ressalva de dado.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `data/prova/casos_oficiais.teste.freeze.json` | **novo**: o manifesto do congelamento (100 linhas, sha256, data) |
| `data/prova/README.md` | seção "O lote `teste` congelado (25/09)": hash, comando de conferência, ressalva do B-05, contador de uso (0); nota no "Próximo passo" original, sem apagar o texto do Ryu |
| esta evidência, `evidencias/joao/README.md` | a rodada 22 |
| `evidencias/backlog.md` | [B-71](../backlog.md#b-71) |

Commits: `9c9f92f` (abre a rodada, com o esperado), `cba543a` (o
congelamento, trilho B1) e este. Testes: 242 / 197 antes e depois.

## Observações

**1. O `--check` do vocabulário falha num clone limpo no Windows**
([B-71](../backlog.md#b-71)). O Git no Windows, com `core.autocrlf=true`,
grava os arquivos com CRLF na pasta de trabalho. O
`sync_retrieval_terms.py` calcula o `source_sha256` sobre os bytes do mapa,
então o hash do mapa com CRLF não bate com o gerado no CI (LF), e o check
diz "desatualizado" sem nada ter mudado. No clone desta rodada o checkout foi
refeito com LF (`core.autocrlf=false`), como no CI. O mesmo cuidado vale para
qualquer hash de arquivo que as rodadas seguintes criarem: o
`sync_fichas.py` da rodada 23 normaliza as quebras de linha antes do hash.

**2. O manifesto guarda o caminho com barra invertida no Windows.** O
`prova_freeze.py` grava `str(Path)`; o campo `cases_file` foi reescrito com
barra normal. O campo é só informativo (a conferência recalcula o caminho do
manifesto a partir de `--cases`). Vai junto no B-71.

**3. O lote teste nunca foi usado, e agora está protegido.** O runner de mapa
(`run_map_triage_eval.py`) já confere o hash quando roda com `--split teste`;
o `run_evaluation.py` passa a conferir também quando ganhar o `--cases`
(rodada 25).

## Deixado para depois

- **Normalizar as quebras de linha nos hashes de arquivo** do
  `sync_retrieval_terms.py` e gravar caminhos com barra normal no
  `prova_freeze.py` ([B-71](../backlog.md#b-71)). Não foi feito aqui porque
  são arquivos de outros trilhos e o CI (Linux) não é afetado.
- **Usar o lote teste** só uma vez, pela configuração final — ou não usar, se
  a prova 2 substituir a prova 1 como instrumento final
  ([B-63](../backlog.md#b-63)).

## Próximo passo

A [rodada 23](2026-09-25-24-fichas-de-busca-e-de-leitura.md): o script que
gera, a partir do mapa e dos rascunhos versionados, o arquivo de fichas que o
backend lê.

```
python scripts/sync_fichas.py && python scripts/sync_fichas.py --check
```
