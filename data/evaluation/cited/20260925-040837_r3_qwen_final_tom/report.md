# Rodada 20260925-040837_r3_qwen_final_tom

**Preset:** local_qwen · **Subconjunto:** None · **Linhas:** 74 · **Repetições:** 1

Início 2026-09-25T04:08:37.130695-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

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
  "model": "qwen3:8b",
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
| **Acurácia balanceada** | **0.9459** |
| Acurácia estrita | 0.9459 IC95 [0.8691, 0.9788] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.9459 |
| Macro-F1 | 0.9722 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 4 | 0.054 |
| Falsos urgentes (leve tratado como emergência) | 0 | n/a |
| Abstenções (INCERTO) | — | 0.000 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 1.0000 |
| Menos de 5 sintomas → não emergência | n/a |
| Só sintomas leves → não emergência | n/a |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 74 | 1.0000 | 0.9459 | 0.9722 |
| NAO_EMERGENCIA | 0 | 0.0000 | n/a | n/a |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 70 | 4 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 0 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 1.03 |
| Respostas com ao menos uma citação | 0.959 |
| Linhas em que nada passou de 0,70 | 0.716 |
| Score máximo médio | 0.6663 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.14 | 0.13 | 0.211 |
| generation_s | 2.554 | 2.524 | 2.842 |
| total_s | 2.694 | 2.671 | 2.986 |
| client_s | 2.706 | 2.681 | 3.002 |
