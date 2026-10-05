# Rodada 20261005-180853_a3_qwen_dev_paralelo

**Preset:** local_qwen · **Subconjunto:** None · **Linhas:** 50 · **Repetições:** 1

Início 2026-10-05T18:08:53.013666-03:00 · máquina DESKTOP-5UGARQ1 · commit bb2cdae (com alterações locais)

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
| **Acurácia balanceada** | **0.9800** |
| Acurácia estrita | 0.9600 IC95 [0.8654, 0.989] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.9600 |
| Macro-F1 | 0.9698 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 1 | 0.040 |
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
| EMERGENCIA | 25 | 1.0000 | 0.9600 | 0.9796 |
| NAO_EMERGENCIA | 24 | 0.9231 | 1.0000 | 0.9600 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 24 | 1 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 24 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.88 |
| Respostas com ao menos uma citação | 0.860 |
| Linhas em que nada passou de 0,70 | 0.880 |
| Score máximo médio | 0.6476 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.14 | 0.141 | 0.187 |
| generation_s | 4.244 | 4.611 | 5.914 |
| total_s | 4.385 | 4.75 | 6.07 |
| client_s | 4.396 | 4.763 | 6.083 |
