# Correção do travamento em `/health/fingerprint`

**Data:** 15/09/2026

**Branch:** `codex/lote-01-intoxicacoes`

**HEAD inicial:** `ad9b55ff5754370a60ab63bc78fcd8773de77359`

**HEAD sincronizado:** `784875098a109d48ce03d624450d239fc7443367`

**Origem do relato:** Julian observou duas chamadas que não retornaram e
suspeitou de retenção de lock no arquivo do ChromaDB após o endurecimento da
ingestão vetorial.

## Resultado

O branch local foi atualizado por fast-forward até o mesmo commit de
`origin/main`, sem conflitos e sem sobrescrever as alterações locais já
existentes. O endpoint foi corrigido, o backend foi reconstruído com as
dependências do HEAD atual e o problema não voltou a ocorrer nas chamadas
repetidas em `localhost`.

Não foi encontrado indício de que a causa primária fosse um lock de arquivo do
ChromaDB. A reprodução mostrou o processo parado no carregamento do
`SentenceTransformerEmbeddingFunction`, enquanto o Hugging Face repetia
consultas de metadados com backoff. O fingerprint só precisava ler IDs,
documentos e metadados, mas usava `ChromaDBClient.get_collection()`, caminho
destinado a consultas vetoriais e que inicializava o modelo de embeddings.

Além da espera de rede, o caminho anterior validava a coleção inteira dentro
de `get_collection()` e depois fazia outra leitura integral no serviço de
fingerprint. Isso ampliava desnecessariamente o tempo de acesso ao Chroma e
podia ocupar o worker que atendia a rota, fazendo outras consultas parecerem
bloqueadas.

## Alterações implementadas

- `ChromaDBClient._get_strict_collection` passou a permitir abertura sem
  função de embeddings.
- Foi criado `get_collection_for_inspection`, que usa
  `embedding_function=None`, não cria coleção e não consulta o Hugging Face.
- Coleções versionadas continuam exigindo manifesto com identidade dos
  chunks e hash igual ao ponteiro ativo.
- A coleção legada pode ser inspecionada sem inventar manifesto ou criar uma
  nova coleção.
- O fingerprint passou a fazer uma única leitura da coleção e compara nessa
  leitura a contagem, o hash dos IDs e o hash do conteúdo com o manifesto.
- Foram adicionados testes para impedir regressão ao caminho que carrega o
  embedding e para confirmar que a inspeção não cria coleção.

Arquivos alterados nesta correção:

- `backend/app/database/chroma_client.py`;
- `backend/app/services/fingerprint_service.py`;
- `backend/tests/test_api_health.py`;
- `backend/tests/test_chroma_ingestion_integration.py`.

## Verificações executadas

| Verificação | Resultado |
|---|---|
| Testes focados de health e Chroma real | **26 passaram** |
| Suíte completa do backend no ambiente local | **203 passaram** |
| Suíte completa do backend na imagem reconstruída | **203 passaram** |
| Testes do mock e scripts | **196 passaram** |
| `python -m compileall -q backend frontend mock scripts` | código 0 |
| `git diff --check` | código 0 |
| Inspeção direta de `_base_vetorial()` | 0,559 s, sem erro |
| Primeira chamada após rebuild a `/health/fingerprint` | HTTP 200 em 0,211 s |
| Segunda chamada após rebuild a `/health/fingerprint` | HTTP 200 em 0,027 s |
| Chamada subsequente a `/health/` | HTTP 200 em 0,004 s |
| Frontend real em `localhost:8501` | HTTP 200 |
| Mock independente em `localhost:8502` | HTTP 200 |

O backend foi reconstruído porque o HEAD atualizado elevou `supabase` de
2.15.0 para 2.31.0. O Compose recriou os containers do backend e do MongoDB;
o volume nomeado `mongo_data` foi preservado. Frontend e Ollama permaneceram
ativos.

## Estado entregue

- Backend real: <http://localhost:8000>.
- Fingerprint: <http://localhost:8000/health/fingerprint>.
- Frontend real: <http://localhost:8501>.
- Mock de demonstração: <http://localhost:8502>.
- Base sincronizada usada na correção: `origin/main` em
  `784875098a109d48ce03d624450d239fc7443367`.
- Correção publicada posteriormente no commit `5f32e39` da branch
  `origin/codex/lote-01-intoxicacoes`.
- Nenhum PR ou merge em `main` foi realizado.
- Alterações locais anteriores do mock, curadoria e scripts foram mantidas.

## Limitação

A correção elimina a inicialização indevida do modelo no fingerprint e reduz
a janela de acesso ao Chroma. Ela não transforma o fingerprint em uma prova
formal da ausência de locks internos do SQLite/Chroma sob qualquer carga
concorrente. Para esse nível de garantia ainda seria necessário um teste de
carga com múltiplos workers e uma coleção ativa representativa.
