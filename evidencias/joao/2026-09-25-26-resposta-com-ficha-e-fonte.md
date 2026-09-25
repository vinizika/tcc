# A resposta: a ficha, a fonte real e quem respondeu

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2 (a etapa de consulta é do
B1) · **Rodada:** 25 · **Commits:** este

> Terceira rodada de código. Muda o que sai do pipeline, não o que entra no
> modelo: o bloco de contexto do prompt continua byte a byte o mesmo, para a
> réplica valer. O portão é o primeiro teste do caminho inteiro pela API, com
> o qwen, no lote `dev` da prova 1.

## O que foi feito

1. **A citação ao tutor.** "Baseado em" passa a mostrar a ficha usada e o
   documento aprovado por trás dela, com o título real, o periódico, o ano e o
   DOI: `- <ficha> — fonte: <título real> (<periódico>, <ano>). <doi>`. As
   referências vêm de `backend/data/fichas.json` (rodada 23) pela coleção
   (rodada 24), e a API as devolve em cada fonte.
2. **O corte de 4.000 caracteres para de mentir.** Hoje, um trecho que não
   coube no bloco de contexto continua listado como fonte e contado como
   usado. Agora a fonte, a contagem e o índice que o modelo pode citar vêm só
   dos trechos que entraram no prompt. O bloco em si não muda.
3. **A procedência na resposta**, fora da configuração: provedor, modelo,
   versão (o digest, no Ollama) e se o modelo "pensou", para o atendente; e,
   para a etapa de consulta, qual provedor respondeu cada etapa, **inclusive
   quando o Gemini caiu para o Ollama** — hoje essa queda é silenciosa. O
   runner grava tudo em cada linha.
4. **O `think` do qwen configurável** (`LLM_THINK`, padrão falso, e por
   requisição): o qwen3 "pensa" antes de responder se ninguém disser que não,
   e a autópsia mediu o qwen sem pensar.
5. **O retrato da API** ganha o `think`, o hash do formato do bloco de
   contexto, o modelo do Gemini e a lista de configurações que vieram do
   ambiente (só os nomes).
6. **`run_evaluation.py --cases <csv> [--split …]`**: o runner do time passa a
   rodar qualquer lote no formato da prova (`id`, `text`, `expected_class`),
   com o sha256 do arquivo no manifesto e a conferência do congelamento quando
   o lote tem `.freeze.json`. Sem `--cases`, faz exatamente o que fazia.

## Por quê

