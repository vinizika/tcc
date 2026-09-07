# Ingestão científica com seções e chunks por tokens

**Data:** 07/09/2026 · **Trilho:** A (Recuperação e Conhecimento) · **Rodada:** 2  
**Commits:** nenhum — implementação ainda não commitada

## O que foi feito

Substituição do chunking de 1200 caracteres por um pipeline determinístico
orientado a seções, frases e tokens. O nome do modelo foi centralizado entre
o ChromaDB e o tokenizer, os sidecars passaram a controlar inclusão de
seções, exclusões e páginas, e foi criado o modo `--inspect` sem escrita no
banco.

O PDF real *Pathophysiology of heatstroke in dogs – revisited* foi usado na
implementação e nos testes. Seu sidecar registra procedência científica sem
confundir publicação revisada por pares com validação local.

## Por quê

O recorte anterior cortava texto por caracteres, perdia estrutura e podia
vetorizar referências e conteúdo editorial. Isso não respeitava a janela real
do embedder nem produzia trechos explicáveis para a régua de recuperação.

Esta rodada altera somente a variável de ingestão/chunking. O modelo de
embedding, a busca, o `top_k`, o reranking e a classificação não mudaram.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Usar o identificador canônico `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` em uma constante compartilhada | O apelido curto funcionava no Chroma, mas não no `AutoTokenizer`; o modelo continua o mesmo |
| Limite seguro de 128 tokens, target 96 e overlap 16 | O tokenizer anuncia 512, mas a configuração publicada do SentenceTransformer limita as sequências a 128; prefixo e tokens especiais entram na contagem |
| Preservar frase mesmo quando ela passa de 96, desde que não ultrapasse 128 | 96 é target experimental, não uma fronteira semântica; frases acima de 128 usam fallback por palavras |
| Tratar References/Bibliography como seções terminais | PMIDs, DOIs e siglas em maiúsculas dentro das referências não podem ser confundidos com novos headings |
| Excluir a página 1 pelo sidecar deste paper | Ela é uma capa editorial da publicadora; o artigo começa na página 2 |
| Não reindexar o ChromaDB nesta rodada | Primeiro era necessário inspecionar e testar os recortes; a comparação de retrieval exige a régua do trilho A |

## Resultado esperado

Esperava-se que o artigo real tivesse capa e seções editoriais removidas,
`References` excluída até o fim, seções clínicas preservadas e nenhum chunk
acima do limite efetivo de 128 tokens. Os sete protocolos anteriores deveriam
continuar processáveis sem sidecars novos ou edição dos PDFs.

## Resultado obtido

### Paper real, com tokenizer do modelo

| Medida | Resultado |
|---|---:|
| Páginas extraídas | 16 |
| Headings detectados | 24 |
| Seções com conteúdo indexável | 16 |
| Seções explicitamente excluídas | 6 |
| Chunks | 200 |
| Tokens por chunk | mínimo 45 · mediana 90,5 · máximo 128 |
| Chunks acima do target de 96 | 31 |
| Chunks acima do limite seguro de 128 | **0** |
| Frases longas com fallback por palavras | 16 |
| Última página com conteúdo indexado | 11 |

Foram preservadas `Abstract`, fatores predisponentes, sinais clínicos,
`Diagnosis`, `Prognosis`, `Conclusions` e as demais seções científicas úteis.
Foram excluídas capa editorial, `Comprehensive Review`, histórico do artigo,
abreviações, declaração de conflitos, autores e `References`. As referências
das páginas 12 a 16 não produziram chunks.

Os sete PDFs sintéticos anteriores também passaram pelo modo de inspeção. O
fallback de seção única preservou o documento cuja extração separa o título
em palavras maiúsculas isoladas.

### Verificações automatizadas

| Verificação | Resultado |
|---|---:|
| Backend | 73 testes aprovados |
| Scripts de avaliação | 48 testes aprovados |
| Análise sintática de `backend/app` e `backend/tests` | aprovada |
| `git diff --check` | aprovado |

Os testes novos cobrem hifenização, hífen legítimo, seções automáticas e
configuradas, fallback, limites, overlap, páginas/metadados, defaults neutros,
warnings, conteúdo vazio, ausência de acesso ao Chroma no modo de inspeção e
o PDF real de 16 páginas.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/database/embedding_config.py` | configuração única do MiniLM e dos limites |
| `backend/app/database/document_processing.py` | limpeza, parsing de seções, filtros e chunking por tokens |
| `backend/app/database/ingest_documents.py` | orquestração, logs e CLI `--inspect`/`--file` |
| `backend/app/database/chroma_client.py` | consumo do nome centralizado do mesmo modelo |
| `backend/data/documents/pathophysiology_heatstroke_dogs_2017.json` | metadados e regras do paper real |
| `backend/data/documents/README.md` | procedimento para adicionar e inspecionar fontes |
| `backend/tests/test_document_processing.py` | cobertura do pipeline e do PDF real |
| `backend/requirements.txt` | dependências explícitas de tokenizer e fontes CFF |
| `README.md` | contagem atual da suíte do backend |
| `evidencias/backlog.md` | progresso do B-31 e novo B-35 |

O PDF foi fornecido pelo usuário e não foi modificado. Seu SHA-256 observado é
`e35a625db133f6cf4785ec1ea3dc7164db5652cddb183e0fecd60c4c901eeda3`.

## Observações

1. O tokenizer do modelo informa `model_max_length=512`, enquanto a camada
   SentenceTransformer usada para embeddings declara `max_seq_length=128`.
   O código adota o menor limite confiável: 128.
2. O prefixo `Document title` + `Section`, bem como tokens especiais, participa
   da contagem; os 96 tokens não são reservados apenas ao corpo.
3. O algoritmo e, consequentemente, os IDs/chunks mudam. A migração do banco
   exige `--reset`, depois de congelar a medição anterior.
4. O modo `--inspect` importa o tokenizer, mas não importa o cliente Chroma,
   não abre a coleção e não faz delete/upsert.
5. A ingestão continua com delete antes de upsert; a correção transacional
   permanece separada no B-30.

## Deixado para depois

**Reindexação e métricas de retrieval.** Não executadas para não alterar a
base ativa antes da régua Precision@1/MRR/Recall@5. O Chroma local permanece
com os 18 chunks anteriores.

**Artefatos do extrator.** Apesar da dehyphenation, o `pypdf` ainda entrega
trechos como `58delirium`, `/C14C` e espaços residuais de ligaturas no paper
multicoluna. Isso foi registrado como [B-35](../backlog.md#b-35), sem aplicar
correção clínica inventada.

**Parsing acadêmico universal.** O detector usa headings comuns, headings do
sidecar e fallback seguro. Layouts muito diferentes ainda exigem inspeção e,
quando necessário, override determinístico por documento.

## Próximo passo

Construir a régua de recuperação do trilho A e congelar a linha de base dos
18 chunks atuais. Depois, executar a reindexação com `--reset` e comparar a
base nova na mesma régua, isolando o efeito desta mudança.
