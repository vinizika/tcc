# Rodada 20260923-183742_autopsia_rag_query_sem_gemini

**Preset:** rag_query · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-23T18:37:42.700505-03:00 · máquina DESKTOP-5UGARQ1 · commit fceab20

## Configuração efetiva

```json
{
  "query_rewriting_enabled": true,
  "multi_query_enabled": true,
  "hyde_enabled": true,
  "retrieval_enabled": true,
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
| **Acurácia balanceada** | **0.7081** |
| Acurácia estrita | 0.8265 IC95 [0.7396, 0.8888] |
| Cobertura | 0.9796 |
| Acurácia entre as decididas | 0.8438 |
| Macro-F1 | 0.7529 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 15 | 0.556 |
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
| EMERGENCIA | 71 | 0.8214 | 0.9718 | 0.8903 |
| NAO_EMERGENCIA | 27 | 1.0000 | 0.4444 | 0.6154 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 69 | 0 | 2 | 0 | 0 |
| NAO_EMERGENCIA | 15 | 12 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 0.898 |
| Respostas em que a busca ficou silenciosa | 0.102 |
| Fontes citadas por resposta | 0.89 |
| Respostas com ao menos uma citação | 0.837 |
| Linhas em que nada passou de 0,70 | 0.102 |
| Score máximo médio | 0.7635 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.976 | 0.915 | 1.136 |
| retrieval_s | 0.331 | 0.333 | 0.354 |
| generation_s | 1.321 | 1.328 | 1.511 |
| total_s | 2.629 | 2.586 | 2.873 |
| client_s | 2.644 | 2.598 | 2.895 |
