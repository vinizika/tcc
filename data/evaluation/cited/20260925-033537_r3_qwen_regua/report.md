# Rodada 20260925-033537_r3_qwen_regua

**Preset:** naive_rag · **Subconjunto:** None · **Linhas:** 66 · **Repetições:** 1

Início 2026-09-25T03:35:37.584413-03:00 · máquina DESKTOP-5UGARQ1 · commit b277fa6 (com alterações locais)

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": true,
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
| **Acurácia balanceada** | **0.9683** |
| Acurácia estrita | 0.9697 IC95 [0.8961, 0.9917] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.9697 |
| Macro-F1 | 0.9683 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 1 | 0.025 |
| Falsos urgentes (leve tratado como emergência) | 1 | 0.038 |
| Abstenções (INCERTO) | — | 0.000 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 0.6061 |
| Menos de 5 sintomas → não emergência | n/a |
| Só sintomas leves → não emergência | n/a |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 40 | 0.9750 | 0.9750 | 0.9750 |
| NAO_EMERGENCIA | 26 | 0.9615 | 0.9615 | 0.9615 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 39 | 1 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 1 | 25 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.91 |
| Respostas com ao menos uma citação | 0.909 |
| Linhas em que nada passou de 0,70 | 0.742 |
| Score máximo médio | 0.6573 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.113 | 0.11 | 0.138 |
| generation_s | 2.518 | 2.51 | 2.824 |
| total_s | 2.631 | 2.635 | 2.94 |
| client_s | 2.644 | 2.648 | 2.958 |
