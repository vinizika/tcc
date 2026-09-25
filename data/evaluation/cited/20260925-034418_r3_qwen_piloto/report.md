# Rodada 20260925-034418_r3_qwen_piloto

**Preset:** naive_rag · **Subconjunto:** None · **Linhas:** 40 · **Repetições:** 1

Início 2026-09-25T03:44:18.006746-03:00 · máquina DESKTOP-5UGARQ1 · commit d7c87df (com alterações locais)

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
  "think": false
}
```

## Resultado

| Métrica | Valor |
|---|---|
| **Acurácia balanceada** | **0.9062** |
| Acurácia estrita | 0.9250 IC95 [0.8014, 0.9742] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.9250 |
| Macro-F1 | 0.9189 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 3 | 0.188 |
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
| EMERGENCIA | 24 | 0.8889 | 1.0000 | 0.9412 |
| NAO_EMERGENCIA | 16 | 1.0000 | 0.8125 | 0.8966 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 24 | 0 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 3 | 13 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.95 |
| Respostas com ao menos uma citação | 0.825 |
| Linhas em que nada passou de 0,70 | 0.975 |
| Score máximo médio | 0.6397 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.314 | 0.3 | 0.469 |
| generation_s | 2.754 | 2.779 | 3.157 |
| total_s | 3.068 | 3.072 | 3.506 |
| client_s | 3.081 | 3.08 | 3.515 |
