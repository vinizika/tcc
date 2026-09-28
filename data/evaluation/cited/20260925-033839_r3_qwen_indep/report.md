# Rodada 20260925-033839_r3_qwen_indep

**Preset:** naive_rag · **Subconjunto:** None · **Linhas:** 122 · **Repetições:** 1

Início 2026-09-25T03:38:39.992815-03:00 · máquina DESKTOP-5UGARQ1 · commit b277fa6 (com alterações locais)

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
| **Acurácia balanceada** | **0.8801** |
| Acurácia estrita | 0.8934 IC95 [0.8262, 0.9367] |
| Cobertura | 0.9918 |
| Acurácia entre as decididas | 0.9008 |
| Macro-F1 | 0.8880 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 5 | 0.066 |
| Falsos urgentes (leve tratado como emergência) | 7 | 0.152 |
| Abstenções (INCERTO) | — | 0.008 |
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
| EMERGENCIA | 76 | 0.9103 | 0.9342 | 0.9221 |
| NAO_EMERGENCIA | 46 | 0.8837 | 0.8261 | 0.8539 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 71 | 5 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 7 | 38 | 1 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.95 |
| Respostas com ao menos uma citação | 0.869 |
| Linhas em que nada passou de 0,70 | 0.885 |
| Score máximo médio | 0.6474 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.142 | 0.137 | 0.199 |
| generation_s | 2.538 | 2.544 | 2.884 |
| total_s | 2.68 | 2.694 | 3.035 |
| client_s | 2.692 | 2.705 | 3.041 |
