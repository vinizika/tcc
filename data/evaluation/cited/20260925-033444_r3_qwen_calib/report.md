# Rodada 20260925-033444_r3_qwen_calib

**Preset:** naive_rag · **Subconjunto:** None · **Linhas:** 18 · **Repetições:** 1

Início 2026-09-25T03:34:44.753092-03:00 · máquina DESKTOP-5UGARQ1 · commit b277fa6 (com alterações locais)

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
| **Acurácia balanceada** | **1.0000** |
| Acurácia estrita | 1.0000 IC95 [0.8241, 1.0] |
| Cobertura | 0.9444 |
| Acurácia entre as decididas | 1.0000 |
| Macro-F1 | 1.0000 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
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
| EMERGENCIA | 9 | 1.0000 | 1.0000 | 1.0000 |
| NAO_EMERGENCIA | 8 | 1.0000 | 1.0000 | 1.0000 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 9 | 0 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 8 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.78 |
| Respostas com ao menos uma citação | 0.667 |
| Linhas em que nada passou de 0,70 | 0.833 |
| Score máximo médio | 0.6400 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.143 | 0.137 | 0.18 |
| generation_s | 2.421 | 2.516 | 2.855 |
| total_s | 2.564 | 2.663 | 2.991 |
| client_s | 2.575 | 2.675 | 3.007 |
