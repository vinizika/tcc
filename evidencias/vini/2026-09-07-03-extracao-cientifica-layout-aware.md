# Extração científica orientada a layout

**Data:** 07/09/2026 · **Trilho:** A (Recuperação e Conhecimento) · **Rodada:** 3  
**Commits:** nenhum — implementação ainda não commitada

## O que foi feito

Substituição do caminho principal de extração simples de PDF por uma camada
determinística de blocos e coordenadas. O restante do pipeline da rodada 2 foi
preservado: sidecar opcional, seções, prefixo, tokenizer, chunks 96/16/128,
modelo de embedding, metadados e modo `--inspect`.

O paper *Pathophysiology of heatstroke in dogs – revisited* foi usado como
regressão real. Foram acrescentados 19 testes específicos de layout, ruído,
Unicode, fallback e continuidade entre documentos, além da inspeção dos sete
PDFs sintéticos anteriores.

## Por quê

O `pypdf` entregava texto, mas não a geometria necessária para decidir a ordem
de um paper em duas colunas. O resultado carregava endereço de contato,
captions e artefatos como `/C14C`, `signi ficantly` e `58delirium` antes do
chunking. Alterar tokens ou embedding não resolveria uma perda que já ocorreu
na etapa PDF → texto.

Esta rodada isola somente a extração. Nenhuma consulta, ranking, decisão
clínica, reindexação ou escrita no ChromaDB foi executada.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Adotar `PyMuPDF==1.28.2` como extrator principal | No paper real forneceu blocos, spans e coordenadas estáveis; preservou ligaturas e permitiu reconstruir as colunas com uma dependência única |
| Manter `pypdf` como fallback | PDFs que falhem no parser estruturado continuam processáveis e geram warning explícito |
| Não adotar `pdfplumber` | Embora tenha licença MIT e coordenadas, foi mais lento e suas caixas separaram várias palavras justificadas da mesma linha neste corpus |
| Detectar colunas por página | Abstract, figuras e corpo podem usar layouts diferentes no mesmo documento |
| Usar recorrência + margem para headers/footers | Estar perto da borda, isoladamente, não é evidência suficiente para remover ciência |
| Remover captions apenas por marcador numerado no início | `Figure 1.`/`Table 2:` são fortes; `(Fig. 1)` no corpo precisa permanecer |
| Converter glifo de controle em `°` apenas entre número e C/F | O contexto torna a unidade inequívoca; outros glifos sem `ToUnicode` não são inventados |
| Descartar abertura corrompida somente até a primeira sentença completa | O próprio PDF renderizado começa `Clinical signs` com um fragmento; o pipeline preserva `The median...` sem fabricar a oração ausente |
| Manter `heatstrokeassociated` quando o PDF não fornece espaço | Separar exigiria dicionário ou inferência lexical, proibidos e arriscados |

### Comparação técnica dos extratores

Medição local de três execuções sobre o PDF de 16 páginas; é uma verificação
de engenharia, não um benchmark geral:

| Extrator | Coordenadas/blocos | Ordem pronta para duas colunas | Mediana local | Licença / custo |
|---|---|---|---:|---|
| `pypdf` 6.18.0 | não em uma API de blocos usada pelo projeto | não; fluxo simples trouxe ruído e mistura | 0,361 s | fallback já existente |
| PyMuPDF 1.28.2, sem decodificar imagens | sim, por bloco/linha/span | requer a heurística implementada | **0,233 s** | wheel de 23,9 MB; AGPL-3.0 ou comercial |
| `pdfplumber` 0.11.10 | sim | default alternou colunas e fragmentou linhas justificadas | 1,525 s | MIT, com `pdfminer.six`, Pillow e `pypdfium2` transitivos |

O teste inicial do PyMuPDF com imagens habilitadas custou 0,488 s. Como não há
OCR nem interpretação visual nesta rodada, desabilitar a decodificação de
bitmaps reduziu o custo sem mudar nenhum bloco textual.

A licença do PyMuPDF é uma limitação real: o repositório deve permanecer
compatível com AGPL-3.0 ou obter licença comercial antes de distribuição sob
termos incompatíveis. A vantagem técnica não elimina essa obrigação.

## Resultado esperado

Esperava-se remover o contato e seis captions, manter menções a figuras no
corpo, ordenar esquerda→direita sem alternância, normalizar ligaturas e
temperaturas quando seguras e fazer `Clinical signs` começar em uma unidade
completa. As 16 seções úteis, o limite de 128 tokens, os sete PDFs antigos e
os 18 embeddings da baseline deveriam permanecer preservados.

