# Rodada 20260911-145537_m1_llm_only_cot

**Preset:** llm_only_cot · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 3

Início 2026-09-11T14:55:37.036377-03:00 · máquina DESKTOP-5UGARQ1 · commit e4da997

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
| **Acurácia balanceada** | **0.4085** |
| Acurácia estrita | 0.5918 IC95 [0.4929, 0.6839] |
| Cobertura | 0.7653 |
| Acurácia entre as decididas | 0.7733 |
| Macro-F1 | 0.4000 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 1 | 0.014 |
| Falsos urgentes (leve tratado como emergência) | 16 | 0.593 |
| Abstenções (INCERTO) | — | 0.235 |
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
| EMERGENCIA | 71 | 0.7838 | 0.8169 | 0.8000 |
| NAO_EMERGENCIA | 27 | 0.0000 | 0.0000 | 0.0000 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 58 | 1 | 12 | 0 | 0 |
| NAO_EMERGENCIA | 16 | 0 | 11 | 0 | 0 |

### Estabilidade entre repetições

- Repetições: 3
- Linhas com resposta idêntica em todas: 0.969
- Linhas instáveis: 3
- Acurácia balanceada: média 0.3991, desvio 0.0066, faixa 0.3944–0.4085

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 3.988 | 3.208 | 8.053 |
| total_s | 3.988 | 3.208 | 8.053 |
| client_s | 4.004 | 3.235 | 8.072 |
