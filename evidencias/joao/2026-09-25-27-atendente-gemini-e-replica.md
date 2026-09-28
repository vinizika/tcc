# O Gemini como atendente, e a réplica completa

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2 · **Rodada:** 26 ·
**Commits:** este

> Última rodada de código e o teste que diz se a implementação está pronta:
> **o runner do time, pela API, reproduz os números da autópsia**, com os três
> atendentes. Implementa a decisão de produto do João (25/09): o Gemini
> (`gemini-3.5-flash-lite`) é o atendente padrão; o `qwen3:8b` e o
> `llama3.2:3b` ficam como opções; o sistema nunca troca de modelo em silêncio.

## O que foi feito

1. **O cliente do Gemini como atendente** (`gemini_llm_client.py`), com a
   mesma interface do cliente do Ollama: saída por esquema JSON, temperatura e
   seed, espaçamento entre chamadas, espera crescente no limite por minuto
   (429) e na falta de capacidade do servidor (503), e a cota do dia esgotada
   como erro explícito. **Ele nunca chama o Ollama.** A resposta registra a
   versão do modelo que a API devolve. Testes sem rede.
2. **O provedor do atendente selecionável** por configuração
   (`ATTENDANT_PROVIDER`, padrão `gemini`) e por requisição, com o modelo local
   por requisição (`llm_model`). O atendente é escolhido a cada chamada.
3. **Sem troca silenciosa.** Se o atendente falha e a troca não foi permitida
   (`ATTENDANT_FALLBACK = "none"`, o padrão), a API responde **503** com o
   código (`attendant_unavailable` ou `quota_exhausted`), o provedor, o modelo e
   o motivo. Se a troca foi permitida (`ATTENDANT_FALLBACK = "ollama"`), a
   resposta vem pelo Ollama **e diz isso**: `fallback_from` na procedência e um
   aviso no texto.
4. **O runner** aceita `attendant_provider` e `llm_model`, para na cota
   esgotada com a dica de `--resume`, e conta as linhas respondidas por troca.
5. **Os presets explícitos**: `producao`, `local_qwen`, `local_llama`,
   `fichas_com_porta_0_72`, `fichas_tradutor`, `hoje_academico_llama` e
   `hoje_academico_llama_tradutor`, além do `legacy`.
6. **A réplica**, pela API, promovida a `cited/`.

## Por quê

A rodada 21 terminou dizendo que a implementação só está pronta quando o
runner do repositório, pela API, reproduzir a linha "proposto" da tabela
dentro do ruído. A busca (rodada 24) e o caminho com o qwen no lote `dev`
(rodada 25) já bateram exatos; falta o atendente padrão e os lotes inteiros.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Gemini padrão, sem troca por padrão | Decisão de produto do João, com a condição "nunca trocar em silêncio" ([rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md)) |
| Sem chave do Gemini, a API responde 503 em vez de cair no Ollama | É a mesma regra: um clone sem chave precisa saber que o atendente é outro. Quem quer rodar local escolhe `ATTENDANT_PROVIDER=ollama` ou o preset `local_qwen` |
| `LLM_MODEL = "qwen3:8b"` | É o modelo local da arquitetura; o llama continua pelo preset `local_llama` |
| Com a troca permitida, o aviso vai no texto da resposta, além da procedência | O tutor e o avaliador têm de ver que respondeu outro modelo |
| A cota esgotada para a rodada do runner | Uma rodada com metade das linhas em erro não é medição; `--resume` continua de onde parou |
| Rotação de contas do Gemini: **uma chave por processo da API**, rótulo no manifesto, nunca a chave | Combinado com o João; a cota gratuita é de 500 chamadas por dia e por conta |

## Resultado esperado

_Escrito antes de rodar._ Emergências perdidas · falsos alarmes (a semântica
da autópsia: perdida inclui INCERTO):

| # | Rodada | Esperado (autópsia) | Tolerância |
|---|---|---|---|
| R2 | `producao` (Gemini): prova + régua / relatos independentes / piloto / tom | 2 · 1 / 6 · 3 / 0 · 3 / 3 | ±1 em tudo; mesma resposta em ≥ 99% dos casos numa repetição |
| R2 | Gemini sem busca: prova + régua / independentes | 0 · 3 / 5 · 10 | ±1 |
| R3 | `local_qwen`: prova + régua / independentes / piloto / tom | 2 · 1 / 5 · 7 / 0 · 3 / 4 | ±1 / ±2 / ±1 / ±1; mesma resposta que a autópsia em ≥ 97% dos casos |
| R4 | `local_qwen` sem busca: prova + régua / independentes | 7 · 0 / 21 · 9 | ±1 / ±2 |
| R5 | `hoje_academico_llama` (coleção acadêmica ativa, MiniLM, porta): prova + régua, tradutor desligado / ligado | 15 · 4 / 8 · 3 | ±2 (se sobrar tempo) |

