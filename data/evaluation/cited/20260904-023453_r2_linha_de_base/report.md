# Rodada 20260904-023453_r2_linha_de_base

**Preset:** llm_only · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 2

Início 2026-09-04T02:34:53.772015-03:00 · máquina DESKTOP-5UGARQ1 · commit a95f895 (com alterações locais)

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
| **Acurácia balanceada** | **0.8925** |
| Acurácia estrita | 0.8776 IC95 [0.7981, 0.9285] |
| Cobertura | 0.9796 |
| Acurácia entre as decididas | 0.8958 |
| Macro-F1 | 0.8719 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 8 | 0.113 |
| Falsos urgentes (leve tratado como emergência) | 2 | 0.074 |
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
| EMERGENCIA | 71 | 0.9683 | 0.8592 | 0.9104 |
| NAO_EMERGENCIA | 27 | 0.7576 | 0.9259 | 0.8333 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 61 | 8 | 2 | 0 | 0 |
| NAO_EMERGENCIA | 2 | 25 | 0 | 0 | 0 |

### Estabilidade entre repetições

- Repetições: 2
- Linhas com resposta idêntica em todas: 1.000
- Linhas instáveis: 0
- Acurácia balanceada: média 0.8925, desvio 0.0000, faixa 0.8925–0.8925

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 1.801 | 1.796 | 2.098 |
| total_s | 1.801 | 1.796 | 2.098 |
| client_s | 1.816 | 1.818 | 2.12 |
