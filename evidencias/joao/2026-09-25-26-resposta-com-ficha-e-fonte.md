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

_(preenchido ao fechar a rodada)_

## O que mudou no repositório

_(preenchido ao fechar a rodada)_

## Observações

_(preenchido ao fechar a rodada)_

## Deixado para depois

_(preenchido ao fechar a rodada)_

## Próximo passo

_(preenchido ao fechar a rodada)_
