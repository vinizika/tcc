# Resultados da autópsia 2 (23 e 24/09/2026)

Os dados que sustentam os números das rodadas 14 a 21 do trilho B2
(`evidencias/joao/2026-09-23-15-…` a `2026-09-24-22-…`). Eles não saíram do
runner de avaliação do repositório. Saíram de um **executor da autópsia**, que
chama por dentro o próprio código do pipeline de `fceab20`
(`ChatPipeline._build_queries`, `_retrieve`, `_classify`), sem servidor HTTP,
para poder trocar só o que entra no prompt (nenhum trecho, os trechos da busca
de hoje, o trecho certo, uma ou três fichas).

- **Conferência contra o runner:** 18 de 18 previsões iguais na calibração, com
  e sem RAG, com o mesmo número de trechos.
- **Onde está o executor:** fora do repositório, no registro local da autópsia.
  Ele depende de caminhos daquela máquina.
- **A réplica pelo runner, pela API**, é parte da implementação da autópsia. Os
  números dela vão para `data/evaluation/cited/`, como toda rodada citada.

As rodadas que **saíram** dos runners do repositório (tarde de 23/09) estão nas
pastas de cada runner: `data/evaluation/cited/20260923-*_autopsia_*`,
`data/evaluation/prova_runs/20260923-*_autopsia_*` e
`data/retrieval/cited/20260923-175254_autopsia_candidata_3481`.

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `resultados_por_caso.csv` | uma linha por caso, em cada condição citada nas rodadas 14 a 21 (106 combinações de condição e atendente, 15.798 linhas) |
| `justificativas_citadas.csv` | a justificativa do atendente, caso a caso, nas condições cuja leitura qualitativa as evidências citam |
| `busca/` | as buscas sem modelo de linguagem: os seis embeddings nas fichas do mapa e na base acadêmica (`embed_*.json`, com o top 5 de cada caso), a busca em cada base de fichas (`busca_fichas.json`), a busca de produção com o bge-m3 (`producao_bge_*.json`), as âncoras (`ancoras_*.json`) e os títulos (`titulos.json`) |
| `tradutor/tradutor_por_caso.csv` | as saídas da reescrita, do multi-query e do HyDE, caso a caso, com o llama (134 casos × 5 saídas) e com o Gemini (50 × 3), mais os três consertos (134 × 4), e o veredito do juiz e das regras do código em cada uma |
| `tradutor/busca_por_variante.csv` | o efeito de cada variante de consulta na busca de hoje e nas fichas |

## As colunas de `resultados_por_caso.csv`

| Coluna | O que é |
|---|---|
| `condicao` | o que o atendente recebeu (tabela abaixo) |
| `lote` | `dev`, `calib` (prova do trilho B1), `regua` (`data/retrieval/cases.csv`), `antigo` (os 98 de 04/09), `indep` e `indep2` (relatos de quem não viu o mapa, `data/diagnostico/relatos_independentes.csv`) e `piloto` (`data/diagnostico/piloto_prova2.csv`) |
| `atendente` | `llama3.2-3b`, `qwen3-8b` (com `think=False`) ou `gemini-3.5-flash-lite` |
| `id`, `topico`, `tom`, `esperado` | o caso, o quadro do mapa, o tom (nos relatos independentes e no piloto) e a classe esperada |
| `previsto` | a resposta do atendente |
| `no_prompt` | os assuntos das fichas ou dos trechos que entraram no prompt, na ordem, separados por `;` (vazio = nada entrou) |
| `tempo_s` | o tempo da chamada ao modelo; no Gemini, sem a espera entre chamadas imposta pela cota |

## As condições

