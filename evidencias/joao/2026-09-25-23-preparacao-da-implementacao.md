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

_(preenchido ao fechar a rodada)_

## O que mudou no repositório

_(preenchido ao fechar a rodada)_

## Observações

_(preenchido ao fechar a rodada)_

## Deixado para depois

_(preenchido ao fechar a rodada)_

## Próximo passo

_(preenchido ao fechar a rodada)_
