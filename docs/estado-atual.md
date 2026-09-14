# Estado atual da ingestão vetorial

Este é o ponto de entrada operacional da base. A ingestão é versionada e
transacional: preparar uma candidata nunca altera a coleção ativa; a ativação
é explícita, só ocorre depois da validação do manifesto, contagem e hashes, e
mantém a coleção anterior disponível para rollback.

## Identidade da receita

- modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`;
- revisão de modelo e tokenizer:
  `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`;
- receita reconstruída: `vector-ingestion-recovery-v1`;
- o hash efetivo da receita é calculado por
  `backend/app/database/embedding_config.py`.

A serialização literal da receita perdida não pôde ser recuperada. Por isso a
reconstrução usa uma identidade nova e não tenta fabricar o hash histórico.

## Perfis

| Perfil | Finalidade | Regra de entrada |
|---|---|---|
| `curated` | base apta a sustentar avaliação | exige aprovação de especialista, direitos, procedência, espécie canônica, tópico do mapa e revisão de extração para PDF |
| `experimental` | inspeção de fontes ainda não aprovadas | aceita candidatas com avisos; nunca as transforma em curadas |
| `legacy_rechunk` | reproduzir o corpus legado com a receita nova | seleciona somente os protocolos sintéticos legados |

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
