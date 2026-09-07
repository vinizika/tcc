# Evidências — Vinicius de Castro Duarte · Trilho A (Recuperação e Conhecimento)

Trilho responsável pela **base de conhecimento e pela busca**: curadoria dos
documentos, extração e chunking, embeddings, ChromaDB, ordenação da recuperação
e re-ranking.

- **[planejamento.md](planejamento.md)** — estado atual, próxima entrega e
  bloqueios do trilho.
- **[../backlog.md](../backlog.md)** — fila única de melhorias do projeto.
- [`docs/divisao-de-trabalho.md`](../../docs/divisao-de-trabalho.md) — escopo,
  fronteiras e acordos do time.
- [`docs/CONTRATOS.md`](../../docs/CONTRATOS.md) — contrato do documento
  recuperado entregue ao trilho B2.
- [`../README.md`](../README.md) — padrão destes registros.

## Rodadas

| # | Data | Rodada | Resultado |
|---|---|---|---|
| 1 | 07/09 | [Auditoria do repositório e estado do trilho A](2026-09-07-01-auditoria-do-repositorio.md) | Repositório sincronizado; achados anteriores separados dos novos; base local confirmada com 18 chunks de 7 protocolos; próximos passos do trilho definidos |
| 2 | 07/09 | [Ingestão científica com seções e tokens](2026-09-07-02-ingestao-cientifica-token-aware.md) | Pipeline determinístico implementado; paper real inspecionado em 200 chunks, mediana 90,5 e máximo 128 tokens; ChromaDB não alterado |
| 3 | 07/09 | [Extração científica orientada a layout](2026-09-07-03-extracao-cientifica-layout-aware.md) | PyMuPDF e heurísticas genéricas de blocos/colunas adotados; seis captions, 15 headers e quatro blocos editoriais removidos; paper passou a 186 chunks, máximo 119; sete PDFs antigos preservados e Chroma ainda com 18 registros |

## Estado atual

O pipeline de recuperação funciona de ponta a ponta, mas ainda não cumpre a
missão do trilho: colocar o documento correto nas primeiras posições de forma
comprovada. A régua própria de recuperação ainda não existe, o re-ranking é
apenas uma ordenação pelo score original e a base tem somente sete protocolos
sintéticos, todos voltados a emergências.

A preparação documental já possui inspeção sem escrita, seções, chunks por
tokens e extração multicoluna por coordenadas. O primeiro paper real foi
validado localmente, mas ainda não foi inserido: a base experimental continua
deliberadamente nos 18 chunks anteriores.

O impacto no sistema já foi medido pelo trilho B2. O melhor braço atual é o
LLM sem RAG, com 0,893 de acurácia balanceada e 8 falsos não urgentes em 71.
Com RAG direto, a acurácia balanceada cai para 0,763 e os falsos não urgentes
sobem para 30. No pipeline completo mais recente, chegam a 40.

O detalhe da auditoria e a distinção entre descobertas da equipe e achados
novos estão na [rodada 1](2026-09-07-01-auditoria-do-repositorio.md).
