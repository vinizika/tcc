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
| 7 | 17/09 | [Conter julgamento clínico na reescrita](2026-09-17-07-conter-julgamento-clinico-na-reescrita.md) | **B-08 resolvido** — prompt com exemplo negativo explícito, mais guarda-corpo determinístico (`_contains_unwarranted_urgency`) que descarta a reescrita e devolve o relato original quando ela injeta "imediata"/"urgente"/"emergência" ausentes do relato. 2 testes novos, suíte do backend em 207 |
| 8 | 17/09 | [Paralelizando Multi-Query e HyDE](2026-09-17-08-paralelizando-multi-query-e-hyde.md) | **B-07 em andamento** — as duas chamadas, independentes entre si, agora rodam em `ThreadPoolExecutor` quando ambas ligadas; sobreposição confirmada nos logs de uma chamada real. Falta medir `query_s` mediano com modelo aquecido e coleção com conteúdo — critério numérico do item ainda não fechado. Suíte do backend em 208 |
| 9 | 21/09 | [Medindo latência com modelo aquecido](2026-09-21-09-medindo-latencia-com-modelo-aquecido.md) | Medido contra a coleção final do trilho A (3.481 chunks): a paralelização economiza 13–39% da etapa de consulta, nunca piora. Critério numérico (`query_s` < 1,5s) segue em aberto — este ambiente roda o Ollama 100% CPU, sem GPU; falta remedir num ambiente com GPU |
| 10 | 21/09 | [Runner de texto livre reaproveitado](2026-09-21-10-runner-de-texto-livre-reaproveitado.md) | **Entrega 6 concluída** — em vez de escrever um runner novo, estendi `scripts/run_map_triage_eval.py` (já do Vinicius) com `--cases`, `--split` e `--runs-dir`. Testado contra o lote de calibração: 3/3 corretos. Falta só o lote oficial (~150 casos) para a prova nova rodar de verdade |
| 11 | 21/09 | [Lote dev da prova oficial](2026-09-21-11-lote-dev-da-prova-oficial.md) | **Entrega 5 em andamento** — 50 casos em `data/prova/casos_oficiais.csv` (`split=dev`), 47 de 61 tópicos cobertos, 16 pares de confusão, balanço 25/24/1. Zero inconsistências nas checagens automáticas (ids, pares recíprocos, sobreposição de texto, rótulo batendo com o mapa). Falta o lote `teste` (~100 casos) |
| 12 | 22/09 | [Lote teste + verificador de sobreposição](2026-09-22-12-lote-teste-e-verificador-de-sobreposicao.md) | **Entrega 5 substancialmente completa** — 100 casos novos (`split=teste`), cobertura total do mapa (61/61), balanço final 77/70/3 (150 casos). Verificador automático da regra 4 da muralha (`check_prova_overlap.py`): zero sobreposição de 6-grama com a base. Achado honesto: "agora"/"comendo" concentradas numa classe só, registrado para os baselines triviais. Falta só congelar por hash. Suíte do backend em 229 |

## Estado atual

Query Rewriting, Multi-Query e HyDE já existem e estão plugados no pipeline
via flags (`QUERY_REWRITING_ENABLED`, `MULTI_QUERY_ENABLED`, `HYDE_ENABLED`).
O que falta é medição e alguns ajustes pontuais — detalhados no
[planejamento.md](planejamento.md).
