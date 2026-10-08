# Rodada 20261007-222308_r23_calib_v2

**Preset:** producao_suficiencia · **Subconjunto:** None · **Linhas:** 66 · **Repetições:** 1

Início 2026-10-07T22:23:08.027120-03:00 · máquina Ryu · commit 6ed671d (com alterações locais)

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
| **Acurácia balanceada** | **0.9792** |
| Acurácia estrita | 0.9848 IC95 [0.919, 0.9973] |
| Cobertura | 0.9545 |
| Acurácia entre as decididas | 1.0000 |
| Macro-F1 | 0.9894 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 0 | 0.000 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
| Abstenções (INCERTO) | — | 0.045 |
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
| EMERGENCIA | 40 | 1.0000 | 1.0000 | 1.0000 |
| NAO_EMERGENCIA | 24 | 1.0000 | 0.9583 | 0.9787 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 40 | 0 | 0 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 23 | 1 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| **Respostas que receberam algum trecho** | 1.000 |
| Respostas em que a busca ficou silenciosa | 0.000 |
| Fontes citadas por resposta | 1.03 |
| Respostas com ao menos uma citação | 0.848 |
| Linhas em que nada passou de 0,70 | 0.909 |
| Score máximo médio | 0.6403 |
| Respostas com citação inválida | 0.000 |

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 0.0 | 0.0 | 0.001 |
| retrieval_s | 1.658 | 1.254 | 3.003 |
| generation_s | 8.082 | 3.138 | 30.015 |
| total_s | 9.74 | 4.255 | 31.703 |
| client_s | 9.806 | 4.328 | 31.783 |
