# Retrato da base vetorial de 18 trechos

Este é o **estado da base de conhecimento que sustenta as rodadas citadas
até 05/09**: `r3_marco1`, `r3c_um_trecho` e `b04_confirmacao`, além dos
números com RAG que aparecem no README da raiz e nas evidências do trilho B2.

Ele existe porque **essa base não pode mais ser gerada a partir do código.**
Em 07/09 o trilho A substituiu a receita de chunking (fatias de 1200
caracteres → seções, frases e tokens). Os mesmos sete PDFs, processados hoje,
produzem outros trechos, com outros identificadores e outros vetores. Sem
este arquivo, a única cópia da base antiga seriam as máquinas que já a
tinham, e ela se perderia na primeira reindexação
([B-37](../../../../evidencias/backlog.md#b-37)).

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `export.json` | Os 18 trechos: identificador, texto, metadados e o vetor de 384 dimensões de cada um |

Exportado em 11/09/2026, ordenado por identificador para o arquivo ser
estável entre execuções.

| Campo | Valor |
|---|---|
| Trechos | 18, de 7 protocolos sintéticos |
| Modelo de embedding | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Dimensões | 384 |
| `chunk_ids_sha256` | `eeba9f51d239e2f6167d18ffe87ef5e6f505de0497b222555a3cb953dd12a914` |
| `content_sha256` | `89a215ac3c7c6014b6dce500652f1c921e2a276f8d2ecd195751626592ad1444` |
| `chromadb` que gravou | 1.5.9 |

O `chunk_ids_sha256` é o mesmo que aparece no `backend_fingerprint` de cada
uma das rodadas citadas — é assim que se confirma que este retrato é daquela
base, e não de outra.

## Por que JSON, e não uma cópia da pasta do banco

A pasta `backend/data/chroma/` tem 700 KB e é o formato interno do ChromaDB,
que muda entre versões. Este JSON tem 140 KB, é legível, e traz os vetores
já calculados — então restaurar não depende de baixar o modelo de embedding
nem de a versão do ChromaDB ser a mesma.

## Como restaurar

> **Isto substitui a base da sua máquina.** Faça só se você quiser reproduzir
> uma rodada citada antes de 07/09.

O script é [`scripts/restore_base_snapshot.py`](../../../../scripts/restore_base_snapshot.py).
Ele precisa falar com o ChromaDB direto, e o Compose monta só `./backend` —
por isso o comando leva as outras pastas:

```bash
docker compose stop backend
docker run --rm -v "$PWD/backend:/app" -v "$PWD/scripts:/scripts" -v "$PWD/data:/data" -w /app -e PYTHONPATH=/app tcc-backend:latest python /scripts/restore_base_snapshot.py /data/evaluation/cited/base-2026-09-04-18-chunks/export.json --force
docker compose start backend
```

Parar o backend antes evita dois processos escrevendo no mesmo SQLite. Sem
`--force`, o script **recusa** rodar sobre uma coleção que já tenha conteúdo.
Ao terminar, ele confere sozinho os dois hashes contra os do retrato e falha
se algum divergir. Para confirmar pela API:

```bash
curl localhost:8000/health/fingerprint
```

`chunk_ids_sha256` e `content_sha256` devem bater com a tabela acima.

Este caminho foi testado em 11/09: apagar a coleção e restaurar devolveu os
dois hashes idênticos, e a busca voltou a trazer o protocolo de chocolate em
primeiro lugar para o relato de chocolate.

## O que este retrato mostra sobre a base antiga

Vale olhar o `export.json` antes de usar estes trechos como referência de
qualidade. O primeiro deles começa assim:

> `sinais, uma exposição conhecida deve ser comunicada a um serviço
> veterinário. Sinais observáveis Relatos podem incluir v`

Começa no meio de uma frase e termina no meio de uma palavra. É o corte por
número de caracteres, e é exatamente o defeito que motivou a receita nova do
trilho A. Onze dos 18 trechos são continuações assim.

Ou seja: este retrato preserva uma base **pior** que a atual, e é bom que
seja assim. Ele não é um alvo de qualidade — é a régua que torna os números
de setembro comparáveis entre si.
