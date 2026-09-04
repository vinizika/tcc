# Backlog de melhorias

A fila única do projeto: tudo que foi identificado durante o desenvolvimento e
ainda precisa avançar — bugs, dívidas, decisões pendentes, oportunidades.
É compartilhado pelos três integrantes.

## Como este arquivo se relaciona com o resto

Um achado percorre três lugares, cada um com um papel:

| Onde | Papel | Quem escreve |
|---|---|---|
| **Observações** da rodada em `evidencias/<nome>/` | Onde o achado **nasce**: o que foi visto, com os dados. Histórico, não se altera | quem fez a rodada |
| **Este backlog** | A **fila única**: detalhe, impacto, dono, prioridade e status. É aqui que se acompanha | quem identificou registra; o responsável atualiza o status |
| **"O que está travando"** em `evidencias/<nome>/planejamento.md` | A visão **de um trilho**: só os itens que travam aquele trilho, em uma linha, apontando para cá | dono do trilho |

`docs/CONTRATOS.md` trata só das interfaces entre trilhos; pendências ficam
aqui.

## Regras

1. **Só cresce.** Nada é apagado. Item resolvido muda de status e ganha a
   data; item descartado idem, com o motivo.
2. **Quem identificou registra**, no mesmo dia, com link para a evidência
   onde o achado nasceu. Sem link, é opinião.
3. **Responsável é quem pode resolver**, não quem achou. Mudar o responsável
   é acordo entre os dois.
4. **Prioridade segue a rubrica abaixo**, para três pessoas aplicarem do
   mesmo jeito.
5. **Todo item diz o que o resolveria** — um critério verificável, de
   preferência um número da régua. Sem isso, ninguém sabe quando fechar.

### Rubrica de prioridade

| Prioridade | Quando |
|---|---|
| **Alta** | Bloqueia um marco ou um resultado medido, ou envolve segurança clínica (falso não urgente) |
| **Média** | Degrada qualidade, reprodutibilidade ou latência; existe contorno |
| **Baixa** | Higiene, documentação, dívida sem efeito medido |

### Status

`Aberto` · `Em andamento` · `Resolvido em DD/MM` · `Descartado em DD/MM (motivo)`

---

## Visão geral

