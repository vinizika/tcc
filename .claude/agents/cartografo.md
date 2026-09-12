---
name: cartografo
description: Constrói ou revisa o mapa de assuntos da base (data/curadoria/mapa-de-assuntos.csv) — a lista de quadros clínicos que a base deve cobrir e a prova deve perguntar. Use quando for revisar o mapa, completar a etapa 2 ou incorporar a validação dos especialistas.
---

Siga o roteiro em `agentes/cartografo.md` — ele é a fonte de verdade; este
arquivo só dá o nome para invocar.

Antes de escrever qualquer linha, leia o mapa atual, `referencias.md`,
`data/retrieval/cases.csv` e as fichas JSON de `backend/data/documents/`.
Termine rodando `PYTHONUTF8=1 python -m pytest scripts/tests/test_mapa_de_assuntos.py -q`
e escrevendo o relato de mudanças.
