# Rodada 20260925-043411_r2_gemini_sembusca_dev_conta1

**Preset:** producao · **Subconjunto:** None · **Linhas:** 50 · **Repetições:** 1

Início 2026-09-25T04:34:11.394338-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

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
| **Acurácia balanceada** | **0.9583** |
| Acurácia estrita | 0.9600 IC95 [0.8654, 0.989] |
| Cobertura | 0.9600 |
| Acurácia entre as decididas | 0.9792 |
| Macro-F1 | 0.9685 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 1 | 0.042 |
| Abstenções (INCERTO) | — | 0.040 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 0.5000 |
| Menos de 5 sintomas → não emergência | n/a |
| Só sintomas leves → não emergência | n/a |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 25 | 0.9615 | 1.0000 | 0.9804 |
| NAO_EMERGENCIA | 24 | 1.0000 | 0.9167 | 0.9565 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 25 | 0 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 1 | 22 | 1 | 0 | 0 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 4.169 | 3.877 | 8.012 |
| total_s | 4.169 | 3.878 | 8.013 |
| client_s | 4.185 | 3.891 | 8.032 |
