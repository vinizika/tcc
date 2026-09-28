# Rodada 20260925-041445_r5_hoje_academico_llama_regua

**Preset:** hoje_academico_llama · **Subconjunto:** None · **Linhas:** 66 · **Repetições:** 1

Início 2026-09-25T04:14:45.966193-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": true,
  "retrieval_mode": "routed_rerank",
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
  "num_predict": 600,
  "think": false,
  "attendant_provider": "ollama",
  "attendant_fallback": "none"
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.9000** |
| Acurácia estrita | 0.8788 IC95 [0.7786, 0.9373] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.8788 |
| Macro-F1 | 0.8778 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 8 | 0.200 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
| Abstenções (INCERTO) | — | 0.000 |
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
| EMERGENCIA | 40 | 1.0000 | 0.8000 | 0.8889 |
| NAO_EMERGENCIA | 26 | 0.7647 | 1.0000 | 0.8667 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 32 | 8 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 26 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 0.273 |
| Respostas em que a busca ficou silenciosa | 0.727 |
| Fontes citadas por resposta | 0.20 |
| Respostas com ao menos uma citação | 0.121 |
| Linhas em que nada passou de 0,70 | 0.985 |
| Score máximo médio | 0.5931 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.298 | 0.296 | 0.32 |
| generation_s | 1.026 | 1.022 | 1.42 |
| total_s | 1.323 | 1.315 | 1.725 |
| client_s | 1.334 | 1.327 | 1.741 |
