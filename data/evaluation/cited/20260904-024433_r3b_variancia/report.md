# Rodada 20260904-024433_r3b_variancia

**Preset:** rag_query · **Subconjunto:** full · **Linhas:** 98 · **Repetições:** 3

Início 2026-09-04T02:44:33.226345-03:00 · máquina DESKTOP-5UGARQ1 · commit a95f895 (com alterações locais)

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
| **Acurácia balanceada** | **0.7324** |
| Acurácia estrita | 0.6122 IC95 [0.5133, 0.7027] |
| Cobertura | 0.9796 |
| Acurácia entre as decididas | 0.6250 |
| Macro-F1 | 0.6173 |

### Erros clínicos

| Erro | Contagem | Taxa |
|---|---|---|
| Falsos não urgentes (emergência tratada como leve) | 36 | 0.507 |
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
| EMERGENCIA | 71 | 1.0000 | 0.4648 | 0.6346 |
| NAO_EMERGENCIA | 27 | 0.4286 | 1.0000 | 0.6000 |

### Matriz de confusão

| real ↓ / previsto → | EMERGENCIA | NAO_EMERGENCIA | INCERTO | INVALID_JSON | OTHER |
|---|---|---|---|---|---|
| EMERGENCIA | 33 | 36 | 2 | 0 | 0 |
| NAO_EMERGENCIA | 0 | 27 | 0 | 0 | 0 |

### Ancoragem nos documentos

| Métrica | Valor |
|---|---|
| Fontes citadas por resposta | 0.28 |
| Respostas com ao menos uma citação | 0.276 |
| Linhas em que nada passou de 0,70 | 0.602 |
| Score máximo médio | 0.6797 |
| Respostas com citação inválida | 0.000 |

### Estabilidade entre repetições

- Repetições: 3
- Linhas com resposta idêntica em todas: 0.663
- Linhas instáveis: 33
- Acurácia balanceada: média 0.7007, desvio 0.0288, faixa 0.6628–0.7324

### Tempo de resposta

| Etapa | Média | Mediana | p95 |
|---|---|---|---|
| query_s | 3.52 | 3.463 | 4.342 |
| retrieval_s | 0.166 | 0.142 | 0.309 |
| generation_s | 2.254 | 2.234 | 2.813 |
| total_s | 5.94 | 5.739 | 7.17 |
| client_s | 5.964 | 5.78 | 7.192 |
