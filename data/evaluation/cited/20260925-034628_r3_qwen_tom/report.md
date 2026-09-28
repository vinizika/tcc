# Rodada 20260925-034628_r3_qwen_tom

**Preset:** naive_rag · **Subconjunto:** None · **Linhas:** 74 · **Repetições:** 1

Início 2026-09-25T03:46:28.454273-03:00 · máquina DESKTOP-5UGARQ1 · commit 81231b9 (com alterações locais)

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
| **Acurácia balanceada** | **0.9459** |
| Acurácia estrita | 0.9459 IC95 [0.8691, 0.9788] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.9459 |
| Macro-F1 | 0.9722 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 4 | 0.054 |
| Falsos urgentes (leve tratado como emergência) | 0 | n/a |
| Abstenções (INCERTO) | — | 0.000 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 1.0000 |
| Menos de 5 sintomas → não emergência | n/a |
| Só sintomas leves → não emergência | n/a |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 74 | 1.0000 | 0.9459 | 0.9722 |
| NAO_EMERGENCIA | 0 | 0.0000 | n/a | n/a |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 70 | 4 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 0 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 1.03 |
| Respostas com ao menos uma citação | 0.959 |
| Linhas em que nada passou de 0,70 | 0.716 |
| Score máximo médio | 0.6663 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.121 | 0.114 | 0.159 |
| generation_s | 2.552 | 2.545 | 2.865 |
| total_s | 2.674 | 2.668 | 2.994 |
| client_s | 2.684 | 2.678 | 2.998 |
