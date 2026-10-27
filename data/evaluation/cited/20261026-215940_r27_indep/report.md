# Rodada 20261026-215940_r27_indep

**Preset:** producao · **Subconjunto:** None · **Linhas:** 122 · **Repetições:** 1

Início 2026-10-26T21:59:40.009576-03:00 · máquina Ryu · commit 1cb7ea4 (com alterações locais)

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
  "model": "gemini-3.5-flash-lite",
  "temperature": 0.0,
  "seed": 42,
  "num_ctx": 4096,
  "num_predict": 600,
  "think": false,
  "attendant_provider": "gemini",
  "attendant_fallback": "none"
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.8670** |
| Acurácia estrita | 0.8770 IC95 [0.807, 0.9241] |
| Cobertura | 0.9262 |
| Acurácia entre as decididas | 0.9469 |
| Macro-F1 | 0.9071 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 1 | 0.013 |
| Falsos urgentes (leve tratado como emergência) | 5 | 0.109 |
| Abstenções (INCERTO) | — | 0.074 |
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
| EMERGENCIA | 76 | 0.9324 | 0.9079 | 0.9200 |
| NAO_EMERGENCIA | 46 | 0.9744 | 0.8261 | 0.8941 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 69 | 1 | 6 | 0 | 0 |
| NAO_EMERGENCIA | 5 | 38 | 3 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.99 |
| Respostas com ao menos uma citação | 0.902 |
| Linhas em que nada passou de 0,70 | 0.885 |
| Score máximo médio | 0.6474 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.406 | 0.343 | 0.529 |
| generation_s | 3.62 | 3.603 | 4.17 |
| total_s | 4.026 | 3.981 | 4.608 |
| client_s | 4.041 | 3.998 | 4.614 |
