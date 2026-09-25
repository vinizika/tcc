# Rodada 20260925-035453_r4_qwen_sembusca_indep

**Preset:** llm_only · **Subconjunto:** None · **Linhas:** 122 · **Repetições:** 1

Início 2026-09-25T03:54:53.966588-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

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
  "model": "qwen3:8b",
  "temperature": 0.0,
  "seed": 42,
  "num_ctx": 4096,
  "num_predict": 600,
  "think": false
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.7640** |
| Acurácia estrita | 0.7541 IC95 [0.6707, 0.822] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.7541 |
| Macro-F1 | 0.7486 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 21 | 0.276 |
| Falsos urgentes (leve tratado como emergência) | 9 | 0.196 |
| Abstenções (INCERTO) | — | 0.000 |
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
| EMERGENCIA | 76 | 0.8594 | 0.7237 | 0.7857 |
| NAO_EMERGENCIA | 46 | 0.6379 | 0.8043 | 0.7115 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 55 | 21 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 9 | 37 | 0 | 0 | 0 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 2.135 | 2.151 | 2.414 |
| total_s | 2.136 | 2.152 | 2.414 |
| client_s | 2.146 | 2.167 | 2.431 |
