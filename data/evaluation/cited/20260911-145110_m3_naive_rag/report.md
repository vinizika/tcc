# Rodada 20260911-145110_m3_naive_rag

**Preset:** naive_rag · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-11T14:51:10.036362-03:00 · máquina DESKTOP-5UGARQ1 · commit e4da997

## Configuração efetiva

```json
{
  "query_rewriting_enabled": false,
  "multi_query_enabled": false,
  "hyde_enabled": false,
  "retrieval_enabled": true,
  "context_top_k": 3,
  "context_min_score": 0.0,
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
| **Acurácia balanceada** | **0.7676** |
| Acurácia estrita | 0.6633 IC95 [0.5651, 0.7491] |
| Cobertura | 0.9694 |
| Acurácia entre as decididas | 0.6842 |
| Macro-F1 | 0.6701 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 30 | 0.423 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
| Abstenções (INCERTO) | — | 0.031 |
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
| EMERGENCIA | 71 | 1.0000 | 0.5352 | 0.6972 |
| NAO_EMERGENCIA | 27 | 0.4737 | 1.0000 | 0.6429 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 38 | 30 | 3 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 27 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| Fontes citadas por resposta | 0.33 |
| Respostas com ao menos uma citação | 0.327 |
| Linhas em que nada passou de 0,70 | 1.000 |
| Score máximo médio | 0.5740 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.078 | 0.067 | 0.18 |
| generation_s | 2.528 | 2.508 | 3.215 |
| total_s | 2.607 | 2.585 | 3.266 |
| client_s | 2.621 | 2.598 | 3.283 |
