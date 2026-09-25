# Rodada 20260925-041259_r5_hoje_academico_llama_dev

**Preset:** hoje_academico_llama · **Subconjunto:** None · **Linhas:** 50 · **Repetições:** 1

Início 2026-09-25T04:12:59.481059-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

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
| **Acurácia balanceada** | **0.8575** |
| Acurácia estrita | 0.8600 IC95 [0.7381, 0.9305] |
| Cobertura | 0.9800 |
| Acurácia entre as decididas | 0.8571 |
| Macro-F1 | 0.8571 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 4 | 0.160 |
| Falsos urgentes (leve tratado como emergência) | 3 | 0.125 |
| Abstenções (INCERTO) | — | 0.020 |
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
| EMERGENCIA | 25 | 0.8750 | 0.8400 | 0.8571 |
| NAO_EMERGENCIA | 24 | 0.8400 | 0.8750 | 0.8571 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 21 | 4 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 3 | 21 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 0.160 |
| Respostas em que a busca ficou silenciosa | 0.840 |
| Fontes citadas por resposta | 0.08 |
| Respostas com ao menos uma citação | 0.080 |
| Linhas em que nada passou de 0,70 | 1.000 |
| Score máximo médio | 0.5649 |
| Respostas com citação inválida | 0.020 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.314 | 0.304 | 0.359 |
| generation_s | 1.025 | 1.022 | 1.316 |
| total_s | 1.339 | 1.337 | 1.622 |
| client_s | 1.349 | 1.342 | 1.638 |
