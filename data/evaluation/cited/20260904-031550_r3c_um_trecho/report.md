# Rodada 20260904-031550_r3c_um_trecho

**Preset:** naive_rag · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-04T03:15:50.340602-03:00 · máquina DESKTOP-5UGARQ1 · commit a95f895 (com alterações locais)

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": true,
  "context_top_k": 1,
  "context_min_score": 0.0,
  "rewritten_hint_enabled": false,
  "cot_enabled": false,
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
| **Acurácia balanceada** | **0.6899** |
| Acurácia estrita | 0.6837 IC95 [0.5862, 0.7673] |
| Cobertura | 0.9592 |
| Acurácia entre as decididas | 0.7128 |
| Macro-F1 | 0.6703 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 19 | 0.268 |
| Falsos urgentes (leve tratado como emergência) | 8 | 0.296 |
| Abstenções (INCERTO) | — | 0.041 |
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
| EMERGENCIA | 71 | 0.8571 | 0.6761 | 0.7559 |
| NAO_EMERGENCIA | 27 | 0.5000 | 0.7037 | 0.5846 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 48 | 19 | 4 | 0 | 0 |
| NAO_EMERGENCIA | 8 | 19 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| Fontes citadas por resposta | 0.62 |
| Respostas com ao menos uma citação | 0.622 |
| Linhas em que nada passou de 0,70 | 1.000 |
| Score máximo médio | 0.5740 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.034 | 0.031 | 0.055 |
| generation_s | 2.088 | 2.069 | 2.948 |
| total_s | 2.122 | 2.095 | 2.974 |
| client_s | 2.138 | 2.115 | 2.984 |
