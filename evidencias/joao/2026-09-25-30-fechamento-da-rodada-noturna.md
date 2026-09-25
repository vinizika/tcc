# Fechamento da implementação da autópsia 2

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2, olhando o sistema inteiro ·
**Rodada:** 29 · **Commits:** este

> Rodada de **documentação**, sem código de sistema. Fecha a sequência das
> rodadas 22 a 28: a documentação de uso passa a descrever o sistema que o
> código roda, o código morto sai, e o backlog e o planejamento do trilho
> registram o que ficou para depois.

## O que foi feito

1. **README, `.env.example`, `docs/CONTRATOS.md`, `docs/estado-atual.md` e
   `data/retrieval/README.md`** reescritos onde contradiziam o código:
   - o sistema como ele é: relato cru, bge-m3 nas 61 fichas de busca, as 3 mais
     próximas, a ficha de leitura no prompt, o Gemini como atendente padrão, o
     qwen e o llama como opções;
   - como subir: a chave do Gemini (e o 503 sem ela), `ollama pull qwen3:8b`,
     a coleção que já vem versionada, `ingest --profile fichas`;
   - as chaves novas (`retrieval_mode`, `attendant_provider`, `llm_model`,
     `think`), a procedência e o 503 do atendente;
   - contradições antigas: o CoT existe (o contrato dizia "não implementado"),
     o HyDE não está "desligado desde 17/09", o corte padrão não é 0,70, a
     régua tem 66 casos e não 18, a docstring do `gemini_query_client.py`
     dizia "não é chamado por nada em produção".
