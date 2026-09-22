# Benchmark dos componentes do RAG — preservação parcial

**Data:** 22/09/2026

**Branch:** `codex/evaluate-rag-variants`

**HEAD inicial:** `f2b83119e0cb24e4589c0e8f2ddd1f9df1748b57`

**Estado:** resultado principal concluído; demais braços em andamento

## Objetivo

Produzir uma comparação reproduzível entre busca vetorial pura, reordenação
lexical, roteamento por assunto e o pipeline de recuperação atual. O plano
também inclui LLM sem RAG/com RAG, técnicas de consulta e receitas com overlap
0, 16 e 32, mas somente resultados efetivamente concluídos são declarados.

## Ambiente observado

- API, frontend, Mongo e Ollama saudáveis via Docker Compose.
- Modelo: `llama3.2:3b`, Q4_K_M, Ollama `0.33.3`.
- Ambiente sem VRAM registrada; medições absolutas de LLM podem refletir CPU.
- Coleção ativa `veterinary_documents`: **0 chunks**.
- Candidata avaliada, sem ativação:
  `veterinary_documents__20260920T160842289762Z__388f518d`.
- Candidata: **3.481 chunks, 66 documentos, overlap 16, target 96**.
- Modelo de embedding fixado em
  `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, revisão
  `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`.
- Régua: `data/retrieval/cases.csv`, **66 relatos**, 60 tópicos esperados.

Nenhum ponteiro foi alterado e nenhuma coleção foi ativada.

## Testes antes da alteração

- Backend no container: **226 aprovados**.
- Scripts no Python local: **161 aprovados, 26 falharam**.
- As 26 falhas são todas de `test_capturar_fonte.py` por ausência da
  dependência local `trafilatura`; limitação preexistente também registrada
  pelo Ryu.

## Implementação feita

- `backend/app/database/benchmark_retrieval_variants.py`: novo benchmark de
  leitura, com resultado por caso, chunks, tópicos, scores e latência.
- `process_document()` ganhou parâmetros opcionais de target e overlap; os
  defaults existentes permanecem 96/16, preservando compatibilidade.
- `backend/tests/test_benchmark_retrieval_variants.py`: testes das métricas.
- Testes direcionados após a mudança: **36 aprovados**.

## Resultado concluído — ablação da recuperação

| Configuração | Assunto certo em 1º | Assunto certo no top 5 | MRR | Latência mediana |
|---|---:|---:|---:|---:|
| Vetor sozinho | 21,2% | 30,3% | 0,244 | 46,2 ms |
| Vetor + reordenação lexical | 45,5% | 53,0% | 0,479 | 51,6 ms |
| Vetor + roteamento, sem reordenação | 21,2% | 30,3% | 0,244 | 109,6 ms |
| **Pipeline atual (roteamento + reordenação)** | **51,5%** | **66,7%** | **0,570** | **125,4 ms** |

Leitura: a reordenação é responsável pela maior parte do ganho. O roteamento
sozinho amplia candidatos, mas não muda o top 5 porque, sem a reordenação,
eles voltam a ser ordenados apenas pela similaridade vetorial. Combinado com
a reordenação, ele eleva o top 1 em 6,0 pontos e o top 5 em 13,6 pontos sobre
a reordenação isolada.

## Corte de contexto no pipeline atual

| Corte | Casos que receberiam contexto | Casos com assunto correto no contexto |
|---:|---:|---:|
| 0,60 | 48/66 | 31/66 |
| 0,65 | 33/66 | 25/66 |
| 0,70 | 22/66 | 20/66 |
| 0,72 | 18/66 | 16/66 |
| 0,75 | 3/66 | 3/66 |

O corte 0,70 oferece, nesta régua, mais cobertura que 0,72 sem reduzir a
quantidade absoluta de casos corretos: 20 corretos contra 16. Isso ainda não
autoriza mudança de produção, pois falta medir o efeito na classificação da
LLM e os falsos contextos caso a caso.

## Artefato bruto

`data/evaluation/rag_variants/20260922-retrieval-components-overlap16.json`

SHA-256:
`45cb510f247fe495e1bc4b55398a20e3ad3e65699b13da855a0b5fc5902fbc96`

## Experimentos ainda não concluídos

1. A coleção temporária com overlap 0 foi concluída: 3.009 chunks e 67
   documentos. Ela obteve top 1 de 47,0%, top 5 de 68,2% e MRR 0,544 no
   pipeline completo. **Ainda não é uma comparação causal válida com overlap
   16**, porque a candidata histórica tem 66 documentos e o rechunk atual
   selecionou 67. É necessário gerar também overlap 16 e 32 a partir desse
   mesmo conjunto atual de 67 documentos.
2. Overlap 16 equivalente e overlap 32 ainda não foram executados.
3. A comparação da decisão final da LLM — sem RAG, RAG sem corte, RAG com
   corte e pipeline completo — ainda não foi executada nesta rodada.
4. Reescrita, Multi-Query e HyDE ainda precisam ser medidos numa amostra
   estratificada; em CPU, essa etapa é lenta.
5. O conjunto oficial de 150 casos está na branch remota `ryuv3`, ainda não
   integrada à `main`; esta rodada usou os 66 casos já presentes na branch.

## Próxima retomada

1. Rodar overlaps 16 e 32 a partir dos mesmos 67 documentos e só então
   comparar 0/16/32.
3. Criar/rodar o avaliador de classificação diretamente contra a candidata,
   sem ativar o ponteiro.
4. Rodar técnicas de consulta numa amostra estratificada.
5. Reexecutar backend completo, scripts, `pip check`, `compileall` e
   `git diff --check`; gerar evidência final JSON/Markdown.

Artefato parcial do overlap 0:
`data/evaluation/rag_variants/20260922-retrieval-components-overlap0.json`,
SHA-256 `293a1971a8f3aa9bd6b1c141abd1033694798f369ca1b6d5cd330aa02c11871f`.