Se um número estourar: conferir, nesta ordem, a busca, o hash do prompt e do
molde, o digest do modelo, o `think`, o `num_ctx` e o que veio do ambiente,
antes de suspeitar do código.

## Resultado obtido

**A implementação reproduz a autópsia.** Pela API, com o runner do time, o
Gemini e o qwen deram **a mesma resposta que a autópsia em todos os casos** de
todos os lotes, com e sem busca, e o Gemini repetiu a si mesmo em 50 de 50
casos numa segunda rodada, com outra conta. O sistema de hoje com o tradutor desligado
também reproduz (15 · 4, 132 de 134 iguais). O único braço fora da tolerância é
o sistema de hoje **com o tradutor ligado** (11 · 3 contra 8 · 3), e a causa
está na etapa de consulta, não no código novo (observação 1).

**A réplica** (emergências perdidas · falsos alarmes, na semântica da
autópsia; "mesma resposta" compara a classe caso a caso com os arquivos da
autópsia):

| # | Configuração · lote | Autópsia | Runner, pela API | Mesma resposta | Dentro? |
|---|---|---|---|---|---|
| R2 | **Gemini** (`producao`) · prova + régua (134) | 2 · 1 | **2 · 1** | 134/134 | ✅ |
| R2 | Gemini · relatos independentes (122) | 6 · 3 | **6 · 3** | 122/122 | ✅ |
| R2 | Gemini · piloto da prova 2 (40) | 0 · 3 | **0 · 3** | 40/40 | ✅ |
| R2 | Gemini · tom calmo (74 emergências) | 3 | **3** | 74/74 | ✅ |
| R2 | Gemini sem busca · prova + régua | 0 · 3 | **0 · 3** | 134/134 | ✅ |
| R2 | Gemini sem busca · independentes | 5 · 10 | **5 · 10** | 122/122 | ✅ |
| R2 | Gemini, repetição do `dev` (50), outra conta, 50 min depois | 1 · 0 (a 1ª rodada) | **1 · 0** | **50/50 com a 1ª** (e a justificativa idêntica em 50/50) | ✅ (≥ 99%) |
| R3 | **qwen** (`local_qwen`) · prova + régua | 2 · 1 | **2 · 1** | 134/134 | ✅ |
| R3 | qwen · independentes | 5 · 7 | **5 · 7** | 122/122 | ✅ |
| R3 | qwen · piloto | 0 · 3 | **0 · 3** | 40/40 | ✅ |
| R3 | qwen · tom | 4 | **4** | 74/74 | ✅ |
| R3 | qwen, código final (API desta rodada) · `dev` / tom | 1 · 0 / 4 | **1 · 0 / 4** | 50/50 · 74/74 | ✅ |
| R4 | qwen sem busca · prova + régua | 7 · 0 | **7 · 0** | 134/134 | ✅ |
| R4 | qwen sem busca · independentes | 21 · 9 | **21 · 9** | 122/122 | ✅ |
| R5 | Hoje (`hoje_academico_llama`), tradutor desligado · prova + régua | 15 · 4 | **15 · 4** | 132/134 | ✅ (±2) |
| R5 | Hoje, tradutor ligado (`hoje_academico_llama_tradutor`) · prova + régua | 8 · 3 | **11 · 3** | 129/134 | ❌ (+3; tolerância ±2) |

Prova + régua = `dev` (50) + calibração (18) + régua (66); 74 emergências e 58
leves. Os relatos independentes e o piloto são diagnóstico, não prova
([rodada 22](2026-09-25-23-preparacao-da-implementacao.md)).

**Quem respondeu** (a procedência de cada linha, contada no arquivo de
previsões):

| Rodadas | Atendente | Versão do modelo | Troca de modelo | Etapa de consulta | Tempo por caso, mediana · p95 |
|---|---|---|---|---|---|
| R2 (Gemini) | `gemini` em todas as linhas | `gemini-3.5-flash-lite` | 0 | não roda | ~4,0 s · 5 a 10 s (o espaçamento de 4 s entre chamadas domina; observação 4) |
| R3/R4 (qwen) | `ollama` | digest `500a1f06…` | 0 | não roda | 2,7 s · 3,0 s (sem busca: 2,1 s) |
| R5 (hoje) | `ollama` | digest `a80c4f17…` (o da autópsia) | 0 | tradutor ligado: reescrita e multi-query pelo **Ollama, com a queda do Gemini registrada** em 134/134; HyDE **nenhum** | 1,3 s (tradutor: 2,5 s) |

