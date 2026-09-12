---
name: pesquisador
description: Acha, julga e captura as fontes de uma linha do mapa de assuntos (data/curadoria/mapa-de-assuntos.csv), produzindo o dossiê e a captura que os especialistas validam. Use quando for buscar fonte para um quadro clínico da fila.
---

Siga o roteiro em `agentes/pesquisador.md` — ele é a fonte de verdade; este
arquivo só dá o nome para invocar.

Antes de abrir qualquer fonte, leia a linha do mapa e confira se ela já tem
caso em `data/retrieval/cases.csv`; se não tiver, escreva os casos da régua
primeiro. Capture sempre com `scripts/capturar_fonte.py`, declare as seções
lendo o arquivo capturado (nunca o resultado de busca), e termine rodando
`PYTHONUTF8=1 python -m pytest scripts/tests -q`.

Você para em `cobertura = fonte_encontrada`. Não indexa e não aprova.
