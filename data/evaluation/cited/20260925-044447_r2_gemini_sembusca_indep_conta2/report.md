# Rodada 20260925-044447_r2_gemini_sembusca_indep_conta2

**Preset:** producao · **Subconjunto:** None · **Linhas:** 122 · **Repetições:** 1

Início 2026-09-25T04:44:47.206117-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": false,
  "retrieval_mode": "vector",
  "context_top_k": 3,
  "context_min_score": 0.0,
  "rewritten_hint_enabled": false,
  "cot_enabled": false,
  "cot_position": "first",
  "self_refine_enabled": false,
  "prompt_version": "v1_grounded",
  "structured_output_mode": "schema",
  "model": "gemini-3.5-flash-lite",
  "temperature": 0.0,
  "seed": 42,
  "num_ctx": 4096,
  "num_predict": 600,
  "think": false,
  "attendant_provider": "gemini",
  "attendant_fallback": "none"
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.8149** |
| Acurácia estrita | 0.8443 IC95 [0.7695, 0.898] |
| Cobertura | 0.9344 |
| Acurácia entre as decididas | 0.9035 |
| Macro-F1 | 0.8573 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 1 | 0.013 |
| Falsos urgentes (leve tratado como emergência) | 10 | 0.217 |
| Abstenções (INCERTO) | — | 0.066 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 0.6230 |
| Menos de 5 sintomas → não emergência | n/a |
| Só sintomas leves → não emergência | n/a |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 76 | 0.8765 | 0.9342 | 0.9045 |
| NAO_EMERGENCIA | 46 | 0.9697 | 0.6957 | 0.8101 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 71 | 1 | 4 | 0 | 0 |
| NAO_EMERGENCIA | 10 | 32 | 4 | 0 | 0 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 4.465 | 3.99 | 8.481 |
| total_s | 4.465 | 3.991 | 8.481 |
| client_s | 4.481 | 4.006 | 8.497 |
