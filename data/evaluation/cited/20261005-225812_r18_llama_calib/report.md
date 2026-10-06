# Rodada 20261005-225812_r18_llama_calib

**Preset:** local_llama · **Subconjunto:** None · **Linhas:** 66 · **Repetições:** 1

Início 2026-10-05T22:58:12.284385-03:00 · máquina Ryu · commit 698da6a (com alterações locais)

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
| **Acurácia balanceada** | **0.7750** |
| Acurácia estrita | 0.7879 IC95 [0.6749, 0.8692] |
| Cobertura | 1.0000 |
| Acurácia entre as decididas | 0.7879 |
| Macro-F1 | 0.7776 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 3 | 0.075 |
| Falsos urgentes (leve tratado como emergência) | 9 | 0.375 |
| Abstenções (INCERTO) | — | 0.000 |
| Saída inválida | — | 0.000 |

### Referências sem modelo

Regras triviais sobre este conjunto. Se o sistema não as supera, o ganho medido não vem da compreensão do relato.

| Referência | Acurácia |
|---|---|
| Sempre responder emergência | 0.6061 |
| Menos de 5 sintomas → não emergência | n/a |
| Só sintomas leves → não emergência | n/a |

### Por classe

| Classe | Apoio | Precisão | Revocação | F1 |
|---|---|---|---|---|
| EMERGENCIA | 40 | 0.7708 | 0.9250 | 0.8409 |
| NAO_EMERGENCIA | 24 | 0.8333 | 0.6250 | 0.7143 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 37 | 3 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 9 | 15 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 0.67 |
| Respostas com ao menos uma citação | 0.621 |
| Linhas em que nada passou de 0,70 | 0.909 |
| Score máximo médio | 0.6403 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.001 |
| retrieval_s | 4.045 | 2.531 | 10.138 |
| generation_s | 32.145 | 28.726 | 44.979 |
| total_s | 36.191 | 32.321 | 54.922 |
| client_s | 40.996 | 32.344 | 92.302 |

Excluídas 11 linha(s) que pagaram o carregamento do modelo.
