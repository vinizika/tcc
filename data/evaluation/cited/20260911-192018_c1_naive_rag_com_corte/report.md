# Rodada 20260911-192018_c1_naive_rag_com_corte

**Preset:** naive_rag · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-11T19:20:18.161588-03:00 · máquina DESKTOP-5UGARQ1 · commit 9a1ec45

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": true,
  "context_top_k": 3,
  "context_min_score": 0.7,
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
  "num_predict": 600
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.8925** |
| Acurácia estrita | 0.8776 IC95 [0.7981, 0.9285] |
| Cobertura | 0.9796 |
| Acurácia entre as decididas | 0.8958 |
| Macro-F1 | 0.8719 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 8 | 0.113 |
| Falsos urgentes (leve tratado como emergência) | 2 | 0.074 |
| Abstenções (INCERTO) | — | 0.020 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 0.7245 |
| Menos de 5 sintomas → não emergência | 0.9898 |
| Só sintomas leves → não emergência | 1.0000 |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 71 | 0.9683 | 0.8592 | 0.9104 |
| NAO_EMERGENCIA | 27 | 0.7576 | 0.9259 | 0.8333 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 61 | 8 | 2 | 0 | 0 |
| NAO_EMERGENCIA | 2 | 25 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 0.000 |
| Respostas em que a busca ficou silenciosa | 1.000 |
| Fontes citadas por resposta | 0.00 |
| Respostas com ao menos uma citação | 0.000 |
| Linhas em que nada passou de 0,70 | 1.000 |
| Score máximo médio | 0.5740 |
| Respostas com citação inválida | 0.000 |

> **A busca ficou silenciosa em todas as linhas.** Nenhum trecho passou do corte de relevância, então o classificador decidiu sem contexto em 100% dos casos: esta rodada mediu o mesmo que o braço sem recuperação.

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.061 | 0.052 | 0.119 |
| generation_s | 1.896 | 1.892 | 2.261 |
| total_s | 1.957 | 1.963 | 2.345 |
| client_s | 1.973 | 1.972 | 2.359 |
