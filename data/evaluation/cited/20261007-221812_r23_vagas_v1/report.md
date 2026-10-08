# Rodada 20261007-221812_r23_vagas_v1

**Preset:** producao · **Subconjunto:** None · **Linhas:** 22 · **Repetições:** 1

Início 2026-10-07T22:18:12.336523-03:00 · máquina Ryu · commit 6ed671d (com alterações locais)

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
| **Acurácia balanceada** | **1.0000** |
| Acurácia estrita | 0.9091 IC95 [0.7218, 0.9747] |
| Cobertura | 0.4545 |
| Acurácia entre as decididas | 0.8000 |
| Macro-F1 | 0.9000 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
| Abstenções (INCERTO) | — | 0.545 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 0.1818 |
| Menos de 5 sintomas → não emergência | n/a |
| Só sintomas leves → não emergência | n/a |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 4 | 1.0000 | 1.0000 | 1.0000 |
| NAO_EMERGENCIA | 4 | 0.6667 | 1.0000 | 0.8000 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 4 | 0 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 4 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.45 |
| Respostas com ao menos uma citação | 0.455 |
| Linhas em que nada passou de 0,70 | 0.909 |
| Score máximo médio | 0.6304 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.001 |
| retrieval_s | 1.542 | 0.637 | 5.246 |
| generation_s | 2.937 | 3.123 | 5.112 |
| total_s | 4.479 | 3.95 | 6.75 |
| client_s | 4.569 | 4.056 | 6.767 |
