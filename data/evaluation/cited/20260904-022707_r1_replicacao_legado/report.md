# Rodada 20260904-022707_r1_replicacao_legado

**Preset:** legacy · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 3

Início 2026-09-04T02:27:07.176016-03:00 · máquina DESKTOP-5UGARQ1 · commit a95f895

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
  "self_refine_enabled": false,
  "prompt_version": "v0_legacy",
  "structured_output_mode": "json",
  "model": "llama3.2:3b",
  "temperature": 0.8,
  "seed": 1000,
  "num_ctx": 4096,
  "num_predict": -1
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.6659** |
| Acurácia estrita | 0.7653 IC95 [0.6724, 0.8382] |
| Cobertura | 0.9286 |
| Acurácia entre as decididas | 0.8242 |
| Macro-F1 | 0.7106 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 4 | 0.056 |
| Falsos urgentes (leve tratado como emergência) | 12 | 0.444 |
| Abstenções (INCERTO) | — | 0.071 |
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
| EMERGENCIA | 71 | 0.8400 | 0.8873 | 0.8630 |
| NAO_EMERGENCIA | 27 | 0.7500 | 0.4444 | 0.5581 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 63 | 4 | 4 | 0 | 0 |
| NAO_EMERGENCIA | 12 | 12 | 3 | 0 | 0 |

### Estabilidade entre repetições

- Repetições: 3
- Linhas com resposta idêntica em todas: 0.714
- Linhas instáveis: 28
- Acurácia balanceada: média 0.6150, desvio 0.0389, faixa 0.5715–0.6659

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 1.499 | 1.43 | 1.821 |
| total_s | 1.499 | 1.43 | 1.821 |
| client_s | 1.514 | 1.446 | 1.833 |