2. **`frontend/streamlit_app.py` sai** (a interface antiga; o compose sobe o
   `main.py`) — [B-18](../backlog.md#b-18) e [B-19](../backlog.md#b-19).
3. **O backlog, o README e o planejamento do João** com as rodadas 22 a 29.

## Por quê

A documentação de uso descrevia o sistema de 24/09 (llama, MiniLM, porta de
0,72, tradutor ligado), e um clone limpo seguindo o README não chegaria ao
sistema medido. Com a réplica batida, o que está no código é a arquitetura;
a documentação precisa dizer isso.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| O "estado medido" do README passa a ser o da réplica pela API (rodada 26), não o de 04/09 | É o número que o código atual reproduz |
| Só o `frontend/streamlit_app.py` sai; o `mock/` fica | O mock é o protótipo de demonstração, com teste e porta própria |

## Resultado esperado

_Escrito antes de fazer._ Nenhum teste muda; a documentação não contradiz o
código nos pontos listados; o backlog tem um item para cada "deixado para
depois" das rodadas 22 a 28.

## Resultado obtido

**Nenhum teste mudou**: backend 285, scripts 216, `mock/` 10 (os mesmos do fim
da rodada 26); `sync_fichas.py --check` e `sync_retrieval_terms.py --check`
limpos.

**As contradições corrigidas**, uma a uma:

| Onde | Dizia | Diz agora |
|---|---|---|
| `README.md` | llama local, "protocolos recuperados de uma base local", `ollama pull llama3.2:3b`, estado medido de 04/09 | fichas de triagem, Gemini padrão, qwen/llama opções, a chave (e o 503 sem ela), `ollama pull qwen3:8b`, a coleção que já vem pronta, `ingest --profile fichas`, `--cases` no runner, os presets, o estado medido pela réplica |
| `.env.example` | `LLM_MODEL=llama3.2:3b`, as três etapas do tradutor `True`, `CHROMA_PATH=data/chroma` | qwen, `LLM_THINK`, o atendente e a troca, as chaves do Gemini (sem valor), tradutor desligado, `RETRIEVAL_MODE`, `CONTEXT_MIN_SCORE=0.0`, `chroma_db` |
| `docs/CONTRATOS.md` | "CoT ainda não implementado: erro 400"; HyDE "desligado desde 17/09"; corte padrão 0,70 | o CoT existe (rodada 7); as três etapas desligadas desde 25/09, com a queda registrada; 0,0 e a porta de 0,72 só na base acadêmica; `retrieval_mode`, `attendant_provider`, `llm_model`, `think`; a procedência; o 503; os campos das fichas na fonte |
| `docs/estado-atual.md` | a coleção acadêmica como a ativa, uma receita só | a coleção das fichas ativa e versionada, as duas receitas, o perfil `fichas` |
| `data/retrieval/README.md` | 18 casos | 66 casos, e o modo vetorial |
| docstring do `gemini_query_client.py` | "não é chamado por nada em produção" | chamado pelo `HybridQueryClient` quando o tradutor está ligado |

**`frontend/streamlit_app.py` apagado.** Ninguém importava; o compose sobe o
`frontend/main.py`. Com isso, `grep -rn "/triagem"` fora de `evidencias/` só
encontra a linha do contrato que registra a rota como removida (critério do
[B-19](../backlog.md#b-19)).

**Backlog.** Itens novos: [B-75](../backlog.md#b-75) (direitos das capturas da
VCA e das "todos os direitos reservados") e [B-76](../backlog.md#b-76) (a
identidade do manifesto das fichas). O [B-74](../backlog.md#b-74) ("Respondido
por" e o 503 no frontend) entrou com a rodada 26. Atualizados:
[B-18](../backlog.md#b-18), [B-19](../backlog.md#b-19),
[B-61](../backlog.md#b-61), [B-62](../backlog.md#b-62),
[B-67](../backlog.md#b-67) e [B-69](../backlog.md#b-69). Cada "deixado para
depois" das rodadas 22 a 28 tem item:

| Rodada | Deixado para depois | Item |
|---|---|---|
| 22 | quebras de linha nos hashes; o lote teste | B-71, B-63 |
| 23 | 6 documentos de outro assunto; `por_que_importa`; o trecho no CI | B-72, B-61, B-61 |
| 24 | coleção versionada ou gerada; a régua nas fichas; o benchmark | B-73, B-67, B-67 |
| 25 | documentação; `think` na consulta; "Respondido por" | esta rodada, B-69, B-74 |
| 26 | "Respondido por" e 503; consultas guardadas na ablação; LGPD | B-74, B-66, B-64 |
| 27 | especialistas; VCA; `referencias.md`; frase sem fonte e parciais | B-61, B-75, B-62, B-61 |
| 28 | a prova 2 até o uso; pares repetidos e rótulos estranhados; 2ª pesquisa | B-63 |

**README e planejamento do João**: as rodadas 26 e 29 na tabela, o estado
atual e os números de referência da réplica, e a linha 6d do planejamento
(a implementação feita, a validar).

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `README.md`, `.env.example`, `docs/CONTRATOS.md`, `docs/estado-atual.md`, `data/retrieval/README.md` | como acima |
| `backend/app/clients/gemini_query_client.py` | só a docstring |
| `frontend/streamlit_app.py` | apagado |
| `evidencias/backlog.md` | B-75, B-76; atualizações de B-18, B-19, B-61, B-62, B-67, B-69; correção do texto do B-71 |
| `evidencias/joao/README.md`, `planejamento.md` | linha 29, estado atual, números de referência; linha 6d |

Commits: este.

## Observações

**1. Uma duplicata evitada.** O item que eu ia abrir como "a régua de
recuperação nas fichas como instrumento oficial" já existia (B-67, aberto na
consolidação da autópsia). Virou uma atualização dele.

**2. Um erro meu corrigido.** O texto do [B-71](../backlog.md#b-71) (rodada 22)
tinha o `\r\n` gravado como quebra de linha de verdade, e o item aparecia
"Normalizar ` ` → ` `". Corrigido aqui.

**3. O commit que fecha a rodada 27 diz "44 fontes"; são 45.** A evidência
está certa; a linha do README, que também dizia 44, foi corrigida aqui.

**4. O README do projeto** passa a mostrar o estado medido de 25/09 com a
ressalva de que a prova 1 é fácil para os sistemas bons; o número de 04/09
fica como histórico na rodada 4.

## Deixado para depois

- **O resto do código morto** ([B-18](../backlog.md#b-18)): `base_client.py`,
  `log_messages.py`, `seed_chroma.py`, `frontend/pages/chat.py`, `send_voice`,
  `OPENAI_API_KEY`, `VECTOR_DB`. São de outros trilhos.
- **A decisão sobre a coleção versionada** ([B-73](../backlog.md#b-73)): cada
  reindexação das fichas soma uma versão do `chroma.sqlite3` (~73 MB) ao
  histórico.

## Próximo passo

A validação do João, de manhã: `rodada_noturna/99_para_decidir_de_manha.md`
e `git log --oneline main..autopsia2-implementacao` no clone `_trabalho/impl`.
Depois do push, a prova 2 até o uso ([B-63](../backlog.md#b-63)).
