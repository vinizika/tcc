# Rodada 20260925-041837_r5_hoje_academico_llama_tradutor_calib

**Preset:** hoje_academico_llama_tradutor · **Subconjunto:** None · **Linhas:** 18 · **Repetições:** 1

Início 2026-09-25T04:18:37.077720-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

## Configuração efetiva

```json
{
  "query_rewriting_enabled": true,
  "multi_query_enabled": true,
  "hyde_enabled": true,
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
| **Acurácia balanceada** | **1.0000** |
| Acurácia estrita | 0.9444 IC95 [0.7424, 0.9901] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.9444 |
| Macro-F1 | 0.9706 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
| Abstenções (INCERTO) | — | 0.000 |
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
| NAO_EMERGENCIA | 8 | 0.8889 | 1.0000 | 0.9412 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 9 | 0 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 8 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 0.889 |
| Respostas em que a busca ficou silenciosa | 0.111 |
| Fontes citadas por resposta | 0.61 |
| Respostas com ao menos uma citação | 0.500 |
| Linhas em que nada passou de 0,70 | 0.278 |
| Score máximo médio | 0.7315 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.998 | 0.978 | 1.27 |
| retrieval_s | 0.334 | 0.327 | 0.372 |
| generation_s | 1.175 | 1.16 | 1.473 |
| total_s | 2.507 | 2.559 | 2.88 |
| client_s | 2.517 | 2.569 | 2.891 |