Também se esperava encontrar casos que não fossem corrigíveis sem inferência;
eles deveriam virar warning/limitação, não substituição específica do paper.

## Resultado obtido

### Paper real, com o tokenizer do modelo

| Medida | Antes (`pypdf`) | Depois (layout) |
|---|---:|---:|
| Páginas extraídas | 16 | 16 |
| Headings detectados | 24 | 23 |
| Seções indexáveis | 16 | 16 |
| Seções editoriais excluídas | 6 | 5 |
| Blocos extraídos | não medido | 244 |
| Blocos removidos | não medido | 25 |
| Páginas multicoluna | não medido | 15 |
| Chunks | 200 | **186** |
| Tokens por chunk | mín. 45 · mediana 90,5 · máx. 128 | mín. 48 · mediana 93 · máx. 119 |
| Chunks acima do target 96 | 31 | 6 |
| Chunks acima de 128 | 0 | **0** |
| Frases com fallback por palavras | 16 | 31 |
| Última página indexada | 11 | 11 |

Os 25 blocos removidos se dividem em **15 headers, seis captions e quatro
blocos editoriais**. Não havia footer ou número de página em bloco isolado;
os números estavam dentro dos headers recorrentes. O extrator recuperou seis
símbolos `°` pelo contexto número+unidade. Nove glifos sem mapa inequívoco,
principalmente marcadores dentro das captions já removidas, foram registrados
em um warning; nenhum U+FFFD chegou aos chunks.

O aumento de 16 para 31 fallbacks de frase não indica estouro: blocos que
antes estavam quebrados agora formam sentenças mais longas e coerentes. Todos
os chunks ficaram abaixo do limite, e apenas seis passaram do target
semântico de 96.

As 16 seções úteis continuam sendo Abstract, fatores predisponentes, Systemic
outlook, disfunção neurológica, dano muscular, hemostasia, AKI, ARDS, dano
cardíaco, trato gastrointestinal, sinais clínicos, Diagnosis, Prognosis,
biomarcadores, preconditioning e Conclusions. `Comprehensive Review`,
`Abbreviations`, disclosure, autores e `References` foram excluídas.

### Exemplos antes/depois

| Caso | Antes | Depois |
|---|---|---|
| Abertura de `Clinical signs` | `58delirium, stupor, coma and seizures).30 The median...` | `The median systolic and diastolic blood pressures upon presentation...` |
| Contato | `Box 12, Rehovot 761001, Israel. In a study...` | bloco `CONTACT` removido; o estudo começa diretamente em `In a study of 54 dogs...` |
| Caption | `Figure 4. Urine heat shock protein...` | bloco removido; a referência científica `(Fig. 4)` permanece |
| Temperatura | `> 41/C14C` | `> 41°C` |
| Ligaturas | `signi ficantly`, `con firmed`, `in flammation` | `significantly`, `confirmed`, `inflammation` |
| Linha justificada fragmentada | `experimentally` / `induced` em linhas artificiais | `experimentally induced models` |
| Fusão sem pista no PDF | `experimentallyinduced`, `heatstrokeassociated` | permanece; não há gap, cmap ou marcador seguro para decidir onde inserir espaço |

O fragmento `58delirium...` também aparece assim na renderização visual do
PDF: não foi causado pela alternância entre colunas e a oração anterior não
existe na camada textual disponível. A implementação usa um critério genérico
— citação numérica colada a minúscula imediatamente após heading, seguida de
uma sentença completa — para descartar só o fragmento. Ela não reconstrói o
que o artigo não oferece.

### Documentos anteriores

Todos foram inspecionados com o tokenizer real e PyMuPDF, sem escrita:

| Documento | Páginas | Colunas detectadas | Blocos removidos | Chunks | Máximo |
|---|---:|---:|---:|---:|---:|
| `convulsoes.pdf` | 1 | 1 | 0 | 10 | 105 |
| `dificuldade_respiratoria.pdf` | 1 | 1 | 0 | 5 | 85 |
| `intoxicacao_cebola_alho.pdf` | 1 | 1 | 0 | 12 | 128 |
| `intoxicacao_chocolate.pdf` | 1 | 1 | 0 | 12 | 98 |
| `obstrucao_urinaria_gatos.pdf` | 1 | 1 | 0 | 12 | 114 |
| `trauma_hemorragia.pdf` | 1 | 1 | 0 | 11 | 119 |
| `vomito_diarreia.pdf` | 1 | 1 | 0 | 11 | 123 |

