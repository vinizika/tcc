# Rodada 20261005-181358_a3_gemini_indep

**Preset:** producao · **Subconjunto:** None · **Linhas:** 122 · **Repetições:** 1

Início 2026-10-05T18:13:58.527612-03:00 · máquina DESKTOP-5UGARQ1 · commit bb2cdae (com alterações locais)

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
| **Acurácia balanceada** | **0.8561** |
| Acurácia estrita | 0.8689 IC95 [0.7975, 0.9176] |
| Cobertura | 0.9262 |
| Acurácia entre as decididas | 0.9381 |
| Macro-F1 | 0.8974 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 1 | 0.013 |
| Falsos urgentes (leve tratado como emergência) | 6 | 0.130 |
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
| EMERGENCIA | 76 | 0.9200 | 0.9079 | 0.9139 |
| NAO_EMERGENCIA | 46 | 0.9737 | 0.8043 | 0.8810 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 69 | 1 | 6 | 0 | 0 |
| NAO_EMERGENCIA | 6 | 37 | 3 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 1.01 |
| Respostas com ao menos uma citação | 0.902 |
| Linhas em que nada passou de 0,70 | 0.885 |
| Score máximo médio | 0.6474 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.132 | 0.132 | 0.155 |
| generation_s | 4.145 | 3.828 | 4.628 |
| total_s | 4.277 | 3.963 | 4.742 |
| client_s | 4.29 | 3.976 | 4.747 |
