# Rodada 20260911-151445_m2_posthoc

**Preset:** llm_only_cot_posthoc · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-11T15:14:45.065187-03:00 · máquina DESKTOP-5UGARQ1 · commit e4da997

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
  "cot_enabled": true,
  "cot_position": "last",
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
| **Acurácia balanceada** | **0.6641** |
| Acurácia estrita | 0.7959 IC95 [0.7057, 0.8638] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.7959 |
| Macro-F1 | 0.6859 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 3 | 0.042 |
| Falsos urgentes (leve tratado como emergência) | 17 | 0.630 |
| Abstenções (INCERTO) | — | 0.000 |
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
| EMERGENCIA | 71 | 0.8000 | 0.9577 | 0.8718 |
| NAO_EMERGENCIA | 27 | 0.7692 | 0.3704 | 0.5000 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 68 | 3 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 17 | 10 | 0 | 0 | 0 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 3.728 | 3.496 | 4.771 |
| total_s | 3.728 | 3.497 | 4.772 |
| client_s | 3.745 | 3.521 | 4.794 |
