# Rodada 20260923-181051_autopsia_llm_only

**Preset:** llm_only · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-23T18:10:51.044295-03:00 · máquina DESKTOP-5UGARQ1 · commit fceab20

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": false,
  "context_top_k": 3,
  "context_min_score": 0.72,
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
| **Acurácia balanceada** | **0.8581** |
| Acurácia estrita | 0.8776 IC95 [0.7981, 0.9285] |
| Cobertura | 0.9796 |
| Acurácia entre as decididas | 0.8958 |
| Macro-F1 | 0.8646 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 5 | 0.070 |
| Falsos urgentes (leve tratado como emergência) | 5 | 0.185 |
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
| EMERGENCIA | 71 | 0.9275 | 0.9014 | 0.9143 |
| NAO_EMERGENCIA | 27 | 0.8148 | 0.8148 | 0.8148 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 64 | 5 | 2 | 0 | 0 |
| NAO_EMERGENCIA | 5 | 22 | 0 | 0 | 0 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 1.24 | 1.239 | 1.395 |
| total_s | 1.24 | 1.239 | 1.395 |
| client_s | 3.293 | 3.285 | 3.455 |