| Condição | O que o atendente recebe |
|---|---|
| `sem_rag` | só o relato |
| `rag_full` | o que a busca de hoje põe no prompt (base acadêmica de 3.481 trechos, MiniLM, roteador, reranker, porta 0,72), com o relato cru |
| `ragtrad_full` | idem, com o tradutor ligado (reescrita, multi-query e HyDE gerados pelo llama) |
| `rag_query_hibrido_full`, `rag_query_ollama_full`, `rag_query_ingles_full` | 23/09: a busca de hoje com o tradutor pelo Ollama (HyDE pulado), com HyDE local, e só com a reescrita em inglês |
| `oraculo_academico`, `oraculo_academico_pt`, `oraculo_tutor` | os trechos acadêmicos do assunto certo; os mesmos traduzidos; os textos para tutor reais que existem |
| `oraculo_ficha`, `ficha_gemea` | a ficha do mapa do assunto certo; só a ficha da gêmea |
| `ctxarq_oraculo_fichassc` | a ficha do mapa certa, sem a linha de conduta |
| `e5_fichas_top1`, `e5_fichas_top3`, `e5_fichas_top1_gemea` | a ficha do mapa mais próxima pelo e5-base; as 3 mais próximas; a mais próxima + a gêmea |
| `rag_fichas_top3` | as 3 primeiras fichas pela busca de produção (MiniLM) |
| `ctxarq_bge_fichas_top1`, `ctxarq_bge_fichas_top3` | pelo bge-m3: a ficha do mapa mais próxima; as 3 mais próximas, sem porta |
| `ctxarq_bgeprod_fichas`, `ctxarq_bgeprod_fichase1` | bge-m3 na busca de produção, com a porta 0,72 (a "porta de confiança"); idem, só com as fichas da etapa 1 |
| `e5_fichasia_top1`, `e5_fichasiaen_top1`, `oraculo_fichaia` | a ficha escrita pelo autor barato (madrugada de 24/09), em português e em inglês; a certa |
| `ctxarq_bge_fichashib2_top3` | 3 fichas; ficha do mapa na etapa 1 e ficha-IA na etapa 2 |
| `ctxarq_bge_fichascl_top3`, `ctxarq_bge_fichashibcl_top3`, `ctxarq_oraculo_fichascl` | as fichas do Claude, lidas inteiras: 3 mais próximas; a híbrida; a certa |
| `ctxarq_bgecl_leitura_mapa_top3` | **a configuração proposta**: busca nas fichas do Claude, as 3 mais próximas, leitura na ficha do mapa |
| `ctxarq_bgecl_leitura_curta_top3` | idem, leitura na ficha do Claude curta |
| `ctxarq_bgecl_trad_leitura_mapa_top3` | a configuração proposta com o tradutor ligado |
| `ctxarq_bge_fichasp_top3`, `ctxarq_bge_fichasclp_top3` | o mesmo que `ctxarq_bge_fichas_top3` e `ctxarq_bge_fichascl_top3`, no piloto |
| `cue_calmo…` | o teste de tom: só as 74 emergências, com a frase "Mas fora isso continua comendo e brincando normalmente." no fim, e o contexto da condição que vem depois (`cue_calmo` sozinho = sem contexto). `cue_calmo2` a `cue_calmo4` são as outras três frases |
| `…@sinais`, `…@ignora` | o mesmo contexto, com uma regra a mais no prompt: contra o tom; e "ignore o trecho de outro assunto" |
| `cot_…` | o Chain-of-Thought do projeto (`cot_position = first`) |
| `sem_rag_rep2`, `sem_rag_repeticao` | repetições do `sem_rag`, para medir a repetibilidade |

## Como recontar qualquer número

Emergência perdida = emergência respondida como NAO_EMERGENCIA ou INCERTO;
falso alarme = caso leve respondido como EMERGENCIA.

```python
import csv
linhas = list(csv.DictReader(open("data/evaluation/autopsia2/resultados_por_caso.csv", encoding="utf-8")))

def conta(condicao, atendente, lotes):
    v = [r for r in linhas if r["condicao"] == condicao and r["atendente"] == atendente and r["lote"] in lotes]
    em = [r for r in v if r["esperado"] == "EMERGENCIA"]
    lv = [r for r in v if r["esperado"] == "NAO_EMERGENCIA"]
    perdidas = sum(r["previsto"] != "EMERGENCIA" for r in em)
    alarmes = sum(r["previsto"] == "EMERGENCIA" for r in lv)
    return f"{perdidas}/{len(em)} perdidas · {alarmes}/{len(lv)} falsos alarmes"

print(conta("ctxarq_bgecl_leitura_mapa_top3", "gemini-3.5-flash-lite", {"indep", "indep2"}))  # 6/76 · 3/46
print(conta("rag_full", "llama3.2-3b", {"indep", "indep2"}))                                # 40/76 · 22/46
```

## Integridade

São cerca de 17.900 linhas de resultado na autópsia inteira; aqui estão as
15.798 das condições citadas. Duas delas são **falha técnica**, em que o modelo
devolveu resposta vazia ou inválida e o pipeline a converteu no INCERTO de
segurança:
- o Gemini sem contexto no caso `pA01` do piloto;
- o llama com o trecho acadêmico certo no caso `p42` do `dev`.

Elas estão contadas como perda, como o sistema faria com o tutor. Uma queda de
energia na noite de 24/09 estragou um bloco de 61 chamadas, que foi descartado e
refeito; todos os outros arquivos foram conferidos. O lote `teste` da prova
nunca foi usado.
