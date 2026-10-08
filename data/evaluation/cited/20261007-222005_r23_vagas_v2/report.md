# Rodada 20261007-222005_r23_vagas_v2

**Preset:** producao_suficiencia · **Subconjunto:** None · **Linhas:** 22 · **Repetições:** 1

Início 2026-10-07T22:20:05.400564-03:00 · máquina Ryu · commit 6ed671d (com alterações locais)

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
  "prompt_version": "v2_suficiencia",
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
| Acurácia estrita | 1.0000 IC95 [0.8513, 1.0] |
| Cobertura | 0.3636 |
| Acurácia entre as decididas | 1.0000 |
| Macro-F1 | 1.0000 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
| Abstenções (INCERTO) | — | 0.636 |
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
| NAO_EMERGENCIA | 4 | 1.0000 | 1.0000 | 1.0000 |

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
| Fontes citadas por resposta | 0.41 |
| Respostas com ao menos uma citação | 0.409 |
| Linhas em que nada passou de 0,70 | 0.909 |
| Score máximo médio | 0.6304 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.0 |
| retrieval_s | 0.698 | 0.564 | 1.397 |
| generation_s | 6.955 | 3.319 | 29.618 |
| total_s | 7.654 | 4.034 | 30.148 |
| client_s | 7.708 | 4.061 | 30.361 |
