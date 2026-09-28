# Rodada 20260925-041607_r2_gemini_indep_conta1

**Preset:** producao · **Subconjunto:** None · **Linhas:** 122 · **Repetições:** 1

Início 2026-09-25T04:16:07.958747-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

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
| **Acurácia balanceada** | **0.8844** |
| Acurácia estrita | 0.8934 IC95 [0.8262, 0.9367] |
| Cobertura | 0.9262 |
| Acurácia entre as decididas | 0.9646 |
| Macro-F1 | 0.9233 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 1 | 0.013 |
| Falsos urgentes (leve tratado como emergência) | 3 | 0.065 |
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
| EMERGENCIA | 76 | 0.9589 | 0.9211 | 0.9396 |
| NAO_EMERGENCIA | 46 | 0.9750 | 0.8478 | 0.9070 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 70 | 1 | 5 | 0 | 0 |
| NAO_EMERGENCIA | 3 | 39 | 4 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.98 |
| Respostas com ao menos uma citação | 0.893 |
| Linhas em que nada passou de 0,70 | 0.885 |
| Score máximo médio | 0.6474 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.15 | 0.147 | 0.196 |
| generation_s | 4.16 | 3.811 | 7.982 |
| total_s | 4.311 | 3.975 | 8.108 |
| client_s | 4.321 | 3.981 | 8.112 |
