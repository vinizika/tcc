# Rodada 20260904-024054_r3_marco1

**Preset:** naive_rag · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 1

Início 2026-09-04T02:40:54.371571-03:00 · máquina DESKTOP-5UGARQ1 · commit a95f895 (com alterações locais)

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
| **Acurácia balanceada** | **0.7632** |
| Acurácia estrita | 0.6735 IC95 [0.5756, 0.7582] |
| Cobertura | 0.9898 |
| Acurácia entre as decididas | 0.6804 |
| Macro-F1 | 0.6704 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 30 | 0.423 |
| Falsos urgentes (leve tratado como emergência) | 1 | 0.037 |
| Abstenções (INCERTO) | — | 0.010 |
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
| EMERGENCIA | 71 | 0.9756 | 0.5634 | 0.7143 |
| NAO_EMERGENCIA | 27 | 0.4643 | 0.9630 | 0.6265 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 40 | 30 | 1 | 0 | 0 |
| NAO_EMERGENCIA | 1 | 26 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| Fontes citadas por resposta | 0.40 |
| Respostas com ao menos uma citação | 0.388 |
| Linhas em que nada passou de 0,70 | 1.000 |
| Score máximo médio | 0.5740 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.046 | 0.038 | 0.096 |
| generation_s | 2.098 | 2.091 | 2.636 |
| total_s | 2.145 | 2.14 | 2.721 |
| client_s | 2.162 | 2.151 | 2.738 |
