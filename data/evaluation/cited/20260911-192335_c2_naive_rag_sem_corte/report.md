# Rodada 20260911-192335_c2_naive_rag_sem_corte

**Preset:** naive_rag_sem_corte · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-11T19:23:35.647349-03:00 · máquina DESKTOP-5UGARQ1 · commit 9a1ec45

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": true,
  "context_top_k": 3,
  "context_min_score": 0.0,
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
| **Acurácia balanceada** | **0.7746** |
| Acurácia estrita | 0.6735 IC95 [0.5756, 0.7582] |
| Cobertura | 0.9796 |
| Acurácia entre as decididas | 0.6875 |
| Macro-F1 | 0.6760 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 30 | 0.423 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
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
| EMERGENCIA | 71 | 1.0000 | 0.5493 | 0.7091 |
| NAO_EMERGENCIA | 27 | 0.4737 | 1.0000 | 0.6429 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 39 | 30 | 2 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 27 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.38 |
| Respostas com ao menos uma citação | 0.357 |
| Linhas em que nada passou de 0,70 | 1.000 |
| Score máximo médio | 0.5740 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.053 | 0.044 | 0.104 |
| generation_s | 2.211 | 2.236 | 2.85 |
| total_s | 2.264 | 2.273 | 2.894 |
| client_s | 2.282 | 2.296 | 2.917 |
