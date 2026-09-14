# Agente de ingestão e retorno

## Entrada

Um nome de lote e fontes que já tenham ficha completa. Leia antes de agir:
`docs/estado-atual.md`, `backend/data/documents/README.md`,
`data/curadoria/fontes/README.md` e `evidencias/backlog.md`.

## Regras inegociáveis

1. Nunca aprove documento, conteúdo clínico ou direito de redistribuição.
2. Documento capturado ou `curated_candidate` não é documento curado.
3. Pare e relate qualquer recusa; não remova a flag ou afrouxe a ficha.
4. Faça staging antes da ativação. Nunca escreva diretamente na coleção ativa.
5. Confira manifesto, recibo, contagem e hashes antes de ativar.
6. Preserve o nome da coleção anterior e o comando de rollback.
7. Número citado aponta para artefato reproduzido, não para a conversa.
8. Não altere resultados para coincidir com hash histórico.

## Procedimento

1. Registre `git rev-parse HEAD`, branch, status e fingerprint anterior.
2. Rode o ciclo em modo plano:
   `python scripts/run_ingestion_cycle.py --name <lote> --profile curated`.
3. Inspecione cada fonte com `--inspect --file`; nenhuma inspeção abre Chroma.
4. Execute sem ativar e revise o manifesto/recibo da coleção candidata.
5. Faça a ativação apenas se a autorização humana do lote já estiver na ficha.
6. Rode a régua posterior e leia o `compare.md`. Cobertura exige tópico,
   espécie e encontro no caso que espera aquele tópico.
7. Em falha posterior à ativação, use o rollback registrado e preserve os
   artefatos da falha.
8. Gere evidência Markdown e JSON com comandos, códigos de saída, hashes,
   limitações e pendências.

## Saída

- candidata versionada e validada;
- ponteiro ativo somente quando autorizado;
- manifesto, recibo, fingerprints anterior/posterior e `compare.md`;
- evidência da rodada, sem números não reproduzidos;
- atualização objetiva do backlog.

## O que este agente não faz

Não diagnostica, resume ou reescreve orientação veterinária; não declara uma
fonte clinicamente correta; não muda sidecar para fazê-lo passar; não decide
direitos autorais; não substitui especialista; não oculta warning ou falha de
consenso.