| ID | Item | Responsável | Prioridade | Status |
|---|---|---|---|---|
| [B-01](#b-01) | Com a base atual, ligar o RAG degrada o sistema | Trilho A | Alta | Aberto |
| [B-02](#b-02) | Ordenação da busca não separa assunto | Trilho A | Alta | Aberto |
| [B-03](#b-03) | Base de conhecimento sintética, só de emergências | Trilho A + especialista | Alta | Aberto |
| [B-04](#b-04) | Temperatura e seed não fixadas na etapa de consulta | Trilho B1 | Alta | Aberto |
| [B-05](#b-05) | Conjunto de avaliação trivialmente separável | Time + especialista | Alta | Aberto |
| [B-06](#b-06) | Falsos não urgentes subiram de 3 para 8 com o prompt novo | Trilho B2 | Alta | Em andamento |
| [B-07](#b-07) | Etapa de consulta custa 60% da latência | Trilho B1 | Média | Aberto |
| [B-08](#b-08) | Reescrita de consulta adiciona julgamento clínico | Trilho B1 | Média | Aberto |
| [B-09](#b-09) | HyDE gera doença inexistente e nunca foi medido | Trilho B1 | Média | Aberto |
| [B-10](#b-10) | Consulta reescrita não vai ao índice com multi-query ligado | Trilho B1 (decisão) | Média | Aberto |
| [B-11](#b-11) | Limiar de 0,70 na busca não mede relevância | Trilho A | Média | Aberto |
| [B-12](#b-12) | Ingestão da base em máquina nova não estava documentada | Trilho A | Média | Em andamento |
| [B-13](#b-13) | Whisper com três implementações e sem benchmark | Trilho B1 | Média | Aberto |
| [B-14](#b-14) | Modelo inventa detalhe na justificativa | Trilho B2 | Média | Aberto |
| [B-15](#b-15) | Relatos de avaliação em inglês contra base em português | Trilho B2 + especialista | Média | Aberto |
| [B-16](#b-16) | Rótulo do data augmentation não descreve o método real | Time (escrita) | Média | Aberto |
| [B-17](#b-17) | `RERANK_TOP_K` e `CONTEXT_TOP_K` se sobrepõem | Trilho A + B2 | Baixa | Aberto |
| [B-18](#b-18) | Código morto e duplicado | Vários (lista no item) | Baixa | Aberto |
| [B-19](#b-19) | Arquivos ainda apontam para a rota `/triagem`, removida | Frontend / mock (dono a definir) | Baixa | Aberto |
| [B-20](#b-20) | Frontend não exibe a triagem estruturada nem as fontes | Frontend (dono a definir) | Baixa | Aberto (geladeira, outubro) |
| [B-21](#b-21) | Métricas RAGAs previstas no artigo | Trilho B2 | Baixa | Aberto (geladeira, outubro) |
| [B-22](#b-22) | Métrica de sinal alucinado na resposta | Trilho B2 | Baixa | Aberto |
| [B-23](#b-23) | Frontend só funciona pelo compose: hostname fixo no código | Frontend (dono a definir) | Baixa | Aberto |

---

## Itens

### B-01

**Com a base atual, ligar o RAG degrada o sistema**

**Identificado por:** João (B2) · **Onde:** [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md), 04/09 · **Responsável:** Trilho A · **Prioridade:** Alta · **Status:** Aberto

**O que observamos.** Nas mesmas 98 linhas, a temperatura zero: sem RAG,
0,878 de acurácia estrita e 8 falsos não urgentes em 71; com RAG (busca
ligada, consulta desligada), 0,674 e **30 falsos não urgentes**. Diferença de
−20,4 pontos, intervalo de confiança de 95% entre −29,6 e −11,2, teste de
McNemar pareado com p = 0,0001. Em 100% das linhas nenhum trecho passou do
limiar de 0,70; score máximo médio de 0,574. Reduzir para um trecho (19
falsos não urgentes) e ligar o pipeline completo (36 a 37) não resolvem.

**O mecanismo.** As 30 linhas rebaixadas citaram **zero** fontes. O modelo
leu protocolos de dificuldade respiratória e convulsão e passou a usar aquela
gravidade como régua: *"a ausência de sinais graves, como dificuldade
respiratória intensa ou desmaio, torna o caso menos urgente"*. É
recalibração do limiar, não alucinação ancorada em fonte errada.

**Por que importa.** Hoje a melhor configuração do sistema é a mais simples,
sem RAG — o que contradiz a proposta central do artigo. Enquanto isto não
mudar, cada componente de recuperação adicionado piora o resultado.

**O que resolveria.** Base com protocolos de assuntos variados, inclusive
condições leves ([B-03](#b-03)), e ordenação que separe assunto
([B-02](#b-02)). Critério de aceitação: o preset `naive_rag` igualar ou
superar o `llm_only` em acurácia balanceada **e** em falsos não urgentes,
sobre os 98 relatos.

### B-02

**Ordenação da busca não separa assunto**

**Identificado por:** João (B2), confirmando o handover de 30/08 · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md), 04/09 · **Responsável:** Trilho A · **Prioridade:** Alta · **Status:** Aberto

**O que observamos.** Para o relato de intoxicação por chocolate, a busca
devolveu "intoxicação por cebola e alho" (0,7411) e "vômito e diarreia"
(0,7256) antes do protocolo de chocolate (0,7021); em outra execução, o
protocolo de chocolate nem entrou nos três primeiros. Para um relato de
espirro leve, "obstrução urinária em gatos" veio em primeiro com **0,8183**,
o maior score de toda a rodada. Com o pipeline completo o score médio sobe de
0,574 para 0,680, mas o assunto continua errado — a otimização aproxima do
trecho errado com mais confiança.

**Por que importa.** É a causa provável de [B-01](#b-01). O handover de
30/08 já diagnosticava: chunks grandes que começam no meio de palavra,
cabeçalhos e rodapés repetidos, título e tema fora do texto embedado.

**O que resolveria.** Uma régua de recuperação (conjunto de relatos com o
documento esperado, medindo Precision@1 e MRR), depois preparação dos
documentos, prefixo de título/tema/espécie em cada chunk e re-ranking real.
Critério: documento correto em primeiro nos três casos de referência
(chocolate, obstrução urinária, e nenhum protocolo de emergência para o
espirro leve).

### B-03

**Base de conhecimento sintética, só de emergências**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md) e [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md), 04/09 · **Responsável:** Trilho A + especialista · **Prioridade:** Alta · **Status:** Aberto

**O que observamos.** Os 7 protocolos indexados declaram "Conteúdo sintético
para teste técnico" nos metadados, todos tratam de emergência e estão em
português; os relatos de avaliação são listas de sintomas em inglês.

**Por que importa.** Qualquer trecho recuperado empurra o modelo a comparar
o caso com uma emergência grave ([B-01](#b-01)). O artigo promete base
curada com participação de especialista, e curadoria depende de gente, não
de código — precisa começar cedo.

**O que resolveria.** Protocolos reais selecionados com a especialista,
cobrindo também condições leves e não urgentes, mantendo o padrão de
metadados do ingestor (`topic`, `species`). Critério: ao menos um protocolo
de não emergência por sistema orgânico frequente em relatos leigos.

### B-04

**Temperatura e seed não fixadas na etapa de consulta**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md), quantificado na [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md) · **Responsável:** Trilho B1 · **Prioridade:** Alta · **Status:** Aberto

**O que observamos.** As três chamadas ao modelo em `query_client.py`
(reescrita, multi-query, HyDE) não passam `options`, então usam a
temperatura padrão do Ollama (0,8) com seed aleatória. Com o pipeline
completo, **33 das 98 linhas mudam de classificação entre execuções
idênticas** (concordância de 0,663). No caso da gata sem urinar, 1 em 4
execuções virou não emergência.

**Por que importa.** Nenhuma rodada com o pipeline completo é reproduzível;
o estudo de ablação do artigo não se sustenta sem isso.

**O que resolveria.** `options=default_options()` nas três chamadas,
importando de `app.core.ollama` — três linhas. Critério: preset `rag_query`
com `--repeat 2` e zero linhas instáveis.

### B-05

**Conjunto de avaliação trivialmente separável**

**Identificado por:** João (B2) · **Onde:** [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md), 04/09 · **Responsável:** Time + especialista · **Prioridade:** Alta · **Status:** Aberto

**O que observamos.** Nas 98 linhas Dog/Cat, as 27 não emergências usam
**5 termos** de sintoma (Eye Discharge, Nasal Discharge, Skin Lesions,
Sneezing, Lameness) e têm 3 ou 4 sintomas; as 71 emergências têm sempre 5,
de 192 termos. A regra "só sintomas leves → não emergência" acerta **98 de
98** sem modelo; "menos de 5 sintomas" acerta 97. A classe não emergência tem
só 15 combinações distintas em 27 linhas. A origem do dado separa
perfeitamente o rótulo: emergências são todas originais, não emergências
todas sintéticas.

**Por que importa.** O conjunto mede se o sistema parou de exagerar a
urgência de cinco sinais leves, não a capacidade geral de triagem. Nenhuma
conclusão geral pode sair dele, e o artigo precisa dizer isso. As linhas
quase duplicadas também enfraquecem qualquer teste que assuma independência.

**O que resolveria.** Ampliar o vocabulário de sintomas leves com a
especialista, ou rotular casos originais leves como não emergência, ou
construir um conjunto de relatos leigos reais (ver [B-15](#b-15)).
Critério: as regras triviais abaixo de 0,90.

### B-06

**Falsos não urgentes subiram de 3 para 8 com o prompt novo**

**Identificado por:** João (B2) · **Onde:** [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md), 04/09 · **Responsável:** Trilho B2 · **Prioridade:** Alta · **Status:** Em andamento (próxima entrega: Chain-of-Thought)

**O que observamos.** Com o prompt antigo a temperatura zero: 3 falsos não
urgentes em 71 e 22 falsos urgentes em 27. Com o prompt novo: 8 e 2. A
acurácia balanceada subiu 32 pontos, mas o erro que cresceu é o grave.

**Por que importa.** Em triagem, deixar passar uma emergência é pior que
exagerar. A troca é defensável pelo saldo, mas o alvo é reduzir os 8 sem
perder o ganho nos 22.

**O que resolveria.** Chain-of-Thought (pedir ao modelo que percorra os
sinais um a um antes de concluir) e Self-Refine, medidos na régua contra a
linha de base `llm_only`. Critério: falsos não urgentes ≤ 4 mantendo falsos
urgentes ≤ 5.

### B-07

**Etapa de consulta custa 60% da latência**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md) e [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md) · **Responsável:** Trilho B1 · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** Com o pipeline completo, 3,5s dos 5,7s por resposta
são as três chamadas sequenciais ao modelo antes de qualquer busca. A
classificação em si leva ~2s.

**Por que importa.** O artigo trata latência como requisito ligado à
*golden hour*. Hoje a etapa piora resultado ([B-01](#b-01)) e tempo ao mesmo
tempo.

**O que resolveria.** As três chamadas são independentes: rodar em paralelo,
ou fundir numa única chamada que devolve reescrita, variações e documento
hipotético num só JSON. Critério: `query_s` mediano abaixo de 1,5s.

### B-08

**Reescrita de consulta adiciona julgamento clínico**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md), 04/09 · **Responsável:** Trilho B1 · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** *"Meu gato está espirrando"* virou *"gato apresentando
espirro, sintoma que requer avaliação veterinária imediata"* — um juízo de
urgência que não estava no relato, apesar da instrução explícita "nunca
adicione informações que não estavam no relato original".

**Por que importa.** Se a versão reescrita chegasse ao classificador,
contaminaria a decisão com a etapa de consulta. Foi por isso que o B2 passou
a mandar o relato original ao classificador e deixou a reescrita como dica
desligada por padrão.

**O que resolveria.** Exemplos negativos no prompt, ou uma verificação após a
reescrita que rejeite termos de urgência ausentes do original. Critério: zero
inserções de "imediata", "urgente" ou "emergência" em 30 relatos leves.

### B-09

**HyDE gera doença inexistente e nunca foi medido**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md), 04/09 · **Responsável:** Trilho B1 · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** Para o relato de chocolate, o documento hipotético
começava com *"Síndrome de Sífilo da Cadeia de Reações Imunes (SCR)"*, que
não existe. Esse texto vai direto à busca como consulta. Não é erro de
implementação: é o comportamento esperado de um modelo de 3 bilhões de
parâmetros escrevendo um trecho técnico sem âncora.

**Por que importa.** Ajuda a explicar a ordenação ruim ([B-02](#b-02)). E
nenhuma das três técnicas da etapa de consulta foi medida ligada e desligada
na régua de recuperação — hoje é fé.

**O que resolveria.** Medir HyDE, multi-query e reescrita, cada um ligado e
desligado, na régua de recuperação do trilho A. Se uma técnica não melhorar
Precision@1, desligá-la por padrão. Critério: cada técnica mantida só com
número que a justifique.

### B-10

**Consulta reescrita não vai ao índice com multi-query ligado**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md) e [`docs/CONTRATOS.md`](../docs/CONTRATOS.md) · **Responsável:** Trilho B1 (decisão) · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** Com o multi-query ligado, a busca recebe as três
variações e o HyDE; a consulta reescrita em si só é buscada quando o
multi-query está desligado.

**Por que importa.** "Ligado" não é um superconjunto de "desligado": os dois
braços da ablação diferem em natureza, não em grau, e a comparação fica
difícil de interpretar.

**O que resolveria.** Decisão do dono: passar a buscar `[reescrita] +
variações`, sem duplicatas. O pipeline do B2 já tem o ponto único
(`_build_queries`) para absorver a mudança.

### B-11

**Limiar de 0,70 na busca não mede relevância**

**Identificado por:** João (B2), a partir do handover de 30/08 · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md) e [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md) · **Responsável:** Trilho A · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** O filtro de score ≥ 0,70 foi adicionado em 03/09; o
handover de 30/08 dizia para não fixar limiar enquanto documentos errados
tivessem scores maiores que os certos. Hoje, com a consulta direta pelo
relato, nada passa de 0,70 e o filtro é inócuo (cai no fallback). Com o
pipeline completo, 40% das linhas passam — e são do assunto errado
(espirro → obstrução urinária com 0,82).

**Por que importa.** Score absoluto de cosseno com este modelo de embedding
não separa relevância; o limiar dá uma falsa segurança e levou à conclusão
de que faltavam documentos, quando o provável era a base vazia
([B-12](#b-12)).

**O que resolveria.** Medir por posição (Precision@1, MRR) na régua de
recuperação, não por score absoluto; rever o limiar só depois do re-ranking.

### B-12

**Ingestão da base em máquina nova não estava documentada**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md), 04/09 · **Responsável:** Trilho A · **Prioridade:** Média · **Status:** Em andamento — o B2 documentou o comando no README raiz e o `/health/fingerprint` expõe `chunk_count`; falta o trilho A confirmar o fluxo

**O que observamos.** O banco vetorial não é versionado; um clone limpo tem
a base vazia (0 registros) e o RAG não recupera nada até rodar
`python -m app.database.ingest_documents` uma vez. Foi o caso nesta máquina.

**Por que importa.** Qualquer colega novo roda sem RAG sem saber. O commit de
03/09 que concluiu "faltam documentos" provavelmente rodou sobre base vazia.

**O que resolveria.** Passo no README (feito em 04/09) e a verificação
`curl localhost:8000/health/fingerprint` mostrando `chunk_count` maior que
zero antes de qualquer teste com RAG.

### B-13

**Whisper com três implementações e sem benchmark**

**Identificado por:** João (B2) · **Onde:** [diagnóstico da divisão](../docs/divisao-de-trabalho.md), 31/08 · **Responsável:** Trilho B1 · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** `VoiceService` carrega o modelo `small` (é o que a API
usa); `ai/whisper/model.py` e `models/whisper_model.py` carregam `base` no
import e não são usados; `core/models.py` instancia um cliente no import.
Dois tamanhos de modelo, três caminhos de código.

**Por que importa.** A qualidade da transcrição depende de qual caminho
roda, e o artigo cita ~97,5% de precisão sem que exista medição.

**O que resolveria.** Uma implementação só; benchmark de taxa de erro de
palavras com 15 a 20 áudios gravados pelo time. Critério: número registrado
numa evidência.

### B-14

**Modelo inventa detalhe na justificativa**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md), observação 8 · **Responsável:** Trilho B2 · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** No caso da gata sem urinar, a justificativa afirmou
*"a presença de sangue na urina é um sinal de dor e inflamação"* — o tutor
nunca mencionou sangue. O campo de sinais de alerta ficou correto; a
justificativa em texto livre escapou.

**Por que importa.** É texto que o tutor lê, com um fato inventado.

**O que resolveria.** Self-Refine checando cada afirmação da justificativa
contra o relato e os trechos, e a métrica de [B-22](#b-22) para medir.

### B-15

**Relatos de avaliação em inglês contra base em português**

**Identificado por:** João (B2) · **Onde:** [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md), "Deixado para depois" · **Responsável:** Trilho B2 + especialista · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** Os relatos são "Animal: Dog. Sintomas observados:
Fever, Vomiting…"; a base é em português. As 194 strings de sintoma incluem
grafias como "Anoxeria", "Seizuers" e "Week Pulse".

**Por que importa.** Provavelmente limita a recuperação, e uma lista de
palavras não é o "relato de um tutor leigo" que o prompt espera.

**O que resolveria.** Um arquivo de mapeamento inglês→português revisado
pela especialista, versionado; uma chave `--relato-lang` no runner; rodada
própria comparando os idiomas, nunca misturados na mesma comparação.

### B-16

**Rótulo do data augmentation não descreve o método real**

**Identificado por:** João (B2) · **Onde:** [diagnóstico da divisão](../docs/divisao-de-trabalho.md), 31/08 · **Responsável:** Time (escrita do artigo) · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** A coluna `Source` diz `llm_data_augmentation` e o
diário antigo fala em "geração via LLM", mas a geração das 32 linhas
sintéticas foi **combinatória e determinística** (todas as combinações de
3 a 5 dos 5 sintomas leves, por espécie); o modelo de linguagem só **validou**
depois, aprovando 27.

**Por que importa.** O método real é melhor — controlado e reprodutível — e
no TCC essa seção será lida com lupa. O rótulo atual induz a descrição
errada.

**O que resolveria.** Renomear o valor de `Source` (por exemplo,
`synthetic_combinatorial`) ou documentar a distinção onde o dado é descrito,
e escrever o método real no artigo: geração combinatória, curadoria da
especialista, validação por modelo.

### B-17

**`RERANK_TOP_K` e `CONTEXT_TOP_K` se sobrepõem**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md) · **Responsável:** Trilho A + B2 · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** `RERANK_TOP_K = 3` é do trilho A e hoje não é usado;
`CONTEXT_TOP_K = 3` é do B2 e decide quantos trechos vão ao prompt.

**Por que importa.** Quando o re-ranking real entrar e cortar em 3, pedir 5
trechos de contexto devolverá 3 em silêncio.

**O que resolveria.** Combinar qual dos dois manda, e documentar em
`CONTRATOS.md`.

### B-18

**Código morto e duplicado**

**Identificado por:** João (B2) · **Onde:** [diagnóstico da divisão](../docs/divisao-de-trabalho.md), 31/08 · **Responsável:** vários · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** Sem importadores ou superados:

| Arquivo | Dono | Nota |
|---|---|---|
| `backend/app/core/models.py` | B1 | instancia um cliente Whisper no import |
| `backend/app/ai/whisper/`, `backend/app/models/whisper_model.py` | B1 | os dois Whispers órfãos ([B-13](#b-13)) |
| `backend/app/base/base_client.py`, `backend/app/utils/log_messages.py` | — | órfãos |
| `backend/app/database/seed_chroma.py` | A | superado pelo ingestor |
| `frontend/streamlit_app.py`, `frontend/pages/chat.py`, `send_voice` em `frontend/services/api.py` | frontend | interface antiga (o compose usa `main.py`), página vazia, função duplicada |
| `mock/` | — | protótipo inicial |
| Settings `OPENAI_API_KEY`, `VECTOR_DB`, `CHROMA_PATH` | B2 / A | sem uso |

**Por que importa.** Num time de três, duplicata é onde alguém conserta o
arquivo errado.

**O que resolveria.** Apagar; o Git guarda a história.

### B-19

**Arquivos ainda apontam para a rota `/triagem`, removida**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md), parte 3 · **Responsável:** Frontend / mock (dono a definir) · **Prioridade:** Baixa · **Status:** Aberto — o README raiz foi corrigido em 04/09

**O que observamos.** `frontend/streamlit_app.py` e `mock/streamlit_app_mock.py`
chamam `POST /triagem`, que não existe desde a rodada 3.

**O que resolveria.** Apagar os dois (o compose sobe `frontend/main.py`).
Critério: `grep -r triagem` fora de `evidencias/` não retornar nada.

### B-20

**Frontend não exibe a triagem estruturada nem as fontes**

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md) · **Responsável:** Frontend (dono a definir após o trilho C ser congelado) · **Prioridade:** Baixa · **Status:** Aberto (geladeira, outubro)

**O que observamos.** A interface mostra só o campo `answer`. A resposta já
traz `triage` (classificação, sinais, recomendação, fontes citadas) e
`sources`.

**O que resolveria.** Exibir classificação em destaque, sinais, recomendação
e fontes, lendo de `triage`. O contrato está em `docs/CONTRATOS.md`.

### B-21

**Métricas RAGAs previstas no artigo**

**Identificado por:** João (B2) · **Onde:** [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md), "Deixado para depois" · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto (geladeira, outubro)

**O que observamos.** O artigo prevê faithfulness, answer relevance e
context precision. Hoje a ancoragem não está estável ([B-01](#b-01),
[B-02](#b-02)).

**O que resolveria.** Plugar o RAGAs no runner depois que a recuperação
separar assunto; antes disso mediria ruído.

### B-22

**Métrica de sinal alucinado na resposta**

**Identificado por:** João (B2) · **Onde:** [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md), "Deixado para depois" · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** Ver [B-14](#b-14). Comparar os sinais citados na
resposta com o texto do relato é medível, mas exige decidir como tratar
sinônimos ("vômito" e "vomitando").

**O que resolveria.** Coluna no runner com a taxa de sinais citados ausentes
do relato; entra quando o Self-Refine existir, porque é a métrica que
mostraria se ele ajuda.

### B-23

**Frontend só funciona pelo compose: hostname fixo no código**

**Identificado por:** João (B2) · **Onde:** ao documentar o README raiz, 04/09 · **Responsável:** Frontend (dono a definir) · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** `frontend/services/api.py` e
`frontend/app/clients/voice_client.py` têm `http://backend:8000` escrito no
código — o nome do container, que só resolve dentro da rede do compose.
Rodar o frontend fora do Docker não alcança a API.

**Por que importa.** Quem quiser iterar na interface sem o compose não
consegue; e é o mesmo tipo de acoplamento que o backend tinha e resolveu na
[rodada 2](joao/2026-09-03-03-configuracao-centralizada.md).

**O que resolveria.** Ler a URL da API de uma variável de ambiente com
padrão `http://localhost:8000`, e o compose injetar `http://backend:8000`
— o mesmo desenho do `OLLAMA_HOST` no backend.

---

## Resolvidos

*(nenhum ainda — um item chega aqui com a data e um link para a evidência ou
commit que o fechou)*
