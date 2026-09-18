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
| 2 | 08/09 | [Endurecimento do upload de voz](2026-09-08-02-endurecimento-do-upload-de-voz.md) | **B-32 resolvido**: `POST /voice/` grava com nome do servidor, valida tipo (415) e tamanho (413), apaga o arquivo em `finally`; 7 testes novos, suíte do backend em 99 |
| 3 | 08/09 | [Whisper único e benchmark de WER](2026-09-08-03-whisper-unico-e-wer.md) | **B-13 resolvido**: 2 implementações órfãs apagadas, `VoiceService` sozinho; harness de WER em `scripts/` com 18 relatos PT-BR sintéticos (edge-tts). WER inaugural registrado na evidência — limite otimista, a repetir com áudio real |
| 4 | 13/09 | [Primeiro lote da prova nova](2026-09-13-04-primeiro-lote-da-prova-nova.md) | Formato da prova de classificação em `data/prova/`, referência de triagem escolhida (MSD, 3 níveis, igual ao mapa de assuntos), 18 casos de calibração com 7 pares de confusão desenhados. Rodado contra a API: 15/18, as 3 falhas são falsos não urgentes por tom do relato ou sinal não extraído — inclusive o par de maior letalidade do mapa (obstrução uretral) |
| 5 | 13/09 | [Cadastro de tutor/pet e histórico de conversa](2026-09-13-05-cadastro-de-tutor-pet-e-historico.md) | Persistência nova e independente dos outros trilhos: tutores/pets no Supabase, histórico de conversa no MongoDB (local no compose), `pet_id` em `/chat/` injeta o cadastro no prompt de triagem. Sem autenticação real ainda ([B-56](../backlog.md#b-56), registrado). Testes: backend 134 → 181 |
| 6 | 17/09 | [Medindo consulta nas candidatas experimentais](2026-09-17-06-medindo-consulta-nas-candidatas.md) | **B-09 e B-10 resolvidos** — primeira medição real das técnicas de consulta, contra as 3 coleções experimentais do trilho A. HyDE nunca ajudou (`HYDE_ENABLED` passou a `False`); fundir reescrita+multi-query (B-10) nunca perde. Achado colateral: [B-57](../backlog.md#b-57), o snapshot versionado do Chroma está num caminho que o backend real não lê |

## Estado atual

Query Rewriting, Multi-Query e HyDE já existem e estão plugados no pipeline
via flags (`QUERY_REWRITING_ENABLED`, `MULTI_QUERY_ENABLED`, `HYDE_ENABLED`).
O que falta é medição e alguns ajustes pontuais — detalhados no
[planejamento.md](planejamento.md).
