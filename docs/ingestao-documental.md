# Ingestão de documentos científicos

Referência técnica para quem for evoluir o corpus do trilho A. O procedimento
de uso e o formato do sidecar ficam em
[`backend/data/documents/README.md`](../backend/data/documents/README.md); este
documento explica as fronteiras da implementação.

## Fluxo e responsabilidades

```text
PDF/TXT + sidecar opcional
        ↓
extração de blocos e coordenadas por página
        ↓
ordem de leitura + remoção conservadora de ruído
        ↓
detecção e filtragem de seções
        ↓
chunks de 96 tokens, overlap 16, limite 128
        ↓
embedding MiniLM multilíngue
        ↓
ChromaDB
```

| Arquivo | Responsabilidade |
|---|---|
| `backend/app/database/pdf_layout_extraction.py` | Extrair blocos de PDF, normalizar glifos seguros, detectar colunas, ordenar a página e remover ruído de layout |
| `backend/app/database/document_processing.py` | Carregar sidecar, aplicar fallback, detectar/filtrar seções e produzir chunks por tokens |
| `backend/app/database/ingest_documents.py` | CLI, inspeção, logs e escrita explícita no ChromaDB |
| `backend/app/database/embedding_config.py` | Fonte única do modelo e dos limites de chunking |

O extrator de layout não conhece títulos, autores, periódicos, arquivos ou
páginas específicas. O paper de heatstroke é uma regressão real, não uma
configuração do parser. Casos excepcionais devem preferir o sidecar; uma regra
Python nova só é aceitável quando for genérica e vier acompanhada de blocos
sintéticos que comprovem o comportamento.

## Decisão do extrator

O PyMuPDF 1.28.2 é o caminho principal. No paper real ele forneceu blocos
nativos com coordenadas, preservou melhor ligaturas e foi mais rápido que
`pypdf` e `pdfplumber`. `pdfplumber` foi avaliado, mas suas caixas dividiram
linhas justificadas do corpus em fragmentos e exigiriam mais reconstrução. O
`pypdf` permanece como fallback simples porque não fornece uma representação
de layout suficiente para ordenar papers multicoluna.

A escolha tem um custo: PyMuPDF é distribuído sob AGPL-3.0 ou licença
comercial. O repositório precisa continuar compatível com esses termos ou
reavaliar a dependência antes de uma distribuição incompatível. Não foi
adicionada uma segunda biblioteca de layout.

## Heurísticas e proteções

- A detecção de colunas usa distribuição horizontal, largura e centros dos
  blocos por página. Não assume que todo o documento tenha o mesmo layout.
- Blocos que atravessam a faixa central separam bandas; isso permite título ou
  heading de largura total seguido por duas colunas.
- Cabeçalho/rodapé exige proximidade da margem e recorrência em pelo menos três
  páginas e 20% do documento. Texto científico perto da margem não basta.
- Caption exige `Figure`, `Fig.` ou `Table`, número e pontuação no início do
  bloco. Menções no corpo são mantidas.
- Contato exige marcadores fortes (`CONTACT`, `ORCID`, `corresponding author`)
  ou e-mail junto de indício de afiliação na margem.
- Um caractere de controle entre número e unidade C/F pode ser normalizado
  para `°`; os demais glifos sem mapa inequívoco permanecem explícitos como
  U+FFFD e geram warning.
- Fragmentos de uma mesma linha que se sobrepõem verticalmente são reunidos
  por geometria. Não há dicionário veterinário nem correção lexical inventada.
- Se o PyMuPDF falhar, o documento tenta `pypdf`. Se somente as coordenadas
  forem inválidas, a página preserva a sequência original dos blocos.

Não há OCR, interpretação de imagens, reconstrução agressiva de tabelas, LLM
de parsing, tradução ou resumo nesta camada.

## Como alterar com segurança

1. Adicione primeiro um teste sintético de blocos/coordenadas para a regra.
2. Rode os testes de `backend/tests/test_pdf_layout_extraction.py` e a suíte
   completa do backend.
3. Use `--inspect --file` no documento que motivou a mudança e depois
   `--inspect` nos documentos anteriores.
4. Confira limites de tokens, seções, warnings e exemplos antes/depois.
5. Registre a rodada em `evidencias/<nome>/`, atualize o planejamento e o
   backlog quando houver limitação pendente.
6. Reindexe somente em uma rodada experimental autorizada e com a linha de
   base congelada. `--inspect` nunca deve abrir ou escrever no ChromaDB.

Mudanças de modelo, chunking, busca, ranking ou contrato pertencem a rodadas
separadas para que seus efeitos continuem mensuráveis.
