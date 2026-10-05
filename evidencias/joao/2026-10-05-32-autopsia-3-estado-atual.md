# Autópsia 3: o estado do projeto depois da segunda etapa

**Data:** 05/10/2026 · **Trilho:** B2, olhando o sistema inteiro · **Rodada:** 31 ·
**Commits:** este

> Rodada de **leitura e réplica**, sem mudar o sistema. Entre 27/09 e 02/10 a
> `main` recebeu dez commits (frontend React, segunda etapa, fluxo
> conversacional) enquanto o trilho B2 não desenvolveu. A pergunta desta rodada
> é a mesma das autópsias anteriores: onde o projeto está, medido e não
> lembrado — o sistema de 25/09 ainda responde igual? o que melhorou, o que
> virou risco, e qual é o próximo passo.

## O que foi feito

1. **Leitura do que mudou** (`e365f3e..bb2cdae`): os dez commits, o diff do
   caminho que o runner mede, a configuração nova, as evidências do Vinicius
   (rodadas 11 a 25 dele), o código da segunda etapa e do workspace
   conversacional, e o frontend React.
2. **Réplica mínima do sistema medido**, pela API, na `main` de hoje: a
   identidade da versão, a busca nos 296 casos da autópsia, o lote `dev` com o
   Gemini e com o qwen, e os 122 relatos independentes com o Gemini —
   comparados **caso a caso** com as rodadas citadas de 25/09.
3. **Suítes e conferências** na `main`, num ambiente novo.
4. **Triagem do backlog** (76 itens): o que já foi feito, o que ficou obsoleto
   com a arquitetura nova, o que continua aberto. Proposta, validada pelo João
   antes de mover qualquer item.
5. **As decisões de produto do João em 05/10**, registradas abaixo.

## Por quê

