# Evidências — Julian Ryu Takeda · Trilho B1 (Consulta)

Trilho responsável pelo caminho **do relato do tutor até a busca**: Query
Rewriting, Multi-Query, HyDE e a transcrição de voz (Whisper).

- **[planejamento.md](planejamento.md)** — o que já foi feito, o que vem a
  seguir e o que está travando.
- **[../backlog.md](../backlog.md)** — a fila única de melhorias do projeto,
  compartilhada pelos três; é para lá que vão as observações que exigem ação.
- [`docs/divisao-de-trabalho.md`](../../docs/divisao-de-trabalho.md) — escopo
  e fronteiras entre os trilhos.
- [`../README.md`](../README.md) — o padrão destes registros.

## Rodadas

| # | Data | Rodada | Resultado |
|---|---|---|---|
| 1 | 04/09 | [Reprodutibilidade das chamadas de consulta](2026-09-04-01-reprodutibilidade-da-consulta.md) | B-04 fechado no nível de unidade: as três chamadas do `query_client.py` passam a usar `options=default_options()`; falta confirmar o critério numérico com Ollama de pé |

## Estado atual

Query Rewriting, Multi-Query e HyDE já existem e estão plugados no pipeline
via flags (`QUERY_REWRITING_ENABLED`, `MULTI_QUERY_ENABLED`, `HYDE_ENABLED`).
O que falta é medição e alguns ajustes pontuais — detalhados no
[planejamento.md](planejamento.md).