**Sem chave, a API recusa em vez de trocar** (checagem funcional, API da
branch sem `GEMINI_API_KEY`, relato "meu cachorro comeu chocolate há uma hora e
está tremendo"):

```
ATTENDANT_FALLBACK=none   → HTTP 503
{"error": "AttendantUnavailableException", "code": "attendant_unavailable",
 "message": "GEMINI_API_KEY não configurada: o atendente padrão é o Gemini. Defina a chave no .env ou escolha o atendente local (ATTENDANT_PROVIDER=ollama ou o preset local_qwen).",
 "details": {"provider": "gemini", "model": "gemini-3.5-flash-lite", "reason": "missing_api_key"}}

ATTENDANT_FALLBACK=ollama → HTTP 200, EMERGENCIA
"attendant": {"provider": "ollama", "model": "qwen3:8b", "thinking": false,
              "fallback_from": "gemini:gemini-3.5-flash-lite"}
…
- Intoxicação por chocolate — fonte: Household Food Items Toxic to Dogs and Cats (Frontiers in Veterinary Science, 2016). <https://doi.org/10.3389/fvets.2016.00026>
…
_Aviso: o atendente configurado (gemini:gemini-3.5-flash-lite) não respondeu; esta resposta veio do modelo local qwen3:8b._
```

**Comandos** (as filas estão no diário da noite; cada linha é uma rodada):

```
$ python scripts/run_evaluation.py --api-url http://127.0.0.1:8000 --name r2_gemini_dev_conta1 \
    --cases data/prova/casos_oficiais.csv --split dev --preset producao
$ python scripts/run_evaluation.py ... --cases data/diagnostico/relatos_independentes.csv --preset producao
$ python scripts/run_evaluation.py ... --preset producao --set retrieval_enabled=false      # sem busca
$ python scripts/run_evaluation.py ... --preset local_qwen                                 # R3
$ python scripts/run_evaluation.py --api-url http://127.0.0.1:8001 ... --preset hoje_academico_llama   # R5
```

O R5 rodou numa segunda API (porta 8001) sobre uma **cópia** do Chroma com a
coleção acadêmica `…388f518d` ativa, sem chave do Gemini, como um clone de
24/09 rodava; a coleção versionada do repositório não foi tocada.

**As rodadas citadas** (`data/evaluation/cited/`, uma por lote; o relatório
de cada uma está no `report.md` da pasta):

| Grupo | Rodadas |
|---|---|
| R2 Gemini | `20260925-040612_r2_gemini_dev_conta1`, `…041000_r2_gemini_calib_conta1`, `…041117_r2_gemini_regua_conta1`, `…041607_r2_gemini_indep_conta1`, `…042504_r2_gemini_piloto_conta1`, `…042809_r2_gemini_tom_conta1` |
| R2 Gemini sem busca | `…043411_r2_gemini_sembusca_dev_conta1`, `…043752_r2_gemini_sembusca_calib_conta1`, `…043909_r2_gemini_sembusca_regua_conta1`, `…044447_r2_gemini_sembusca_indep_conta2` |
| R2 repetição | `…045411_r2_gemini_rep_dev_conta2` |
| R3 qwen | `20260925-032957_n4_qwen_dev_fichas` (a da [rodada 25](2026-09-25-26-resposta-com-ficha-e-fonte.md)), `…033444_r3_qwen_calib`, `…033537_r3_qwen_regua`, `…033839_r3_qwen_indep`, `…034418_r3_qwen_piloto`, `…034628_r3_qwen_tom`, `…040616_r3_qwen_final_dev`, `…040837_r3_qwen_final_tom` |
| R4 qwen sem busca | `…034956_r4_qwen_sembusca_dev`, `…035147_r4_qwen_sembusca_calib`, `…035230_r4_qwen_sembusca_regua`, `…035453_r4_qwen_sembusca_indep` |
| R5 hoje | `…041259_r5_hoje_academico_llama_dev`, `…041415_…_calib`, `…041445_…_regua`; com o tradutor: `…041622_r5_hoje_academico_llama_tradutor_dev`, `…041837_…_calib`, `…041929_…_regua` |

Exemplo do trecho do `cite`:

Rodada [`20260925-041607_r2_gemini_indep_conta1`](../../data/evaluation/cited/20260925-041607_r2_gemini_indep_conta1/report.md) · preset `producao` · 122 linhas · acurácia balanceada 0.8844, estrita 0.8934, 1 falso(s) não urgente(s).

**Suíte:** backend 284 → **285** (o teste do link, abaixo); scripts **216**;
`mock/` 10; `sync_fichas.py --check` e `sync_retrieval_terms.py --check`
limpos.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/clients/gemini_common.py`, `gemini_llm_client.py` | **novos**: o Gemini como atendente (esquema JSON, temperatura, seed, espaçamento, recuo em 429/503, cota como erro, versão do modelo); nunca chama o Ollama. No fechamento, só a mensagem de log da espera do 503 |
| `backend/app/exceptions/attendant_exception.py`, `exceptions/handlers.py`, `schemas/error.py` | **novo**: o 503 com `code` e `details` (`attendant_unavailable`, `quota_exhausted`) |
| `backend/app/core/config.py` | `ATTENDANT_PROVIDER="gemini"`, `ATTENDANT_FALLBACK="none"`, `LLM_MODEL="qwen3:8b"`, `GEMINI_TIMEOUT_S`, `GEMINI_MIN_INTERVAL_S`, `GEMINI_MAX_RETRIES_429/503` |
| `backend/app/schemas/triage.py`, `pipeline/config_resolver.py` | `attendant_provider` e `llm_model` por requisição |
| `backend/app/pipeline/chat_pipeline.py`, `clients/llm_client.py` | o atendente escolhido a cada chamada; a falha vira 503, ou a troca com `fallback_from` e aviso |
| `backend/app/pipeline/answer_renderer.py` | o endereço da fonte sai como link (`<https://…>`); o que não é `http(s)://` continua escapado (achado na checagem funcional desta rodada; adendo na [rodada 25](2026-09-25-26-resposta-com-ficha-e-fonte.md)) |
| `backend/app/services/fingerprint_service.py` | bloco `attendant` (provedor, troca, modelo do Gemini, chave configurada ou não, espaçamento) |
| `backend/tests/test_gemini_atendente.py` (**novo**), `test_resposta_procedencia.py`, `test_chat_pipeline.py`, `conftest.py` | o cliente sem rede, o 503, a troca declarada, o link |
| `scripts/run_evaluation.py`, `scripts/tests/test_run_evaluation_cases.py` | `attendant_provider` e `llm_model` nas opções; para na cota com a dica do `--resume`; `attendant_fallback_lines` no manifesto |
| `scripts/presets.json` | `producao`, `local_qwen`, `local_llama`, `fichas_com_porta_0_72`, `fichas_tradutor`, `hoje_academico_llama`, `hoje_academico_llama_tradutor` |
| `scripts/montar_lote_tom.py`, `data/diagnostico/tom_calmo.csv` | **novos**: o lote do tom (74 emergências contadas com calma), montado dos relatos da autópsia |
| `data/evaluation/cited/…` | as rodadas da réplica |

Commits: `d7c87df` (abre a rodada, com o código) e este.

## Observações

**1. Por que o braço "hoje, tradutor ligado" não reproduz.** Dois motivos, os
dois na etapa de consulta:
- **O braço da autópsia não é o que o sistema roda sem chave.** Na rodada 17,
  o "tradutor ligado" usou reescrita, multi-query **e HyDE** gerados pelo llama
  (`_trabalho/tradutor/llama.jsonl`: HyDE em 134 de 134). O sistema sem a chave
  do Gemini **descarta o HyDE** (a queda da etapa não tem substituto local), e
  o runner mostra isso: `hyde: nenhum` em 134 de 134. A
  [rodada 17](2026-09-24-18-tradutor-desligado.md) descreve o braço certo
  ("gerados pelo llama"); o que não bate é a expectativa de que o preset o
  reproduzisse.
- **A reescrita do `llama3.2:3b` não é estável.** Com temperatura 0 e seed 42,
  gerada de novo isolada, **6 de 16 reescritas mudaram entre duas chamadas
  seguidas**; e a de hoje difere da de 24/09 em 61 de 134 casos (a de hoje bate
  com a do runner em 15 de 16). É o ruído de GPU da
  [rodada 5](2026-09-05-06-determinismo-da-consulta.md), que cresce com o
  tamanho da geração.

A classificação em si segue a autópsia: com o tradutor desligado, a mesma
resposta em 132 de 134; ligado, 129 de 134, e as 5 diferenças vêm de consultas
diferentes. Isso não pesa na arquitetura, em que o tradutor é braço da
ablação; pesa na ablação ([B-66](../backlog.md#b-66)): as consultas precisam ser
geradas uma vez, guardadas e dadas a todos os braços que as usam.

**2. O tipo de erro também se repete.** As emergências que o Gemini perde são
**INCERTO**: 2 de 2 na prova + régua (`p41`, `b34`), 5 de 6 nos independentes
(os mesmos casos da [rodada 18](2026-09-24-19-atendente-llama-qwen-gemini.md)),
3 de 3 no tom. As do qwen são **NÃO EMERGÊNCIA** (todas). Por isso o relatório
do runner, que não conta INCERTO como falso não urgente
([B-60](../backlog.md#b-60)), mostra 0 para o Gemini onde a tabela acima mostra
2: as duas leituras estão certas, e a tabela usa a da autópsia.

**3. O código mediu com o que estava na API.** As filas R3/R4 do qwen rodaram
contra a API das 03h29 (código da [rodada 25](2026-09-25-26-resposta-com-ficha-e-fonte.md));
o caminho do Ollama nesta rodada chama o mesmo `LLMClient`, e o `dev` e o tom
rodaram de novo com o código final (`local_qwen`, mesmas respostas). As
rodadas R3 da API anterior usam o preset `naive_rag` com `retrieval_mode=vector`
e `context_min_score=0.0` (o `local_qwen` ainda não existia), que é a mesma
configuração; as R4, o `llm_only`. O
`git.sha` do manifesto é o HEAD do momento (`b277fa6` a `fe11b99`); depois de
`d7c87df` só mudaram dados e scripts da prova 2. O `dirty` é a documentação da
rodada 29 e os binários do Chroma ([B-73](../backlog.md#b-73)). A correção do
link veio depois da réplica e não muda a classificação (o runner lê o JSON da
triagem, não o texto).

**4. O tempo do Gemini é quase todo espera nossa.** O cliente espaça as
chamadas em 4 s (`GEMINI_MIN_INTERVAL_S`) para uma rodada inteira não esbarrar
no limite por minuto da conta gratuita; por isso a mediana de ~4 s. Numa
pergunta avulsa, o espaçamento não pesa ([B-65](../backlog.md#b-65)).

**5. Contas do Gemini.** A conta 1 (a do João) respondeu do `dev` até a linha
`b49` da régua sem busca: 487 linhas, a partir das 04h06, depois da virada da
cota. A cota acabou às 04h42, e o runner parou limpo, com as 49 linhas
gravadas. A API foi reiniciada com a conta 2 (uma chave por processo) e a
mesma rodada retomada com `--resume` (`b50` a `b66`); o resto da fila rodou pela
conta 2. O rótulo da conta está no nome da rodada (`_conta1`, `_conta2`; a
régua sem busca leva `_conta1` por ter começado nela) e no log da fila. A
chave nunca foi para o manifesto, que registra só `gemini_key_configured: true`
e o nome da variável em `overridden_by_env`. Novas tentativas: nenhuma na
conta 1 até a cota acabar; na conta 2, uma espera por limite por minuto (429,
5 s) e uma por falta de capacidade (503, 20 s), em 189 linhas. O log escrevia
"Gemini 503xx"; corrigido para "Gemini 503".

**6. Ollama 0.34.4** nesta máquina (a autópsia registrou 0.34.3). O digest do
llama é o que a autópsia registrou (`a80c4f17…`); o do qwen a autópsia não
registrou, e a réplica caso a caso (100%) é a melhor indicação de que é o
mesmo modelo. Daqui em diante, o digest vai em cada linha da previsão.

## Deixado para depois

- **O "Respondido por" na tela e o 503 no frontend** ([B-74](../backlog.md#b-74)).
- **As consultas do tradutor guardadas e reusadas na ablação**, com o HyDE
  declarado ([B-66](../backlog.md#b-66)).
- **LGPD com o Gemini padrão** ([B-64](../backlog.md#b-64)): o aviso ao tutor e a
  opção "só local" antes de qualquer uso com tutores de verdade.

## Próximo passo

A [rodada 29](2026-09-25-30-fechamento-da-rodada-noturna.md): a documentação
de uso, o backlog e o planejamento com o sistema que o código roda. Depois,
com o João: a prova 2 até o uso ([B-63](../backlog.md#b-63)).
