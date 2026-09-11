# Rodada 20260911-144739_m0_llm_only

**Preset:** llm_only · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-11T14:47:39.846164-03:00 · máquina DESKTOP-5UGARQ1 · commit e4da997

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": false,
  "context_top_k": 3,
  "context_min_score": 0.0,
  "rewritten_hint_enabled": false,
  "cot_enabled": false,
  "cot_position": "first",
  "self_refine_enabled": false,
  "prompt_version": "v1_grounded",
  "structured_output_mode": "schema",
  "model": "llama3.2:3b",
  "temperature": 0.0,
  "seed": 42,
  "num_ctx": 4096,
  "num_predict": 600
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.8555** |
| Acurácia estrita | 0.8571 IC95 [0.7744, 0.913] |
| Cobertura | 0.9796 |
| Acurácia entre as decididas | 0.8750 |
| Macro-F1 | 0.8451 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 8 | 0.113 |
| Falsos urgentes (leve tratado como emergência) | 4 | 0.148 |
| Abstenções (INCERTO) | — | 0.020 |
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
| EMERGENCIA | 71 | 0.9385 | 0.8592 | 0.8971 |
| NAO_EMERGENCIA | 27 | 0.7419 | 0.8519 | 0.7931 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 61 | 8 | 2 | 0 | 0 |
| NAO_EMERGENCIA | 4 | 23 | 0 | 0 | 0 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 2.088 | 2.079 | 2.486 |
| total_s | 2.088 | 2.079 | 2.486 |
| client_s | 2.104 | 2.089 | 2.515 |
