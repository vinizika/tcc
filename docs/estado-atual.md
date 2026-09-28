# Estado atual da ingestão vetorial

Este é o ponto de entrada operacional da base. A ingestão é versionada e
transacional: preparar uma candidata nunca altera a coleção ativa; a ativação
é explícita, só ocorre depois da validação do manifesto, contagem e hashes, e
mantém a coleção anterior disponível para rollback.

## A coleção ativa (desde 25/09)

As **61 fichas de triagem** no bge-m3
(`veterinary_documents__20260925T061349534255Z__280baf13`, perfil `fichas`),
com o ponteiro ativo **versionado** em `backend/chroma_db/active_collection.json`
e `CHROMA_PATH = "chroma_db"`: um clone limpo sobe com ela, sem passo manual
([rodada 24 do João](../evidencias/joao/2026-09-25-25-busca-por-fichas-com-bge-m3.md)).
A anterior no ponteiro é a acadêmica `…388f518d` (3.481 trechos, MiniLM), o
braço "hoje" da ablação: `--rollback` volta para ela, e o embedding certo é
escolhido pelo manifesto.

Abrir o Chroma versionado altera o `chroma.sqlite3` sem mudar o conteúdo das
coleções ([B-73](../evidencias/backlog.md#b-73)): não commite esse arquivo sem
querer.

## Identidade das receitas

Cada coleção guarda no manifesto a receita que a construiu (`recipe_key`), e
o cliente consulta com o modelo dela. As receitas estão em
`backend/app/database/embedding_config.py`:

| Receita | Modelo e revisão | Dimensões · limite | Recorte | Perfis |
|---|---|---|---|---|
| `minilm-academic-v1` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` @ `e8f8c211…` | 384 · 128 tokens | trechos de 96 tokens, sobreposição 16 (`vector-ingestion-recovery-v1`, hash `1a93e1e7…`) | `curated`, `experimental`, `legacy_rechunk` |
| `bge-m3-fichas-v1` | `BAAI/bge-m3` @ `5617a9f6…` | 1024 · 512 tokens | nenhum: uma ficha, um vetor | `fichas` |

Manifestos anteriores a 25/09 não têm `recipe_key`: resolvem pelo par modelo +
revisão. A serialização da receita acadêmica não mudou com as receitas (hash
`1a93e1e7…`, travado em teste).

A serialização literal da receita perdida não pôde ser recuperada. Por isso a
reconstrução usa uma identidade nova e não tenta fabricar o hash histórico.

## Perfis

| Perfil | Finalidade | Regra de entrada |
|---|---|---|
| `curated` | base apta a sustentar avaliação | exige aprovação de especialista, direitos, procedência, espécie canônica, tópico do mapa e revisão de extração para PDF |
| `experimental` | inspeção de fontes ainda não aprovadas | aceita candidatas com avisos; nunca as transforma em curadas |
| `legacy_rechunk` | reproduzir o corpus legado com a receita nova | seleciona somente os protocolos sintéticos legados |
| `fichas` | as 61 fichas de triagem (desde 25/09) | lê `backend/data/fichas.json` (gerado por `scripts/sync_fichas.py`); o texto de busca vira vetor, a ficha de leitura vai ao metadado `body`; recusa hash que não confere e texto acima de 512 tokens |

Se não houver documento elegível no perfil `curated`, o comando falha antes
de importar o Chroma, criar diretório ou carregar tokenizer.

## Procedimento seguro

```bash
# somente inspeciona; não abre o Chroma
cd backend
python -m app.database.ingest_documents --inspect

# cria uma candidata e para
python -m app.database.ingest_documents --profile experimental --stage-only

# ativação explícita, após revisão do manifesto/recibo
python -m app.database.ingest_documents --profile curated --activate

# as fichas de triagem (bge-m3), a coleção padrão desde 25/09
python -m app.database.ingest_documents --profile fichas --activate

# inventário e rollback
python -m app.database.ingest_documents --list-collections
python -m app.database.ingest_documents --rollback
```

O ponteiro ativo fica em `CHROMA_PATH/active_collection.json`. Quando ele
existe, a leitura usa `get_collection`: um ponteiro ausente ou inválido é erro
e jamais cria uma coleção vazia. Toda coleção versionada exige manifesto.

O texto persistido para embedding inclui título e seção. O metadado `body`
guarda o corpo limpo, que é o único texto devolvido ao prompt. Coleções
legadas sem `body` continuam legíveis.

## Evidência e consenso

Cada rodada grava manifesto, recibo e fingerprint. O fingerprint contém
inventário por tópico e espécie, hashes de IDs/conteúdo/fontes, revisão do
embedder e hash da receita. Antes de comparar máquinas, use:

```bash
python scripts/verify_vector_consensus.py fingerprint-a.json fingerprint-b.json
```

O ciclo completo é apenas planejado por padrão. A execução e a ativação
precisam ser pedidas separadamente:

```bash
python scripts/run_ingestion_cycle.py --name lote-1 --profile curated
python scripts/run_ingestion_cycle.py --name lote-1 --profile curated --execute --activate
```

Nenhum desses comandos aprova conteúdo clínico. Captura, aprovação
especialista e autorização de redistribuição continuam etapas distintas.
