# Rodada 20260925-041929_r5_hoje_academico_llama_tradutor_regua

**Preset:** hoje_academico_llama_tradutor · **Subconjunto:** None · **Linhas:** 66 · **Repetições:** 1

Início 2026-09-25T04:19:29.355812-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

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
| **Acurácia balanceada** | **0.9250** |
| Acurácia estrita | 0.9091 IC95 [0.8155, 0.9577] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.9091 |
| Macro-F1 | 0.9077 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 6 | 0.150 |
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
| EMERGENCIA | 40 | 1.0000 | 0.8500 | 0.9189 |
| NAO_EMERGENCIA | 26 | 0.8125 | 1.0000 | 0.8966 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 34 | 6 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 26 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 0.909 |
| Respostas em que a busca ficou silenciosa | 0.091 |
| Fontes citadas por resposta | 0.47 |
| Respostas com ao menos uma citação | 0.424 |
| Linhas em que nada passou de 0,70 | 0.167 |
| Score máximo médio | 0.7460 |
| Respostas com citação inválida | 0.015 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.965 | 0.942 | 1.253 |
| retrieval_s | 0.33 | 0.328 | 0.351 |
| generation_s | 1.147 | 1.166 | 1.376 |
| total_s | 2.442 | 2.436 | 2.861 |
| client_s | 2.452 | 2.447 | 2.865 |