Os sete ficaram sem warning de extração e sem remoção de bloco. O fallback de
seção única já esperado nesses protocolos foi preservado.

### Verificações automatizadas

| Verificação | Resultado |
|---|---:|
| Testes novos de layout | 19 aprovados |
| Backend completo | 92 aprovados |
| Scripts de avaliação | 48 aprovados |
| Análise sintática de `backend/app` e `backend/tests` | aprovada |
| `git diff --check` | aprovado |
| Chroma SQLite, leitura direta | **18 embeddings** |
| SHA-256 do PDF | `e35a625db133f6cf4785ec1ea3dc7164db5652cddb183e0fecd60c4c901eeda3` — inalterado |
| Build Docker | dependência instalou; validação completa bloqueada na exportação da imagem por falta de espaço/I/O da VM |

Os testes sintéticos cobrem uma coluna, duas colunas, heading em largura
total, header, footer, número de página, contato, Figure, referência `(Fig.)`,
Table, ciência na margem, hífen legítimo, dehyphenation, Unicode, grau,
geometria insuficiente, fallback para `pypdf` e continuação após erro em um
documento. A regressão real cobre métricas e passagens do artigo.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/database/pdf_layout_extraction.py` | novo extrator, classes de blocos, ordem, filtros e métricas |
| `backend/app/database/document_processing.py` | integração do extrator, fallback e descarte conservador de abertura corrompida |
| `backend/app/database/ingest_documents.py` | logs resumidos e detalhados da extração |
| `backend/tests/test_pdf_layout_extraction.py` | 19 testes sintéticos/reais |
| `backend/requirements.txt` | PyMuPDF fixado; `pypdf` mantido como fallback |
| `backend/data/documents/README.md` | fluxo automático, inspeção, limites e licença |
| `docs/ingestao-documental.md` e `docs/README.md` | referência técnica compartilhada e índice |
| `README.md` | contagem da suíte atualizada para 92 |
| `evidencias/vini/*`, `evidencias/backlog.md` | rodada, planejamento, índice e progresso de B-35/B-34 |

O PDF e o sidecar não receberam alteração nesta rodada. O PDF continua
untracked e não foi adicionado ao Git.

## Observações

1. `--inspect` foi executado no host com o tokenizer real e terminou com a
   mensagem explícita de que nenhum registro foi escrito.
2. A imagem Docker resolveu e instalou PyMuPDF 1.28.2 com wheel para
   Python 3.12/Linux. A reconstrução completa expôs o B-34: como `torch` e
   outras dependências não estão fixadas, a resolução atual baixou vários
   gigabytes de CUDA e levou o disco a 99%. A exportação foi interrompida para
   evitar esgotar a máquina. A VM registrou erros de I/O em EXT4 e o Docker
   Desktop passou a responder `unable to start`; um reinício normal não o
   recuperou. Nenhum reset, `prune`, remoção de imagem ou volume foi feito.
   Portanto, o `--inspect` dentro do container não pôde ser concluído nesta
   rodada; o mesmo comando passou no host. Isso não é incompatibilidade do
   PyMuPDF, cuja instalação no estágio Linux terminou com sucesso.
3. O banco foi verificado diretamente em modo somente leitura após as
   inspeções e ainda contém 18 embeddings.
4. Nenhum OCR, LLM, tradução, resumo ou reconstrução de tabela foi introduzido.

## Deixado para depois

**Fusões sem evidência gráfica.** `experimentallyinduced` e
`heatstrokeassociated` permanecem. Voltam ao escopo apenas se houver uma regra
estrutural genérica; usar palavras conhecidas deste paper mascararia a perda.
O progresso está no [B-35](../backlog.md#b-35).

**Reprodutibilidade da imagem.** Fixar a árvore de dependências e evitar CUDA
desnecessário na imagem padrão pertence ao [B-34](../backlog.md#b-34), não à
extração de PDF.

**OCR e tabelas complexas.** Permanecem explicitamente fora desta entrega.

**Reindexação e retrieval.** O paper não foi inserido. A base de 18 chunks
continua sendo a baseline até existir a régua de recuperação.

## Próximo passo

Construir a régua de recuperação do trilho A e congelar a medição dos 18
chunks atuais. Só depois autorizar uma rodada separada de reindexação para
medir o efeito conjunto da preparação das rodadas 2 e 3.