A rodada 30 fechou com dois próximos passos: levar o conteúdo certificado pelos
especialistas à ficha de leitura e a prova 2 até o uso. Antes de fazê-los era
preciso saber se o chão continuava o mesmo — o sistema de 25/09 reproduz na
`main` de hoje? — e o que o produto que nasceu em volta dele exige. Uma
autópsia é mais barata do que descobrir isso no meio da prova final.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Nenhum texto do sistema muda aqui; o que a rodada produz é medição e registro | O conteúdo certificado entra na rodada 32, medida à parte |
| A variação do Gemini entre dias é tratada por protocolo (repetições, conjunto-sentinela), não por código | Não há o que consertar no nosso lado; o que dá para fazer é medir sabendo disso ([B-77](../backlog.md#b-77)) |
| O seletor de atendente do produto oferece a escolha da IA, **sem** texto comparando velocidade e privacidade (João, 05/10) | Decisão de produto; o que segue aberto no [B-64](../backlog.md#b-64) é o consentimento e a persistência da escolha |
| As clínicas fictícias do modo demo ficam, como exemplo temporário (João, 05/10) | Decisão de produto; a passagem para clínicas reais depende de chave do Maps e de processo de verificação |
| O backlog é triado por proposta nesta evidência; os itens só mudam de status depois da validação do João | É a fila do time; a regra é o dono mover |
| As evidências dos outros trilhos não são reformatadas; o que esta rodada registra sobre elas é só o que muda a leitura dos números (a semântica das métricas) | Pedido do João: as evidências servem para organizar e escrever o texto, não para serem perfeitas |
| As quatro rodadas de hoje vão para `data/evaluation/cited/` | Sustentam a afirmação central desta evidência |

## Resultado esperado

_Escrito antes de rodar_ (`01_plano_e_criterios.md` da pasta local, 17h50).
Hipótese: o `/chat/` sem identificadores, em `WORKFLOW_MODE=demo`, se comporta
como em 25/09 — as 87 linhas que mudaram no caminho B2 só acrescentam
argumentos opcionais.

| # | O quê | Esperado (25/09) | Tolerância |
|---|---|---|---|
| R0 | `GET /health/fingerprint` | coleção `…280baf13`, 61 fichas, bge-m3, `vector`, corte 0,0, Gemini padrão sem troca, tradutor desligado, `think=False` | tudo igual |
| R1 | `/search/` vector top-3, 296 casos | 296/296 trios iguais aos da autópsia | ≥ 99% |
| R2 | `dev` (50) com `producao` (Gemini) | 1 · 0; 50/50 iguais a `20260925-040612_r2_gemini_dev_conta1` | ±1; ≥ 97% iguais |
| R3 | `dev` (50) com `local_qwen` | 1 · 0; 50/50 iguais a `20260925-040616_r3_qwen_final_dev` | ±1; ≥ 97% |
| R4 | independentes (122) com `producao` | 6 · 3; 122/122 iguais a `20260925-041607_r2_gemini_indep_conta1` | ±1; ≥ 97% |

Semântica da autópsia: emergência perdida inclui INCERTO. O lote `teste` da
prova 1 não é tocado; a prova 2 não é usada.

## Resultado obtido

### O sistema medido continua o mesmo; o atendente externo, não

| # | O quê | 25/09 | 05/10 | Mesma resposta | Dentro? |
|---|---|---|---|---|---|
| R0 | identidade da versão | — | igual em tudo; só o **Ollama** mudou (0.34.4 → 0.35.1), com os mesmos digests | — | ✅ |
| R1 | busca, 296 casos | 296/296 | **296/296**; agregados exatos (107/129 e 123/129; 74/122 e 94/122; 16/40 e 32/40) | — | ✅ |
| R2 | `dev` Gemini | 1 · 0 | **1 · 1** | 49/50 (98%) | ✅ |
| R3 | `dev` qwen (duas rodadas) | 1 · 0 | **1 · 0** e **1 · 0** | 50/50 e 50/50 | ✅ |
| R4 | independentes Gemini | 6 · 3 | **7 · 6** | 118/122 (96,7%) | ❌ perdidas no ±1; **falsos alarmes +3**; iguais abaixo de 97% |

Nos cinco casos que mudaram (p44 no `dev`; i40, i58, j12, j59 nos
independentes), **as 3 fichas foram as mesmas nos dois dias** (122/122 e 50/50),
o `model_version` devolvido pelo Google é o mesmo (`gemini-3.5-flash-lite`) e
não houve nova tentativa: só a decisão do Gemini mudou. Quatro foram para
EMERGENCIA; uma emergência clara (j12, leptospirose com icterícia e urina
escura) virou INCERTO (observação 1). Entre as duas rodadas do qwen de hoje, a
classe foi igual em 50/50 e a justificativa idêntica em 43/50 — o ruído de GPU
da rodada 5, que muda o texto e não a decisão.

Rodadas citadas: [`20261005-180245_a3_gemini_dev`](../../data/evaluation/cited/20261005-180245_a3_gemini_dev/report.md)
· [`20261005-180853_a3_qwen_dev_paralelo`](../../data/evaluation/cited/20261005-180853_a3_qwen_dev_paralelo/report.md)
· [`20261005-181015_a3_qwen_dev`](../../data/evaluation/cited/20261005-181015_a3_qwen_dev/report.md)
· [`20261005-181358_a3_gemini_indep`](../../data/evaluation/cited/20261005-181358_a3_gemini_indep/report.md).
Comandos: `python scripts/run_evaluation.py --api-url http://127.0.0.1:8000 --cases <lote> [--split dev] --preset producao|local_qwen`,
contra a API da `main` (`bb2cdae`) com a chave da conta 1.

**Latência do Gemini**: mediana 4,0 s nos dois lotes (igual a 25/09); no `dev`,
**p95 45 s e máximo 83 s** — o Google devolveu 504 duas vezes e o cliente
esperou 20 s por vez; em 25/09 o p95 do `dev` foi 5,5 s. Nos independentes,
p95 4,7 s e máximo 27,6 s (observação 2).

**Suítes na `main`** (ambiente novo): backend **340** (285 em 26/09), scripts
**224** (217), `mock/` 10; `sync_fichas --check`, `sync_retrieval_terms --check`,
`prova2_montar --check` e `compileall` limpos. Zero falhas.

### O que entrou na `main` entre 27/09 e 02/10

Dez commits do Vinicius, por PR (#15 a #18): 263 arquivos, +56.100 linhas.
`backend/app` passou de 10.165 para 12.061 linhas; `frontend-react/src` nasceu
com 3.577. **Intocados**: `data/` inteiro (o lote `teste` segue congelado, hash
`d370a0a5…`, contador 0), `backend/data/`, `backend/chroma_db/`, prompts,
presets, backlog e `evidencias/joao/`.

- **Frontend React ("VetIA")** na porta 3000; o Streamlit virou `--profile legacy`.
  O frontend **não chama `POST /chat/`**: usa `/workspace/conversations/{id}/messages`
  (202 + processamento em segundo plano + polling).
- **Workspace conversacional**: estende o pipeline medido por subclasse
  (`WorkspacePipeline(ChatPipeline)`), com a coleção das fichas, as 3 mais
  próximas, corte 0 e Gemini padrão herdados do `.env`. Diferenças: do 2º turno
  em diante o classificador recebe a transcrição; a busca usa a concatenação dos
  relatos do tutor; `num_ctx` 32.768 no Ollama; o `content` da resposta é
  montado sem `result.answer`. Quando a classe é INCERTO, uma segunda chamada
  ao mesmo provedor escolhe uma pergunta num catálogo fixo de 16; o
  classificador decide sempre, reexecutado a cada turno.
- **Segunda etapa**: login (demo / contas locais / Supabase), clínicas (Google
  Maps ou fictícias, conforme `MAPS_PROVIDER`), encaminhamento tutor→clínica com
  consentimento, snapshot da triagem reescrito pelo servidor, máquina de
  estados, chat humano, painel da clínica. Persistência em Mongo (loopback).
- **Avaliação conversacional** (rodadas 17, 20 e 24 dele): os 18 casos de
  calibração da prova 1, 2 braços × 2 repetições, em quatro rodadas (288
  decisões), mais 8 diálogos sintéticos. A primeira versão do fluxo regrediu
  de 34/36 para 30/36 (p11 N→I, p14 E→I) porque o histórico com regras e JSON
  foi mandado também à busca vetorial; voltar o relato cru para a busca
  corrigiu (34/36 nas três rodadas seguintes). **Não usou o lote `teste` nem a
  prova 2.** Reproduz a rodada citada de calibração de 25/09 caso a caso (só
  p16, N→I, nas oito passagens).
- **Comparação de embeddings** (rodada 25 dele): bge-m3 × MiniLM × LangChain em
  251 relatos, critério escrito antes (≤ 2 p.p. de hit@3). MiniLM 7,4× mais
  rápido e −33,5 p.p.; LangChain preserva ranks em 1.506/1.506. Mantém o
  bge-m3. Por conjunto, os números são os desta evidência (107/129, 123/129,
  74/122, 94/122).

### Triagem do backlog

_(tabela de proposta ao fim desta evidência, na seção "Anexo")_

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `data/evaluation/cited/20261005-*` (4 rodadas) | a réplica de hoje |
| `evidencias/backlog.md` | [B-77](../backlog.md#b-77) (o Gemini muda entre dias), [B-78](../backlog.md#b-78) (exposição antes de hospedar), [B-79](../backlog.md#b-79) (catálogo de perguntas sem validação), [B-80](../backlog.md#b-80) (dívida da segunda etapa); atualizações em B-61, B-63, B-64, B-65 e B-74 |
| `evidencias/joao/README.md`, `planejamento.md` | a rodada 31, o estado atual, o bloqueio 19 |

Commits: este.

## Observações

**1. O Gemini mudou entre 25/09 e 05/10, com entrada idêntica.** Cinco
decisões em 172 (2,9%):

| Caso | Rótulo · quadro | Ficha certa entre as 3? | 25/09 → 05/10 | Relato (início) |
|---|---|---|---|---|
| p44 | N · comeu fora da dieta | não | N → **E** | "gato… roubar um pedacinho de pastel com cebola… ontem… se comportando do jeitinho de sempre" |
| i40 | N · morcego/raiva | sim | N → **E** | "furinho pequeno no pescoço e vi um morcego voando perto da janela. Ele tá agindo normal" |
| i58 | N · comeu fora da dieta | não | I → **E** | "pedaço de pão com passas… Ele tá normal, brincando e comendo" |
| j12 | **E** · leptospirose | não | E → **I** | "muito prostrado desde ontem… urina… quase marrom. Parou de comer e está com os olhos amarelados" |
| j59 | N · conjuntivite leve | sim | N → **E** | "o olho do meu gato acordou todo remelado e meio fechadinho! É uma tragédia…" |

Na noite de 25/09 a repetição do `dev`, 50 minutos depois e com outra conta,
tinha dado 50/50 e as justificativas idênticas; o qwen deu 100% hoje, duas
vezes. A procedência não detecta a mudança (o `model_version` é o mesmo).
Consequências para a prova 2: repetições em dias diferentes, intervalo de
confiança, o braço local como referência de estabilidade, e um
conjunto-sentinela antes de cada medição ([B-77](../backlog.md#b-77)). Nota de
curadoria: o i58 ("pão com passas") está rotulado leve pelo mapa; passas são
tóxicas para cães, e os relatos independentes nunca passaram por veterinário
([B-63](../backlog.md#b-63)).

**2. O cliente do Gemini não tem prazo total.** O `GEMINI_TIMEOUT_S=60` vale
por tentativa; após 503/504 ele espera 20 s dobrando até 300 s, seis vezes.
Só de espera, o pior caso chega a ~900 s. Observado: 326 s num caso pelo
Vinicius (rodada 24 dele) e os 83 s de hoje. O conserto é um prazo por
pedido do tutor com o 503 `timeout` no estouro — e o produto oferecendo o modo
local ([B-65](../backlog.md#b-65)).

**3. Duas semânticas de métrica no repositório.** As avaliações conversacionais
reportam "acurácia balanceada de 3 classes" (INCERTO como classe) e macro-F1
de 3 classes; o runner do time reporta a balanceada E/N e não conta INCERTO
como falso não urgente. Para as mesmas previsões da calibração: 95,83% contra
0,9375, e macro-F1 0,8667 contra 0,9667. Nenhuma está errada; o texto do TCC
precisa dizer qual usa. Esta evidência usa a semântica da autópsia (perdida
inclui INCERTO), como as rodadas 14 a 30.

**4. O produto e as condições da decisão pelo Gemini.** A rodada 18 condicionou
o Gemini padrão a "nunca trocar de modelo em silêncio" e a resposta dizer quem
respondeu. No frontend de hoje: o autor visível é "VetIA"; "Modelo: provedor ·
modelo" fica num bloco recolhido de referências; o aviso em texto da troca
(quando permitida) não chega, porque o `content` do workspace não usa
`result.answer`; o 503 vira mensagem clara com "tentar de novo", mas o
`error_code` (cota × indisponível) é ignorado; o envio ao Google tem um aviso
informativo, sem consentimento, com Gemini como padrão e a escolha voltando ao
padrão a cada recarga. O seletor Gemini / modelo local **já existe** na tela
([B-74](../backlog.md#b-74), [B-64](../backlog.md#b-64)).

**5. Exposição.** `/chat/`, `/search/`, `/voice/`, `/clinics/search` e
`/clinics/geocode` sem identidade nem limite de taxa; backend (8000) e Ollama
(11434) publicados em todas as interfaces pelo Compose; `/chat/` aceita
`num_ctx` até 131.072 do cliente; o relato inteiro vai ao log INFO; o Nginx
não declara `client_max_body_size` (1 MB) para um `/voice/` que aceita 25 MB.
Não morde enquanto roda numa máquina só; vira bloqueador no dia de hospedar
([B-78](../backlog.md#b-78); o Vinicius lista o mesmo como prioridade 6 na
rodada 22 dele).

**6. Ambiente.** O venv da rodada noturna ficava em `%TEMP%` e o Windows o
apagou; o Ollama atualizou sozinho duas vezes desde a autópsia 2 (0.34.3 →
0.35.1). Os digests dos modelos são os mesmos e a réplica bateu, mas o
ambiente não estava sob controle: venv novo em pasta durável; fixar a versão
do Ollama no Compose é uma linha.

**7. Um bug latente na segunda etapa.** `POC_RAG_COLLECTION`, se preenchido,
abre outra coleção sem ler a receita de embedding do manifesto (cairia no
MiniLM). Por padrão está vazio e a documentação manda deixar assim
([B-80](../backlog.md#b-80)).

## Deixado para depois

- **Rodada 32 — o conteúdo certificado na ficha de leitura** ([B-61](../backlog.md#b-61)).
- **Prova 2 até o uso**, com o protocolo que a observação 1 exige
  ([B-63](../backlog.md#b-63)).
- **O produto honra as condições do Gemini**: "Respondido por" visível, aviso
  de troca no workspace, consentimento e persistência da escolha, 503 com
  código e a sugestão do modo local ([B-74](../backlog.md#b-74),
  [B-64](../backlog.md#b-64)).
- **Prazo total no cliente Gemini** ([B-65](../backlog.md#b-65)).
- **Exposição antes de hospedar** ([B-78](../backlog.md#b-78)); **catálogo de
  perguntas** com veterinários e medido em casos não vistos
  ([B-79](../backlog.md#b-79)); **dívida da segunda etapa**
  ([B-80](../backlog.md#b-80)).
- **Clínicas reais** no lugar das fictícias: chave do Maps e processo de
  verificação (decisão do João: temporário por enquanto).
- **O papel do trilho B1** com o tradutor desligado: a decidir com o time.

## Próximo passo

A rodada 32: preencher no mapa as 60 células da etapa 2 e a coluna
`por_que_importa` a partir dos rascunhos certificados (regra proposta: até 6
sinais curtos de "como o tutor conta" e "sinais de alarme"; o discriminador de
"como diferenciar"; `por_que_importa` do rascunho), regerar as fichas e a
coleção (`python scripts/sync_fichas.py`;
`python -m app.database.ingest_documents --profile fichas --activate`) e medir
busca e classificação (Gemini e qwen) nos lotes desta réplica, com o esperado
escrito antes. A autópsia 2 mostrou que ler a ficha longa piora o qwen; a
rodada pode terminar com menos frases do que os especialistas aceitaram.

## Anexo — triagem do backlog (proposta, a validar)

Cada um dos 76 itens foi conferido contra o código, os dados e as evidências na
`main` de 05/10 (`bb2cdae`), com a evidência (commit ou `arquivo:linha`) por
item. Resumo: **26 feitos** (13 já constam em "Resolvidos", só a tabela-índice
ficou desatualizada; 13 a mover), **12 obsoletos** (o componente saiu do caminho
padrão com a arquitetura da autópsia 2 e só vale para o braço da ablação),
**4 dependem de decisão**, **34 continuam abertos**. Nada foi movido: a regra é
o dono do item mover, depois da validação.

**Feitos, a mover para "Resolvidos" (13)**

| Item | O que fechou | Evidência |
|---|---|---|
| B-01 RAG degradava o sistema | o critério de 25/09: o runner reproduz o ganho (qwen 21 → 5 perdidas nos independentes, 122/122 iguais); com o Gemini o resultado é misto (ver nota) | `0636dfd`; `cited/20260925-033839…`, `…035453…` |
| B-02 Ordenação da busca não separa assunto | bge-m3 nas fichas: P@1 0,879 nos 66 casos; a cláusula "nenhuma emergência para o espirro leve" não cabe num desenho que manda sempre 3 fichas | `cd15c3d`; `data/retrieval/cited/20260925-031753…` |
| B-03 Base sintética, só de emergências | 61 fichas, 23 de rotina/24 h, certificadas em 26/09 | `56048b0`, `e365f3e` |
| B-07 Etapa de consulta custa 60% da latência | 0,92 s de mediana na GPU; e a etapa está desligada por padrão | rodada 14, `78f3186` |
| B-15 Relatos em inglês, base em português | provas e fichas em português; `--cases` e `relato_lang` no runner | `a8e7680` |
| B-19 Arquivos apontam para `/triagem` | só a linha do contrato que registra a remoção | `0163a1d` |
| B-20 Frontend não mostra triagem nem fontes | o React mostra classificação, sinais, recomendação, justificativa, fontes e o modelo (recolhido; o que falta é o B-74) | `6737665`, `454bdcf` |
| B-23 Frontend com hostname fixo | o React lê `VITE_API_URL`; o Streamlit legado continua fixo | `077da3d` |
| B-34 `main` sem CI | o workflow roda em PR; verde em `bb2cdae`; não cobre React/Playwright | `ad9b55f` |
| B-37 Virada da base sem perder comparabilidade | a base virou para as 61 fichas versionadas; o retrato dos 18 trechos segue restaurável | `cd15c3d`, `0636dfd` |
| B-49 Régua mede pouco com base pequena | `n_com_protocolo` 66 e `share_cases_above_threshold` 0,333 / 0,258 (critério literal) | `data/retrieval/cited/…` |
| B-56 Tutor/pet sem autenticação | fora do `demo`, sessão e titularidade; RLS por `auth.uid()`; o padrão continua `demo` | `077da3d` |
| B-57 Snapshot do Chroma fora do `CHROMA_PATH` | `CHROMA_PATH="chroma_db"` com ponteiro versionado; o trilho A confirmou em 27/09 | `cd15c3d` |

**Já resolvidos nas seções, com a tabela-índice desatualizada (13)**: B-08, B-09,
B-10, B-13, B-25, B-29, B-30, B-31, B-32, B-36, B-38, B-51, B-53 (B-30, B-31,
B-36, B-51 e B-53 aparecem como Aberto/Em andamento na tabela e como resolvidos
na seção e em "Resolvidos").

**Obsoletos com a arquitetura nova (12)** — valem só para o braço da ablação com
o tradutor ou a base acadêmica, se o [B-66](../backlog.md#b-66) os mantiver:
B-04 (temperatura e seed na consulta), B-06 (falsos não urgentes do llama nos 98
relatos), B-11 (limiar 0,70), B-12 (ingestão em máquina nova; a coleção vem
versionada), B-17 (`RERANK_TOP_K`, que nada lê), B-26 (HyDE no runner), B-27
(ruído residual do tradutor), B-28 (`num_ctx` na consulta), B-35 (PDF
multicoluna), B-41 (risco à vida no CoT), B-54 (Caderno da UFMG; a cobertura em
português veio pelas fichas), B-55 (paper de heatstroke na base acadêmica).

**Dependem de decisão (4)**: B-24 (critério do B-04: guardar as consultas
geradas uma vez, como o B-66 propõe, ou rodar com repetições), B-43 (decisão não
reproduzível entre sessões: fecha com a faixa já escrita ou migra para o
[B-77](../backlog.md#b-77)), B-52 (repositório privado, quando o orientador
liberar), B-75 (direitos das capturas da VCA).

**Continuam abertos (34)**: B-05, B-14, B-16, B-18, B-21, B-22, B-33, B-39, B-40,
B-42, B-44, B-45, B-46, B-47, B-48, B-50, B-58 a B-74 (exceto os acima), B-76.
Dois pesam na rodada 32: o **B-40** (a trava de base compara só os ids dos
trechos, e nas fichas os ids são fixos — reescrever uma ficha passaria sem aviso;
a rodada 32 confere o `content_sha256`) e o **B-48** (os 66 casos da régua seguem
com rótulo provisório).

**Dois defeitos de formatação no `backlog.md`** a corrigir junto: sete parágrafos
"Atualização de 12/09" de B-01, B-02, B-03, B-05, B-06, B-09 e B-11 estão dentro
da seção B-23 (linhas 783–982 da `main`); e B-06, B-11, B-34, B-37 e B-41 têm
status ou prioridade diferentes na tabela e na seção.

A tabela completa, item a item com a evidência e as dúvidas de cada leitura,
está na pasta local da autópsia (`relatorios/triagem_backlog.md`); entra no
repositório só o que o João validar.
