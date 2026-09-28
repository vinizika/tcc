# Rodada 20260923-183115_autopsia_ab_prompt_1209

**Preset:** llm_only · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-23T18:31:15.350334-03:00 · máquina DESKTOP-5UGARQ1 · commit fceab20 (com alterações locais)

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
| **Acurácia balanceada** | **0.8740** |
| Acurácia estrita | 0.8673 IC95 [0.7862, 0.9208] |
| Cobertura | 0.9796 |
| Acurácia entre as decididas | 0.8854 |
| Macro-F1 | 0.8586 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 8 | 0.113 |
| Falsos urgentes (leve tratado como emergência) | 3 | 0.111 |
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
| EMERGENCIA | 71 | 0.9531 | 0.8592 | 0.9037 |
| NAO_EMERGENCIA | 27 | 0.7500 | 0.8889 | 0.8136 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 61 | 8 | 2 | 0 | 0 |
| NAO_EMERGENCIA | 3 | 24 | 0 | 0 | 0 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 1.825 | 1.829 | 2.188 |
| total_s | 1.825 | 1.83 | 2.188 |
| client_s | 1.839 | 1.852 | 2.208 |