- **A citação era o defeito dos títulos genéricos**
  ([rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md#6-os-títulos-genéricos)):
  o tutor lia "Feline abscess case" como fonte.
- **O corte de 4.000 caracteres** foi achado na autópsia
  ([rodada 14](2026-09-23-15-autopsia-do-sistema-de-hoje.md)). Com as 3 fichas
  (~1.800 caracteres) ele não dispara; com a base acadêmica, pode.
- **Sem procedência, "nunca trocar de modelo em silêncio" não é verificável**
  ([rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md)). É condição da
  decisão do João pelo Gemini, que entra na rodada 26.
- **Sem `think=false`, o qwen do código não é o qwen medido.**
- **Sem `--cases`, a réplica não roda pelo runner do time**: ele só conhecia o
  conjunto antigo em inglês.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| O bloco de contexto (cabeçalho, numeração, título + texto) fica idêntico | Paridade com a autópsia. Mudar o cabeçalho "Trechos de protocolos veterinários" é rodada medida |
| O trecho cortado pela metade conta como visto; o que não entrou nada, não | O modelo leu parte dele e pode citá-lo; o outro ele não viu |
| `think` padrão falso | O qwen medido não pensava; o llama ignora o parâmetro (conferido no Ollama desta máquina) |
| A procedência da consulta registra a queda Gemini → Ollama, mas **não** a elimina | Mudar o comportamento da etapa de consulta é decisão do trilho B1; aqui ela só deixa de ser invisível |
| `row_id` é o `id` do caso (texto) no modo `--cases` | Os casos da prova têm id textual (`p19`, `i37`); o modo antigo continua com o índice numérico |

## Resultado esperado

_Escrito antes de rodar._

- **Suíte** verde, com testes novos: a citação com referência, o corte que
  deixa de listar o trecho não visto, a procedência, o `think` chegando ao
  Ollama, o `--cases` e a conferência do congelamento.
- **Portão**: o qwen (`qwen3:8b`, `think=false`, GPU) pela API, no lote `dev`
  da prova 1 (50 casos), com as fichas: emergências perdidas e falsos alarmes
  iguais aos da autópsia no mesmo lote (`ctxarq_bgecl_leitura_mapa_top3 × dev
  × qwen3-8b`), com tolerância de ±1, e as mesmas respostas em pelo menos 97%
  dos casos.
- **"Baseado em"** mostra a ficha e o título real.

## Resultado obtido

**O caminho inteiro, pela API, reproduz a autópsia: 50 de 50 respostas
iguais.**

**Portão** (API local, `LLM_MODEL=qwen3:8b`, `think=false`, GPU; Ollama
0.34.4; digest do qwen `500a1f06…`):

```
$ python scripts/run_evaluation.py --cases data/prova/casos_oficiais.csv --split dev \
    --preset naive_rag --set retrieval_mode=vector --set context_min_score=0.0 --name n4_qwen_dev_fichas
```

Rodada [`20260925-032957_n4_qwen_dev_fichas`](../../data/evaluation/cited/20260925-032957_n4_qwen_dev_fichas/report.md) · preset `naive_rag` · 50 linhas · acurácia balanceada 0.9800, estrita 0.9600, 1 falso(s) não urgente(s).

| Lote `dev` da prova 1 (25 emergências, 24 leves, 1 INCERTO) | Autópsia (`ctxarq_bgecl_leitura_mapa_top3`, qwen) | Runner, pela API |
|---|---|---|
| Emergências perdidas · falsos alarmes | 1 · 0 | **1 · 0** |
| Mesma resposta, caso a caso | — | **50 de 50** |
| Fichas no prompt | as 3 da busca | as mesmas 3 (a busca já tinha batido 296/296 na rodada 24) |
| Tempo por caso (mediana) | 2,6 s | 2,7 s |

**A resposta ao tutor** (relato "meu cachorro comeu uma barra de chocolate
meio amargo agora e está agitado, tremendo", qwen):

```
**Baseado em**

- Intoxicação por chocolate — fonte: Household Food Items Toxic to Dogs and Cats (Frontiers in Veterinary Science, 2016). https\://doi.org/10.3389/fvets.2016.00026
```

e a procedência que volta junto:

```json
{"attendant": {"provider": "ollama", "model": "qwen3:8b",
  "model_version": "500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41",
  "thinking": false, "fallback_from": null},
 "query_stage": {"rewriting": false, "multi_query": false, "hyde": false, "calls": []}}
```

**Suíte:** backend 262 → **271**; scripts 209 → **214**.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/schemas/triage_output.py` | `SourceReference`; `CitedSource.display_title` e `.references` |
| `backend/app/models/retrieved_document.py`, `backend/app/clients/retrieval_client.py` | o documento traz `display_title` e as referências do metadado |
| `backend/app/pipeline/answer_renderer.py` | "Baseado em": ficha — fonte: título real (periódico, ano). DOI |
| `backend/app/prompts/triage.py` | `documentos_que_cabem()`; o bloco não muda |
| `backend/app/pipeline/chat_pipeline.py` | fontes, contagem e citação só do que coube; `think` ao atendente; procedência; rastro da consulta nas threads |
| `backend/app/clients/llm_client.py` | `think`; `provider`, `model`, `model_version` (digest), `thinking` no resultado |
| `backend/app/clients/hybrid_query_client.py` | rastro de cada chamada da consulta, com a queda do Gemini (trilho B1: o comportamento não muda) |
| `backend/app/schemas/triage.py`, `schemas/chat.py`, `pipeline/result.py`, `services/chat_service.py` | `think` nas opções e na configuração; `Provenance`; a fonte da API com tópico, nome da ficha e referências |
| `backend/app/core/config.py`, `pipeline/config_resolver.py` | `LLM_THINK` (padrão falso) |
| `backend/app/services/fingerprint_service.py` | `think`, `gemini_model`, `context_block_sha256`, `overridden_by_env` |
| `scripts/run_evaluation.py` | `--cases`/`--split`, `think` nas opções válidas, procedência e tópicos usados em cada linha |
| `backend/tests/test_resposta_procedencia.py`, `scripts/tests/test_run_evaluation_cases.py` | **novos**: 9 + 5 testes |
| `data/evaluation/cited/20260925-032957_n4_qwen_dev_fichas/` | a rodada do portão |

Commits: `a8e7680` (abre a rodada, com o código) e este.

## Observações

**1. O "falso não urgente" do runner não conta INCERTO**
([B-60](../backlog.md#b-60)). Aqui dá no mesmo (1 = 1), mas nos lotes com
INCERTO os números do relatório do runner e os da autópsia divergem; as
tabelas da réplica usam a semântica da autópsia (emergência perdida inclui
INCERTO e saída inválida).

**2. O DOI aparece com a barra do escape** (`https\://…`) no texto cru: o
`escapar()` neutraliza os dois-pontos, que no Streamlit viram diretiva. Na
tela, renderizado como markdown, sai `https://…`.

**3. O `think=false` é mandado também ao llama**, que o ignora (conferido no
Ollama 0.34.4). Se um dia o Ollama passar a recusar o parâmetro em modelos
sem raciocínio, `LLM_THINK=` (vazio) volta a não mandar nada.

**4. A etapa de consulta não recebe `think`.** Ela está desligada por padrão;
quando ligada com um qwen, precisaria do mesmo parâmetro (fica anotado).

## Deixado para depois

- **As contradições da documentação** (`docs/CONTRATOS.md`, docstring do
  `gemini_query_client.py`, `.env.example`, README): vão com a rodada 29.
- **`think` na etapa de consulta**, se ela voltar a ser usada com o qwen.
- **O "Respondido por" na tela** do frontend, a partir da procedência (a API já
  devolve).

## Próximo passo

A [rodada 26](2026-09-25-27-atendente-gemini-e-replica.md): o cliente do
Gemini como atendente, o provedor selecionável sem troca silenciosa, e a
réplica completa (Gemini, qwen e o sistema de hoje).

## Adendo (25/09, 04h40)

A observação 2 estava incompleta: renderizado como markdown, `https\://…` sai
com o texto certo, mas **deixa de ser link**. Corrigido na
[rodada 26](2026-09-25-27-atendente-gemini-e-replica.md): o endereço que vem do
sidecar e tem cara de `http(s)://` sai como link automático (`<https://…>`);
o resto continua escapado. O teste desta rodada, que travava a forma escapada,
mudou junto.
