# Rodada 20260925-041415_r5_hoje_academico_llama_calib

**Preset:** hoje_academico_llama · **Subconjunto:** None · **Linhas:** 18 · **Repetições:** 1

Início 2026-09-25T04:14:15.033695-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": true,
  "retrieval_mode": "routed_rerank",
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
  "num_predict": 600,
  "think": false,
  "attendant_provider": "ollama",
  "attendant_fallback": "none"
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.7708** |
| Acurácia estrita | 0.7778 IC95 [0.5478, 0.91] |
| Cobertura | 0.9444 |
| Acurácia entre as decididas | 0.7647 |
| Macro-F1 | 0.7639 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 3 | 0.333 |
| Falsos urgentes (leve tratado como emergência) | 1 | 0.125 |
| Abstenções (INCERTO) | — | 0.056 |
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
| EMERGENCIA | 9 | 0.8571 | 0.6667 | 0.7500 |
| NAO_EMERGENCIA | 8 | 0.7000 | 0.8750 | 0.7778 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 6 | 3 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 1 | 7 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 0.222 |
| Respostas em que a busca ficou silenciosa | 0.778 |
| Fontes citadas por resposta | 0.17 |
| Respostas com ao menos uma citação | 0.056 |
| Linhas em que nada passou de 0,70 | 0.944 |
| Score máximo médio | 0.5708 |
| Respostas com citação inválida | 0.056 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.312 | 0.304 | 0.347 |
| generation_s | 1.066 | 1.058 | 1.442 |
| total_s | 1.378 | 1.368 | 1.741 |
| client_s | 1.388 | 1.387 | 1.747 |
