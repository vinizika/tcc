# A busca nas fichas, com o bge-m3 e as 3 mais próximas

**Data:** 25/09/2026 (madrugada) · **Trilho:** B2, olhando o sistema inteiro
(o embedding, a ingestão e a busca são do trilho A; o tradutor, do B1) ·
**Rodada:** 24 · **Commits:** este

> Segunda rodada de código. Leva ao sistema a busca da
> [rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md): o relato cru vai
> ao bge-m3, que compara com as 61 fichas de busca, e as 3 mais próximas
> entram no prompt, **sempre**, sem porta, sem roteador e sem reranker. A
> coleção acadêmica continua abrindo com o MiniLM, como braço "hoje" da
> ablação. O portão é a busca da API devolver as mesmas 3 fichas que a autópsia
> mediu, caso a caso.

## O que foi feito

1. **Receitas de embedding** (`embedding_config.py`): cada coleção guarda no
   manifesto qual receita a construiu — `minilm-academic-v1` (a de hoje, com o
   mesmo hash `1a93e1e7…`) ou `bge-m3-fichas-v1` (bge-m3 na revisão fixada
   `5617a9f6…`, 1024 dimensões, até 512 tokens, sem recorte em trechos).
2. **O cliente do Chroma escolhe o embedding pelo manifesto** da coleção ativa,
   antes de abri-la, e confere a coleção contra a receita que o manifesto
   declara. Voltar para a coleção acadêmica (`--rollback`) volta a abrir com o
   MiniLM, sem tocar em código.
3. **O perfil `fichas` na ingestão**: 61 registros, id `ficha__<topic>`, o
   texto de busca como documento vetorizado (sem prefixo) e o texto de leitura
   no `metadata.body` (é ele que chega ao prompt), com título de leitura,
   título para o tutor, espécie, urgência e referências. Recusa texto acima de
   512 tokens.
4. **A coleção das fichas versionada** em `backend/chroma_db/` (61 × 1024), com
   manifesto e ponteiro ativo, e `CHROMA_PATH = "chroma_db"`: um clone limpo
   sobe com a busca nova, sem passo manual ([B-57](../backlog.md#b-57)). O
   compose ganha um volume para o cache do Hugging Face.
5. **`retrieval_mode`**: `vector` (novo padrão: busca vetorial pura, as mais
   próximas em ordem de similaridade) ou `routed_rerank` (o caminho de hoje:
   roteador lexical, reranker, âncoras, veto de espécie). Nas settings, nas
   opções da requisição, na configuração efetiva, no `/search`, no runner da
   régua e no runner de avaliação.
6. **Os padrões mudam**: `vector`, corte de relevância 0,0 (as 3 mais
   próximas, sempre), top 3, e o tradutor (reescrita, multi-query e HyDE)
   desligado. O corte de 0,72 continua existindo como constante do braço
   acadêmico e num preset (`fichas_com_porta_0_72`); os presets antigos passam
   a dizer explicitamente o modo e o corte que sempre usaram.

## Por quê

- A autópsia mediu que, nas fichas, o bge-m3 põe a ficha certa em 1º em ~80%
  dos casos da prova + régua, contra ~20% do MiniLM, e que as 3 mais próximas
  sem porta ganham da porta nos relatos de quem não viu o mapa (qwen: 21 → 7
  emergências perdidas, p = 0,0005)
  ([rodada 16](2026-09-24-17-busca-bge-m3-e-tres-fichas.md)). O tradutor
  piora a busca nas fichas ([rodada 17](2026-09-24-18-tradutor-desligado.md)).
- **Trocar só as constantes do embedding quebraria a coleção acadêmica**, que
  foi indexada com o MiniLM e passaria a ser consultada com vetores de outro
  modelo. Guardar a receita no manifesto e escolher o embedding por ela é o que
  deixa os dois braços da ablação abrirem com o próprio modelo.
- **Um clone limpo hoje não reproduz nenhum número com RAG** sem passos
  manuais ([B-57](../backlog.md#b-57)).

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| As constantes antigas (`EMBEDDING_MODEL_NAME` etc.) continuam sendo a receita acadêmica | O recorte em trechos da coleção acadêmica usa o tokenizer do MiniLM; uma reindexação dela tem de continuar produzindo os mesmos trechos |
| Manifesto sem `recipe_key` (os antigos) resolve para a receita pelo par modelo + revisão | As 13 coleções já versionadas não têm o campo; elas continuam abrindo como antes |
| No modo `vector`, sem roteador **e sem veto de espécie** | É o que a autópsia mediu. O veto de espécie mora no reranker e só vale no braço roteado |
| A coleção entra no repositório (o `chroma.sqlite3` versionado) | É o que o time já faz com as candidatas, e o critério do B-57 é o clone limpo subir sem passo manual. O custo é mais uma versão do arquivo binário (~73 MB) no histórico — registrado para o João decidir de manhã |
| O `/search` passa a obedecer o `retrieval_mode` (padrão `vector`) | A régua mede a busca que o sistema usa; o modo roteado continua disponível por parâmetro |
| Corte padrão 0,0, e não "sem corte" como caso especial | O pipeline já tem o corte; com 0,0 ele deixa passar as 3 mais próximas, que é a decisão |

## Resultado esperado

_Escrito antes de rodar._

- **R0 (funcional):**
  - o retrato da API mostra a coleção de fichas: 61 registros, bge-m3, receita
    `bge-m3-fichas-v1`;
  - `--rollback` para `…388f518d` abre com 3.481 trechos e o MiniLM, e volta;
  - `/search` com "meu cachorro comeu chocolate e está tremendo" traz
    `chocolate_toxicosis` em 1º.
- **R1 (réplica da busca):** `/search` em modo `vector`, as 3 primeiras, nos
  lotes da autópsia (dev, calibração, régua, as duas metades dos relatos
  independentes e o piloto: 296 casos), reproduz os trios de
  `_trabalho/ctx/bgecl_leitura_mapa_top3.json` em **pelo menos 99% dos casos**
  (na ordem), e os agregados medidos (ficha certa em 1º / entre as 3):
  prova + régua 107/129 e 123/129; independentes 74/122 e 94/122; piloto 16/40
  e 32/40 — com tolerância de ±1 caso.
- **Suíte** verde, com os testes que mudam de padrão atualizados e os novos
  (receitas, perfil de fichas, modo vetorial).
- **Sem R1 dentro da tolerância, a rodada 26 (a réplica da decisão) não roda.**

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
