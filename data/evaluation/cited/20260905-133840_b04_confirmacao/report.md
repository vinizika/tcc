# Rodada 20260905-133840_b04_confirmacao

**Preset:** rag_query · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 2

Início 2026-09-05T13:38:40.955579-03:00 · máquina DESKTOP-5UGARQ1 · commit ad7c7b8

## Configuração efetiva

```json
{
  "query_rewriting_enabled": true,
  "multi_query_enabled": true,
  "hyde_enabled": true,
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
| **Acurácia balanceada** | **0.7042** |
| Acurácia estrita | 0.5714 IC95 [0.4726, 0.6649] |
| Cobertura | 0.9796 |
| Acurácia entre as decididas | 0.5833 |
| Macro-F1 | 0.5772 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 40 | 0.563 |
| Falsos urgentes (leve tratado como emergência) | 0 | 0.000 |
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
| EMERGENCIA | 71 | 1.0000 | 0.4085 | 0.5800 |
| NAO_EMERGENCIA | 27 | 0.4030 | 1.0000 | 0.5745 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 29 | 40 | 2 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 27 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| Fontes citadas por resposta | 0.18 |
| Respostas com ao menos uma citação | 0.184 |
| Linhas em que nada passou de 0,70 | 0.643 |
| Score máximo médio | 0.6761 |
| Respostas com citação inválida | 0.000 |

### Estabilidade entre repetições

- Repetições: 2
- Linhas com resposta idêntica em todas: 0.939
- Linhas instáveis: 6
- Acurácia balanceada: média 0.7042, desvio 0.0000, faixa 0.7042–0.7042

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 3.313 | 3.26 | 4.185 |
| retrieval_s | 0.147 | 0.139 | 0.234 |
| generation_s | 2.314 | 2.276 | 2.906 |
| total_s | 5.774 | 5.703 | 6.731 |
| client_s | 5.788 | 5.716 | 6.742 |
