# Rodada 20260911-152057_m4_naive_rag_cot

**Preset:** naive_rag_cot · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-11T15:20:57.532636-03:00 · máquina DESKTOP-5UGARQ1 · commit e4da997

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": true,
  "context_top_k": 3,
  "context_min_score": 0.0,
  "rewritten_hint_enabled": false,
  "cot_enabled": true,
  "cot_position": "first",
  "self_refine_enabled": false,
  "prompt_version": "v1_grounded",
  "structured_output_mode": "schema",
  "model": "llama3.2:3b",
  "temperature": 0.0,
  "seed": 42,
  "num_ctx": 4096,
  "num_predict": 1024
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.3894** |
| Acurácia estrita | 0.3980 IC95 [0.3067, 0.497] |
| Cobertura | 0.6224 |
| Acurácia entre as decididas | 0.6393 |
| Macro-F1 | 0.4595 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 22 | 0.310 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
| Abstenções (INCERTO) | — | 0.378 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 0.7245 |
| Menos de 5 sintomas → não emergência | 0.9898 |
| Só sintomas leves → não emergência | 1.0000 |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 71 | 1.0000 | 0.4085 | 0.5800 |
| NAO_EMERGENCIA | 27 | 0.3125 | 0.3704 | 0.3390 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 29 | 22 | 20 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 10 | 17 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| Fontes citadas por resposta | 0.32 |
| Respostas com ao menos uma citação | 0.276 |
| Linhas em que nada passou de 0,70 | 1.000 |
| Score máximo médio | 0.5740 |
| Respostas com citação inválida | 0.010 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.074 | 0.067 | 0.133 |
| generation_s | 3.994 | 3.276 | 8.914 |
| total_s | 4.069 | 3.344 | 9.045 |
| client_s | 4.087 | 3.365 | 9.063 |
