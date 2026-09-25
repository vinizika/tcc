# Rodada 20260925-041622_r5_hoje_academico_llama_tradutor_dev

**Preset:** hoje_academico_llama_tradutor · **Subconjunto:** None · **Linhas:** 50 · **Repetições:** 1

Início 2026-09-25T04:16:22.534573-03:00 · máquina DESKTOP-5UGARQ1 · commit fe11b99 (com alterações locais)

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
| **Acurácia balanceada** | **0.8375** |
| Acurácia estrita | 0.8200 IC95 [0.692, 0.9023] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.8200 |
| Macro-F1 | 0.8284 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 5 | 0.200 |
| Falsos urgentes (leve tratado como emergência) | 3 | 0.125 |
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
| EMERGENCIA | 25 | 0.8696 | 0.8000 | 0.8333 |
| NAO_EMERGENCIA | 24 | 0.7778 | 0.8750 | 0.8235 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 20 | 5 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 3 | 21 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 0.840 |
| Respostas em que a busca ficou silenciosa | 0.160 |
| Fontes citadas por resposta | 0.40 |
| Respostas com ao menos uma citação | 0.360 |
| Linhas em que nada passou de 0,70 | 0.240 |
| Score máximo médio | 0.7419 |
| Respostas com citação inválida | 0.060 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.995 | 0.99 | 1.165 |
| retrieval_s | 0.339 | 0.332 | 0.404 |
| generation_s | 1.175 | 1.184 | 1.409 |
| total_s | 2.51 | 2.547 | 2.91 |
| client_s | 2.522 | 2.555 | 2.917 |
