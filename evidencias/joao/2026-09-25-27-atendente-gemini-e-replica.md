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

_(preenchido ao fechar a rodada)_

## O que mudou no repositório

_(preenchido ao fechar a rodada)_

## Observações

_(preenchido ao fechar a rodada)_

## Deixado para depois

_(preenchido ao fechar a rodada)_

## Próximo passo

_(preenchido ao fechar a rodada)_
