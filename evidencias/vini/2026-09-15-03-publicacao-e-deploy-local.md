# Publicação da branch e deploy local

**Data:** 15/09/2026

**Branch:** `codex/lote-01-intoxicacoes`

**Remoto:** `origin` — `https://github.com/vinizika/tcc.git`

## Resultado

O trabalho acumulado foi separado em commits lógicos, enviado para a branch
remota e implantado no ambiente local definido oficialmente pelo repositório.
Não existe configuração de hospedagem externa neste checkout: o workflow do
GitHub Actions executa testes em pull requests e em pushes para `main`, mas
não publica backend ou frontend em Render, Railway, Vercel ou serviço similar.

Commits publicados:

| Commit | Conteúdo |
|---|---|
| `744d220` | Fontes, artigos, casos e suporte ao lote experimental de intoxicações |
| `1fc90b8` | Protótipo de clínicas, dashboard, documentação e testes do mock |
| `5f32e39` | Correção do travamento em `/health/fingerprint` e testes |
| `02c0fef` | Snapshot completo do ChromaDB experimental |

Branch publicada:
`https://github.com/vinizika/tcc/tree/codex/lote-01-intoxicacoes`.

O GitHub ofereceu a criação de pull request em:
`https://github.com/vinizika/tcc/pull/new/codex/lote-01-intoxicacoes`.
Nenhum PR ou merge em `main` foi feito automaticamente.

## Artigos e ChromaDB compartilhados

Por solicitação explícita do responsável do projeto, os PDFs, texto extraído,
sidecars e arquivos binários do ChromaDB foram mantidos no Git. O snapshot foi
capturado com o backend parado para evitar copiar o SQLite enquanto estivesse
aberto e foi publicado no commit `02c0fef`.

O diretório versionado é `backend/chroma_db/` e contém:

- `chroma.sqlite3`;
- índice HNSW (`data_level0.bin`, `header.bin`, `length.bin` e
  `link_lists.bin`);
- manifesto da candidata;
- recibo da ingestão.

Estado preservado no snapshot:

- coleção candidata:
  `veterinary_documents__20260914T154159080566Z__9106a62e`;
- perfil: `experimental`;
- documentos: 3;
- chunks: 24;
- integridade do manifesto: validada;
- ponteiro ativo: inexistente;
- coleção legada usada pela API: `veterinary_documents`, com 0 chunks.

A candidata não foi ativada porque a encontrabilidade top-5 medida foi 2/3,
ou 66,7%, abaixo da porta de 70%. Versionar o banco garante que a equipe
receba o mesmo snapshot, mas não altera essa decisão registrada.

Depois que o backend foi religado, o próprio Chroma alterou novamente
`chroma.sqlite3` apenas por abrir o armazenamento. Por isso, o Git contém o
snapshot consistente capturado com o backend parado, enquanto a cópia de
trabalho volta a aparecer modificada durante a execução normal. Essa mutação
automática — além de conflitos binários difíceis de mesclar — era a razão
técnica para inicialmente manter bancos locais fora do versionamento. O
snapshot foi publicado mesmo assim por decisão explícita do responsável do
projeto, para que toda a equipe parta dos mesmos bytes.

## Deploy local

Comando executado:

```bash
docker compose up -d --build
```

Backend e frontend foram reconstruídos. Os containers de backend, frontend e
Ollama foram recriados; MongoDB permaneceu em execução. Os volumes nomeados do
MongoDB e do Ollama foram preservados.

Após capturar o snapshot do Chroma, o backend foi religado e ficou saudável.

| Serviço | Verificação final |
|---|---|
| Backend | `http://localhost:8000/health/` — HTTP 200 em 0,004 s |
| Fingerprint | `http://localhost:8000/health/fingerprint` — HTTP 200 em 0,132 s |
| Frontend real | `http://localhost:8501` — HTTP 200 em 0,014 s |
| Mock independente | `http://localhost:8502` — HTTP 200 em 0,013 s |

## Verificações já concluídas antes da publicação

- backend no host: 203 testes aprovados;
- backend na imagem reconstruída: 203 testes aprovados;
- mock e scripts: 196 testes aprovados;
- `compileall`: código 0;
- `git diff --check`: código 0;
- chamadas repetidas ao fingerprint sem travamento.

Não foram enviados `.env`, credenciais, dados pessoais reais, cache Python ou
ambientes virtuais.
