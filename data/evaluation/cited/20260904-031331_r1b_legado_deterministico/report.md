# Rodada 20260904-031331_r1b_legado_deterministico

**Preset:** legacy · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-04T03:13:31.231011-03:00 · máquina DESKTOP-5UGARQ1 · commit a95f895 (com alterações locais)

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
  "temperature": 0.0,
  "seed": 42,
  "num_ctx": 4096,
  "num_predict": -1
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.5715** |
| Acurácia estrita | 0.7449 IC95 [0.6505, 0.8208] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.7449 |
| Macro-F1 | 0.5652 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 3 | 0.042 |
| Falsos urgentes (leve tratado como emergência) | 22 | 0.815 |
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
| EMERGENCIA | 71 | 0.7556 | 0.9577 | 0.8447 |
| NAO_EMERGENCIA | 27 | 0.6250 | 0.1852 | 0.2857 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 68 | 3 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 22 | 5 | 0 | 0 | 0 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.0 | 0.0 | 0.0 |
| generation_s | 1.372 | 1.345 | 1.619 |
| total_s | 1.373 | 1.345 | 1.619 |
| client_s | 1.386 | 1.359 | 1.635 |
