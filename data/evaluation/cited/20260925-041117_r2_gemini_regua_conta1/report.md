# Rodada 20260925-041117_r2_gemini_regua_conta1

**Preset:** producao · **Subconjunto:** None · **Linhas:** 66 · **Repetições:** 1

Início 2026-09-25T04:11:17.046831-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

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
| **Acurácia balanceada** | **0.9683** |
| Acurácia estrita | 0.9697 IC95 [0.8961, 0.9917] |
| Cobertura | 0.9848 |
| Acurácia entre as decididas | 0.9846 |
| Macro-F1 | 0.9777 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 1 | 0.038 |
| Abstenções (INCERTO) | — | 0.015 |
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
| NAO_EMERGENCIA | 26 | 1.0000 | 0.9615 | 0.9804 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 39 | 0 | 1 | 0 | 0 |
| NAO_EMERGENCIA | 1 | 25 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 1.05 |
| Respostas com ao menos uma citação | 0.970 |
| Linhas em que nada passou de 0,70 | 0.742 |
| Score máximo médio | 0.6573 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.102 | 0.096 | 0.138 |
| generation_s | 4.177 | 3.921 | 7.906 |
| total_s | 4.279 | 4.019 | 8.021 |
| client_s | 4.289 | 4.023 | 8.029 |
