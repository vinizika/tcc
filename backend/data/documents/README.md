# Fontes veterinárias do RAG

Esta pasta contém as fontes originais usadas pela recuperação. O ingestor
aceita arquivos `.pdf` e `.txt`; o documento original não deve ser editado
manualmente para facilitar a indexação. Captura não significa curadoria, e
nenhuma automação concede aprovação clínica ou direito de redistribuição.

## Adicionando uma fonte

1. Coloque o PDF ou TXT nesta pasta.
2. Crie, preferencialmente, um JSON de mesmo nome: `fonte.pdf` usa
   `fonte.json`.
3. Inspecione seções e chunks antes de alterar a coleção.
4. Só então execute a ingestão.

Sem sidecar, o documento só pode aparecer nos perfis permissivos e gera
warning. O perfil `curated` o recusa antes de abrir o Chroma.

Adicionar um paper novo não deve exigir nenhuma alteração no código Python.
O sidecar é curadoria opcional, não um perfil de parser por documento.

Campos principais suportados:

```json
{
  "title": "Título da fonte",
  "source": "Instituição ou periódico",
  "document_type": "peer_reviewed_review",
  "validation_status": "published_not_locally_validated",
  "species": "dog",
  "topic": "assunto_controlado",
  "authors": "Autor A; Autor B",
  "year": 2026,
  "doi": "10.xxxx/exemplo",
  "journal": "Periódico",
  "language": "en",
  "source_url": "https://doi.org/10.xxxx/exemplo",
  "ingestion_scope": "experimental_only",
  "rights": {
    "status": "pending",
    "redistribution_allowed": false
  },
  "indexing": {
    "retrieval_anchors": ["chocolate", "cacau", "cocoa"],
    "include_sections": [],
    "exclude_sections": ["Supplementary material"],
    "exclude_pages": []
  }
}
```

- `include_sections` ausente ou vazio mantém todas as seções válidas.
- `include_sections` preenchido funciona como whitelist daquele documento.
- `exclude_sections` complementa as exclusões automáticas, como References,
  Bibliography, conflitos, financiamento, contribuições e agradecimentos.
- `exclude_pages` é um fallback para páginas editoriais ou PDFs cuja estrutura
  não possa ser interpretada. A numeração começa em 1 para PDF; TXT usa 0.
- `retrieval_anchors` restringe fontes dependentes de uma exposição ou contexto
  explícito. Ao menos um termo precisa aparecer no relato para a fonte ser
  elegível; isso evita recuperar intoxicação apenas por sintomas genéricos.
- Nomes de seção são comparados sem diferenciar maiúsculas de minúsculas.
- Uma seção configurada e não encontrada produz warning para revisão.

Publicação revisada por pares e validação local são coisas diferentes. Use,
por exemplo, `peer_reviewed_review` com
`published_not_locally_validated` até a avaliação pela especialista do projeto.

O vocabulário canônico de `species` é `dog`, `cat` e `dog_and_cat`. O perfil
curado também exige `ingestion_scope: curated`, aprovação especialista
identificada e datada, direitos compatíveis, hash e URL da fonte, e `topic`
existente no mapa. PDFs exigem `extraction_reviewed: true`.

## O que o pipeline faz com PDFs

O fluxo padrão usa PyMuPDF para obter blocos com coordenadas e, página a
página:

1. normaliza Unicode e reúne fragmentos da mesma linha pela posição vertical;
2. identifica uma ou duas regiões horizontais dominantes;
3. ordena toda a coluna esquerda antes da direita, respeitando títulos ou
   outros blocos que cruzem a largura da página;
4. remove cabeçalhos e rodapés somente quando posição e recorrência dão
   evidência suficiente;
5. remove números de página isolados, blocos editoriais de contato e legendas
   que começam por `Figure`, `Fig.` ou `Table` com numeração;
6. preserva referências no corpo, como `(Fig. 1)` e `as shown in Table 2`;
7. detecta e filtra seções e cria chunks por tokens com página e seção.

As heurísticas são genéricas: não consultam nome do arquivo, autores, DOI ou
números fixos de página. Se o extrator estruturado falhar, o pipeline registra
um warning e tenta o extrator simples `pypdf`. Se apenas a geometria de uma
página for insuficiente, mantém a ordem original dos blocos dessa página.

O modo `--inspect` informa o extrator, blocos extraídos/removidos, páginas
multicoluna, headers, footers, captions, blocos editoriais e warnings de
Unicode/layout antes de listar as seções e os chunks.

### Limitações conhecidas

- Não há OCR. Um PDF escaneado, sem camada textual, precisa ser convertido
  fora deste pipeline ou aguardará uma entrega futura de OCR.
- Tabelas não são reconstruídas agressivamente. Conteúdo textual aproveitável
  pode permanecer; tabelas ambíguas exigem inspeção e curadoria.
- Layouts extremamente incomuns ou glifos sem mapa Unicode podem exigir
  `exclude_pages`/seções no sidecar. O pipeline não inventa caracteres ou
  conteúdo clínico ausente.
- PyMuPDF 1.28.2 usa licença AGPL-3.0 ou comercial. Antes de distribuir o
  sistema sob termos incompatíveis, o time deve revisar essa escolha; `pypdf`
  continua presente somente como fallback.
- Todo paper importante deve passar por `--inspect` antes da ingestão. A
  automação reduz trabalho manual, mas não substitui curadoria da fonte.

## Inspeção sem escrever no ChromaDB

Dentro do container, para um documento:

```bash
docker compose exec backend python -m app.database.ingest_documents \
  --inspect --file pathophysiology_heatstroke_dogs_2017.pdf
```

Para inspecionar todos, omita `--file`. `--dry-run` é um alias de `--inspect`.
O relatório mostra seções detectadas/incluídas/excluídas, páginas, quantidade
e tamanho em tokens dos chunks, métricas da extração e um preview de cada
trecho. Esse modo não abre nem altera a coleção.

## Ingestão versionada

Criar uma candidata sem trocar a coleção ativa:

```bash
docker compose exec backend python -m app.database.ingest_documents \
  --profile curated --stage-only
```

Ativar somente depois de revisar os artefatos:

```bash
docker compose exec backend python -m app.database.ingest_documents \
  --profile curated --activate
```

`--reset` foi removido porque apagava o estado ativo. Cada candidata tem
manifesto obrigatório; contagem e hashes são conferidos antes da ativação.
Use `--list-collections` e `--rollback` para inventário e retorno. Os perfis,
a receita fixa e o ponteiro ativo estão em
[`docs/estado-atual.md`](../../../docs/estado-atual.md).

Antes de fazer commit de qualquer PDF em repositório público, verifique os
direitos autorais e a licença de redistribuição. A possibilidade técnica de
extrair e indexar uma fonte não concede permissão para redistribuí-la.
