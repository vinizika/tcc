# Rodada 20261026-220759_r27_piloto

**Preset:** producao · **Subconjunto:** None · **Linhas:** 40 · **Repetições:** 1

Início 2026-10-26T22:07:59.450831-03:00 · máquina Ryu · commit 1cb7ea4 (com alterações locais)

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
| Acurácia estrita | 0.9500 IC95 [0.835, 0.9862] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.9500 |
| Macro-F1 | 0.9467 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 2 | 0.125 |
| Abstenções (INCERTO) | — | 0.000 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 0.6000 |
| Menos de 5 sintomas → não emergência | n/a |
| Só sintomas leves → não emergência | n/a |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 24 | 0.9231 | 1.0000 | 0.9600 |
| NAO_EMERGENCIA | 16 | 1.0000 | 0.8750 | 0.9333 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 24 | 0 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 2 | 14 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 1.07 |
| Respostas com ao menos uma citação | 0.950 |
| Linhas em que nada passou de 0,70 | 0.975 |
| Score máximo médio | 0.6397 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.547 | 0.551 | 0.668 |
| generation_s | 3.814 | 3.399 | 3.956 |
| total_s | 4.361 | 3.948 | 4.518 |
| client_s | 4.374 | 3.96 | 4.526 |
