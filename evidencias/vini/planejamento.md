# Planejamento do trilho A — Recuperação e Conhecimento

Roteiro do trilho responsável pela base documental, ingestão, embeddings,
busca vetorial e re-ranking. O histórico detalhado está nas
[rodadas](README.md); o escopo e as fronteiras estão em
[`docs/divisao-de-trabalho.md`](../../docs/divisao-de-trabalho.md).

---

## Objetivo do trilho

Dado um relato de tutor, recuperar nas primeiras posições os trechos do
protocolo correto — ou não fornecer contexto quando a base não cobre o assunto
— com resultado medido por uma régua própria de recuperação.

Números de referência atuais, medidos pelo runner do B2 sobre 98 relatos:

| Configuração | Acurácia balanceada | Falsos não urgentes |
|---|---:|---:|
| LLM sem RAG | **0,893** | **8 de 71** |
| RAG direto, 3 trechos | 0,763 | 30 de 71 |
| Pipeline completo, 05/09 | 0,704 | 40 de 71 |

Esses números medem o sistema inteiro, não substituem a régua do trilho A.

## Onde estou

| # | Entrega | Situação | O que entregou / entrega |
|---|---|---|---|
| 0 | Implementação inicial de ingestão e busca | ✅ anterior a esta pasta | PDFs/TXTs extraídos, divididos e indexados no ChromaDB com embeddings multilíngues |
| 1 | Auditoria do estado do trilho | ✅ 07/09 | Base local confirmada; achados antigos e novos classificados; riscos de ingestão registrados |
| 2 | **Régua de recuperação** | ✅ entregue pelo B2 | Casos fixos, fingerprint por rodada, Precision@1, Recall@5, MRR e compare conservador |
| 3 | Preparação, extração e chunking | ✅ código em 07/09; medição de retrieval pendente | Layout por coordenadas, limpeza determinística, seções, sidecar e chunks por tokens implementados e inspecionados; ainda não reindexados |
| 4 | Curadoria e ampliação da base | ⏳ | Protocolos reais, com procedência e cobertura de emergências e não emergências |
| 5 | Comparação de embeddings | ⏳ | Comparar o MiniLM atual com alternativas usando a mesma régua |
| 6 | Fusão de resultados e re-ranking real | ⏳ | Ordenação que separe assunto e evite concentração de chunks do mesmo documento |
| 7 | LightRAG/grafo | ⏳ fase 2 | Avaliar somente depois de a recuperação vetorial simples ter uma linha de base confiável |

## Próxima entrega: régua de recuperação

**O problema que resolve.** Hoje sabemos que o RAG piora a classificação,
mas não temos uma medida isolada que diga se uma mudança em documentos,
chunking, embeddings ou consulta colocou o protocolo correto mais acima. Isso
também bloqueia a medição das técnicas do trilho B1.

**O que vai fazer:** criar um conjunto pequeno e versionado de relatos com o
documento esperado, começando pelos casos já observados de chocolate,
obstrução urinária, cebola/alho e espirro leve. O caso leve precisa permitir
como resposta correta “nenhum protocolo de emergência”.

**Como será medido:** Precision@1 como número principal, acompanhado de MRR e
Recall@5. A primeira execução preserva o comportamento atual como linha de
base; cada mudança posterior é comparada sobre exatamente os mesmos casos.

## Marcos

| Quando | Marco |
|---|---|
| 8–19 set | Régua de recuperação de pé; base atual medida; primeira rodada de preparação documental |
| 20–30 set | Base curada ampliada e embeddings/re-ranking comparados com antes/depois |
| Outubro | Matriz de ablação completa com os componentes do trilho A e B1 |
| Novembro | Configuração e números congelados para a escrita final |

## O que está travando

Esta seção só cresce. O detalhe e o status ficam no
[backlog compartilhado](../backlog.md).

### Aberto

| # | Bloqueio | De quem depende | Visto em | Efeito | Detalhe |
|---|---|---|---|---|---|
| 1 | Com a base atual, ligar o RAG degrada o sistema | Trilho A | Rodada 4 do B2, 04/09 | −20,4 pontos de acurácia estrita e +22 falsos não urgentes no RAG direto | [B-01](../backlog.md#b-01) |
| 2 | A ordenação não separa assunto | Trilho A | Handover de 30/08 e rodada 3 do B2 | Protocolos incorretos superam o correto e podem ter score alto | [B-02](../backlog.md#b-02) |
| 3 | Base sintética e somente de emergências | Trilho A + especialista | Rodadas 3 e 4 do B2 | Enviesa qualquer contexto recuperado e não sustenta a proposta final | [B-03](../backlog.md#b-03) |
| 4 | A régua de recuperação ainda não existe | Trilho A | Planejamento do time, 31/08 | Bloqueia a avaliação isolada do trilho A e das técnicas do B1 | [B-02](../backlog.md#b-02) e [B-09](../backlog.md#b-09) |
| 8 | PDF-fonte ainda contém fusões sem evidência estrutural para corrigir | Trilho A | Rodadas 2 e 3, 07/09 | Layout, captions, `°C` e ligaturas foram corrigidos; termos como `heatstrokeassociated` exigiriam inferência lexical insegura | [B-35](../backlog.md#b-35) |

### Resolvidos

- B-29: fingerprint identifica conteúdo, modelo, revisão, receita e inventário.
- B-30: staging validado, ativação atômica e rollback preservam a base ativa.
- B-31: integração usa Chroma real temporário e embedding determinístico.
- B-36: corpo limpo foi separado do texto usado para embedding.
- B-53: vocabulário de espécie fechado em `dog`, `cat`, `dog_and_cat`.

## Fora do escopo deste trilho

Prompts e geração da decisão são do B2. Reescrita, Multi-Query, HyDE e
Whisper são do B1. O trilho A fornece a régua usada para medir as consultas,
mas não altera a lógica que as gera sem revisão do respectivo dono.
