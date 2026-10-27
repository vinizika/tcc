# Rodada 20261026-215336_r27_prova1_calib

**Preset:** producao · **Subconjunto:** None · **Linhas:** 18 · **Repetições:** 1

Início 2026-10-26T21:53:36.622303-03:00 · máquina Ryu · commit 1cb7ea4 (com alterações locais)

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
| **Acurácia balanceada** | **0.9375** |
| Acurácia estrita | 0.9444 IC95 [0.7424, 0.9901] |
| Cobertura | 0.8889 |
| Acurácia entre as decididas | 1.0000 |
| Macro-F1 | 0.9667 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
| Abstenções (INCERTO) | — | 0.111 |
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
| NAO_EMERGENCIA | 8 | 1.0000 | 0.8750 | 0.9333 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 9 | 0 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 7 | 1 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 1.00 |
| Respostas com ao menos uma citação | 0.889 |
| Linhas em que nada passou de 0,70 | 0.833 |
| Score máximo médio | 0.6400 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.376 | 0.365 | 0.49 |
| generation_s | 3.449 | 3.557 | 3.9 |
| total_s | 3.825 | 3.937 | 4.311 |
| client_s | 3.841 | 3.95 | 4.323 |
