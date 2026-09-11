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
| [B-04](#b-04) | Temperatura e seed não fixadas na etapa de consulta | Trilho B1 | Alta | Em andamento — 82% resolvido, ver [B-24](#b-24) |
| [B-05](#b-05) | Conjunto de avaliação trivialmente separável | Time + especialista | Alta | Aberto |
| [B-06](#b-06) | Falsos não urgentes subiram de 3 para 8 com o prompt novo | Trilho B2 | Alta | Em andamento |
| [B-07](#b-07) | Etapa de consulta custa 60% da latência | Trilho B1 | Média | Aberto |
| [B-08](#b-08) | Reescrita de consulta adiciona julgamento clínico | Trilho B1 | Média | Aberto |
| [B-09](#b-09) | HyDE gera doença inexistente e nunca foi medido | Trilho B1 | Média | Aberto |
| [B-10](#b-10) | Consulta reescrita não vai ao índice com multi-query ligado | Trilho B1 (decisão) | Média | Aberto |
| [B-11](#b-11) | Limiar de 0,70 na busca não mede relevância — e o corte efetivo é zero | Trilho A | **Alta** | Aberto |
| [B-12](#b-12) | Ingestão da base em máquina nova não estava documentada | Trilho A | Média | Em andamento |
| [B-13](#b-13) | Whisper com três implementações e sem benchmark | Trilho B1 | Média | Resolvido em 08/09 |
| [B-14](#b-14) | Modelo inventa detalhe na justificativa | Trilho B2 | Média | Aberto |
| [B-15](#b-15) | Relatos de avaliação em inglês contra base em português | Trilho B2 + especialista | Média | Aberto |
| [B-16](#b-16) | Rótulo do data augmentation não descreve o método real | Time (escrita) | Média | Aberto |
| [B-17](#b-17) | `RERANK_TOP_K` e `CONTEXT_TOP_K` se sobrepõem | Trilho A + B2 | Baixa | Aberto |
| [B-18](#b-18) | Código morto e duplicado | Vários (lista no item) | Baixa | Em andamento — órfãos de Whisper apagados em 08/09 |
| [B-19](#b-19) | Arquivos ainda apontam para a rota `/triagem`, removida | Frontend / mock (dono a definir) | Baixa | Aberto |
| [B-20](#b-20) | Frontend não exibe a triagem estruturada nem as fontes | Frontend (dono a definir) | Baixa | Aberto (geladeira, outubro) |
| [B-21](#b-21) | Métricas RAGAs previstas no artigo | Trilho B2 | Baixa | Aberto (geladeira, outubro) |
| [B-22](#b-22) | Métrica de sinal alucinado na resposta | Trilho B2 | Baixa | Aberto |
| [B-23](#b-23) | Frontend só funciona pelo compose: hostname fixo no código | Frontend (dono a definir) | Baixa | Aberto |
| [B-24](#b-24) | Critério de aceitação do B-04 pode ser inatingível | Time (decisão de método) | Média | Aberto |
| [B-25](#b-25) | O compare não detecta mudança de código entre rodadas | Trilho B2 | Média | Resolvido em 11/09 |
| [B-26](#b-26) | Runner não registra o documento gerado pelo HyDE | Trilho B2 | Baixa | Aberto |
| [B-27](#b-27) | Caracterizar o ruído residual antes de decidir o critério do B-04 | Trilho B2 | Média | Aberto |
| [B-28](#b-28) | Efeito de num_ctx nas chamadas de consulta não verificado | Trilho B2 | Baixa | Aberto |
| [B-29](#b-29) | Fingerprint da base não identifica conteúdo nem embedder | Trilho A + B2 | Média | Resolvido em 11/09 |
| [B-30](#b-30) | Ingestão pode deixar coleção parcial ou registros órfãos | Trilho A | Alta | Aberto |
| [B-31](#b-31) | Cobertura da ingestão ainda não chega à integração com ChromaDB | Trilho A | Média | Em andamento |
| [B-32](#b-32) | Upload de voz aceita caminho e tamanho controlados pelo cliente | Trilho B1 | Alta | Resolvido em 08/09 |
| [B-33](#b-33) | Healthcheck não verifica modelo nem base vetorial | Operação + B2 | Média | Aberto |
| [B-34](#b-34) | `main` não tem CI nem ambiente totalmente reproduzível | Time | Baixa | Aberto |
| [B-35](#b-35) | Extração do paper multicoluna ainda contém artefatos clínicos | Trilho A | Alta | Em andamento |
| [B-36](#b-36) | Rótulo de título e seção embutido no texto do chunk chega ao prompt | Trilho A | Alta | Aberto |
| [B-37](#b-37) | Virada da base: trocar os 18 trechos pela base nova sem perder comparabilidade | Trilho A + Time + B2 | **Alta** | Em andamento — passo 1 feito |
| [B-38](#b-38) | Runner não confere a base antes de uma rodada com recuperação | Trilho B2 | Alta | Resolvido em 11/09 |
| [B-39](#b-39) | `--expect-base-hash` é opcional e depende de disciplina | Trilho B2 | Baixa | Aberto |
| [B-40](#b-40) | A conferência de base olha o recorte, não o conteúdo | Trilho B2 | Baixa | Aberto |
| [B-41](#b-41) | Modelo não calibra "risco à vida"; âncora não testada | Trilho B2 | Média | Aberto |
| [B-42](#b-42) | Técnica e modelo confundidos: CoT não rodou com modelo maior | Time | Média | Aberto |
| [B-43](#b-43) | Etapa de decisão não é reproduzível entre sessões | Trilho B2 | Baixa | Aberto |
| [B-44](#b-44) | Divergências entre o artigo do TCC1 e o sistema construído | Time (escrita) | Média | Aberto |
| [B-45](#b-45) | Sem conjunto de desenvolvimento: ajuste de prompt no conjunto de teste | Trilho B2 | Alta | Aberto |
| [B-46](#b-46) | Teste limpo do efeito da ordem dos campos | Trilho B2 | Baixa | Aberto |
| [B-47](#b-47) | Retrato do sistema inclui estado de momento e gera aviso falso | Trilho B2 | Baixa | Aberto |
| [B-48](#b-48) | Gabarito da régua de recuperação precisa de validação clínica | Trilho A + especialista | Alta | Aberto |
| [B-49](#b-49) | Régua de recuperação mede pouco enquanto a base e o conjunto forem pequenos | Trilho A + B2 | Média | Aberto |

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

**Identificado por:** João (B2) · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md), quantificado na [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md) · **Responsável:** Trilho B1 · **Prioridade:** Alta · **Status:** Em andamento — corrigido no código pelo B1 em [rodada 1 do Ryu](ryu/2026-09-04-01-reprodutibilidade-da-consulta.md), 04/09. Critério numérico **medido em 05/09** na [rodada 6 do João](joao/2026-09-05-06-determinismo-da-consulta.md): instabilidade caiu de 33 para **6 linhas em 98** (concordância 0,663 → 0,939), mas o critério pede zero e não foi atingido. A causa residual é ruído numérico de GPU, não configuração — ver [B-24](#b-24), que propõe rever o critério

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

**Identificado por:** João (B2) · **Onde:** [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md), 04/09 · **Responsável:** Trilho B2 · **Prioridade:** Alta · **Status:** Aberto — o Chain-of-Thought foi medido em 11/09 e **reprovado**; ver abaixo

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

**Identificado por:** João (B2), a partir do handover de 30/08 · **Onde:** [rodada 3](joao/2026-09-04-04-geracao-ancorada.md) e [rodada 4](joao/2026-09-04-05-runner-de-avaliacao.md) · **Responsável:** Trilho A (medir o limiar certo) · **Prioridade:** Alta · **Status:** Em andamento — a parte do B2 foi **resolvida em 12/09** ([rodada 10](joao/2026-09-12-10-corte-de-relevancia.md)); falta o limiar medido na régua de recuperação

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

**Identificado por:** João (B2) · **Onde:** [diagnóstico da divisão](../docs/divisao-de-trabalho.md), 31/08 · **Responsável:** Trilho B1 · **Prioridade:** Média · **Status:** Resolvido em 08/09 — [rodada 3 do Ryu](ryu/2026-09-08-03-whisper-unico-e-wer.md)

**O que observamos.** `VoiceService` carrega o modelo `small` (é o que a API
usa); `ai/whisper/model.py` e `models/whisper_model.py` carregam `base` no
import e não são usados; `core/models.py` instancia um cliente no import.
Dois tamanhos de modelo, três caminhos de código.

**Por que importa.** A qualidade da transcrição depende de qual caminho
roda, e o artigo cita ~97,5% de precisão sem que exista medição.

**O que resolveria.** Uma implementação só; benchmark de taxa de erro de
palavras com 15 a 20 áudios gravados pelo time. Critério: número registrado
numa evidência.

**Como foi resolvido (08/09).** As duas implementações órfãs foram apagadas
(`app/ai/whisper/`, `app/models/whisper_model.py`, `app/clients/whisper_client.py`,
`app/core/models.py`) — sobrou o `VoiceService`, com o tamanho do modelo em
setting (`WHISPER_MODEL_SIZE`, padrão `small`) para ficar registrado junto de
qualquer medição. O benchmark de WER foi construído em `scripts/` (harness
`run_voice_benchmark.py` + módulo puro `wer_metrics.py` + 18 relatos PT-BR em
`voice_benchmark/references.csv`). Como o time não quis gravar áudio, os
relatos são **fala sintética** (edge-tts, vozes neurais PT-BR) — o WER medido
é um **limite otimista**, a ser substituído por áudio real. Número da rodada
inaugural na evidência. Não cobre o benchmark com áudio real nem a
consolidação dos outros órfãos de [B-18](#b-18) fora do Whisper.

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

**Identificado por:** João (B2) · **Onde:** [diagnóstico da divisão](../docs/divisao-de-trabalho.md), 31/08 · **Responsável:** vários · **Prioridade:** Baixa · **Status:** Em andamento — os órfãos de Whisper foram apagados em 08/09 ([rodada 3 do Ryu](ryu/2026-09-08-03-whisper-unico-e-wer.md)); o resto continua

**O que observamos.** Sem importadores ou superados:

| Arquivo | Dono | Nota |
|---|---|---|
| ~~`backend/app/core/models.py`~~ | B1 | **apagado 08/09** — instanciava um cliente Whisper no import |
| ~~`backend/app/ai/whisper/`, `backend/app/models/whisper_model.py`, `backend/app/clients/whisper_client.py`~~ | B1 | **apagados 08/09** — os Whispers órfãos ([B-13](#b-13)) |
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


**Medido em 11/09 — o Chain-of-Thought não resolve.** A
[rodada 8](joao/2026-09-11-08-chain-of-thought.md) implementou o checklist estruturado e mediu cinco braços.
Os falsos não urgentes caíram de 8 para **1** (o critério pedia 4 ou menos),
mas os falsos urgentes subiram de 4 para **16** — e o recall da classe não
emergência foi a **zero**: das 27 linhas leves, nenhuma classificada
corretamente. Acurácia balanceada de 0,856 para 0,408, McNemar 29 contra 3,
p abaixo de 0,0001.

A metade "mantendo falsos urgentes ≤ 5" do critério foi o que impediu a
leitura errada: sozinha, a primeira metade diria que o item estava resolvido.

Causa raiz em [B-41](#b-41): o modelo marca claudicação como risco à vida em
20 de 25 vezes, e a regra do checklist amplifica fielmente esse julgamento.
O braço de controle mostrou que a rubrica pesa mais que a ordem dos campos —
escrever o raciocínio **depois** da conclusão deu 0,664, melhor que os 0,408
de escrever antes.

**O item segue aberto.** As rotas que restam são a âncora de calibração
([B-41](#b-41)) e um modelo maior ([B-42](#b-42)); nenhuma é a entrega
seguinte do trilho. O Self-Refine, que era a outra técnica prevista para este
item, tem o mesmo pressuposto e provavelmente o mesmo destino — o que
sobrevive do desenho dele é a trava de segurança determinística.


**Atualização de 12/09 — o corte efetivo é zero, e isso muda todas as
medições com RAG.** A [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md) mediu, sobre as 98 linhas do braço
`naive_rag`: similaridade máxima **média de 0,574** e **zero linhas** com
algum trecho acima do limiar de 0,70. Mesmo assim, **98 de 98** prompts
receberam três trechos, porque `context_min_score` está em **0,0** — o
limiar de 0,70 só aparece como estatística no relatório, não corta nada.

Consequência: os braços com recuperação do projeto não mediram recuperação,
mediram **injeção fixa de ruído**. Com o corte aplicado, `naive_rag` seria
idêntico a `llm_only`. Por isso a prioridade sobe para Alta: enquanto isto
não for decidido, nenhuma rodada com RAG mede o que diz medir.


**Atualização de 12/09 — o que foi medido, com precisão.** À luz do
[B-11](#b-11), a frase "ligar o RAG degrada o sistema" precisa ser lida como
**"injetar três trechos irrelevantes no prompt degrada o sistema"**: nas 98
linhas, nenhum trecho recuperado passou do limiar de relevância, e os três
entraram assim mesmo. O mecanismo descrito acima (recalibração do limiar de
gravidade) continua válido; o que muda é que ele foi provocado por ruído, e
não por conhecimento mal aplicado. Ver [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md).


**Atualização de 12/09.** A [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md) acrescenta dois pontos à
curadoria:

1. **Nenhum dos protocolos atuais trata de quadros leves**, e nenhum diz a
   gravidade de um sinal isolado. O desenho de Chain-of-Thought do artigo
   pressupõe exatamente isso — o passo "correlacionar com as evidências
   recuperadas" existe para o modelo não precisar julgar sozinho.
2. **Cuidado ao curar:** os cinco sintomas leves do conjunto de avaliação
   foram escolhidos pela especialista. Um protocolo que diga "estes cinco
   são leves" faz o RAG acertar a prova por construção. Protocolos reais
   sobre quadros leves, sim; a chave de resposta, não.


**Atualização de 12/09 — o atalho é ainda mais estreito do que parecia.**
A [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md) mediu que **18 das 27 linhas leves contêm "Sneezing"**, e o
acerto depende disso: a linha de base acerta 17 de 18 com espirro e 6 de 9
sem. No braço com a rubrica do CoT, 10 de 18 contra **0 de 9**. Os quatro
falsos urgentes da linha de base são **todas** as combinações de lesão de
pele com claudicação.

Ou seja, a classe leve testa na prática dois tokens. Isso não invalida as
medições, mas limita o que elas significam: o conjunto mede **vocabulário**,
não triagem.


**Atualização de 12/09 — o Chain-of-Thought do artigo nunca chegou a ser
testado.** A [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md) comparou o que foi medido com o que o artigo do
TCC1 descreve. O artigo define o CoT em três passos, sendo o do meio
*"a correlação com as evidências recuperadas"* — é ele que dispensa o modelo
pequeno de julgar sozinho.

Esse passo não rodou: no braço sem recuperação por construção, e no braço
com recuperação porque a busca não trouxe nada relevante ([B-11](#b-11)) e o
passo que julgaria os trechos apareceu em 17 de 98 linhas.

O que a rodada 8 mediu, portanto, foi o julgamento clínico do modelo
**sozinho**. A causa principal do fracasso também mudou: não é só o modelo
não calibrar gravidade, é a rubrica por sinal exigir um julgamento que a
entrada não permite — os relatos são listas sem gravidade nem duração, e em
21 das 23 abstenções o modelo contrariou a regra do checklist para seguir a
instrução "sem informação suficiente, responda INCERTO".

**Dependências para uma nova tentativa:** [B-03](#b-03) (protocolos que
cubram os assuntos do conjunto e falem de quadros leves), [B-11](#b-11)
(corte de relevância maior que zero), [B-05](#b-05) e [B-45](#b-45) (dado
com gravidade e conjunto de desenvolvimento separado).


**Correção de dono, 12/09.** Este item estava com o trilho A como único
responsável. Conferindo o código, o corte em zero tem **duas metades**, e
uma é do B2:

| Onde | O que faz | Dono |
|---|---|---|
| `CONTEXT_MIN_SCORE = 0.0` em `core/config.py` | Deixa qualquer trecho entrar no prompt, sem nota mínima. Colocado **de propósito** na rodada 3, com o motivo no comentário: naquele dia nenhum documento passava do limiar, e descartar todos faria o braço com RAG ficar idêntico ao braço sem RAG | **B2** |
| Fallback em `retrieval_client.py` | Quando nada passa de 0,70, devolve os mais próximos assim mesmo, com aviso no log | Trilho A |

**O custo de corrigir, que precisa estar escrito antes de alguém aplicar.**
Com a base atual, respeitar o corte faz o braço com RAG **desaparecer** das
medições: ele vira idêntico ao `llm_only`, porque nenhuma das 98 linhas tem
trecho acima do limiar. Isso não é regressão. É o retrato verdadeiro de que
hoje o RAG não tem o que acrescentar — e é o motivo de esta correção vir
**antes** da ampliação da base ([B-03](#b-03)): enquanto o corte for zero,
qualquer base nova será medida junto com o ruído.

**Decisão pendente do time:** o que o classificador recebe quando não há
nada relevante. A proposta do B2 é "nada", com o sistema se comportando como
sem RAG e a resposta registrando que a busca não trouxe nada acima do corte.
A ordem completa das três correções está no
[adendo da rodada 9](joao/2026-09-12-09-autopsia-do-cot.md#adendo-de-1209--as-três-correções-em-linguagem-simples-e-uma-hipótese-em-espera).


**Resolvido em 12/09, na parte do B2** ([rodada 10](joao/2026-09-12-10-corte-de-relevancia.md)). `CONTEXT_MIN_SCORE`
passou de 0,0 para 0,70, referenciando a constante que a busca já usa. Sem
trecho acima do corte, o classificador recebe nada e o sistema responde como
sem RAG. A resposta passou a trazer o corte aplicado e uma trava
(`used_below_min_score`) que nunca pode ser verdadeira; o relatório de cada
rodada passou a dizer em quantos por cento dos casos o RAG contribuiu, com
aviso automático quando a busca fica silenciosa em todas as linhas.

Medido: com corte, **0 de 98** linhas recebem trecho e o resultado é
**idêntico** à linha de base de 04/09 (zero linhas diferentes). Sem corte,
98 de 98 recebem e a acurácia balanceada cai 11,8 pontos, com 22 falsos não
urgentes a mais. **Injetar três trechos irrelevantes custa 22 emergências
classificadas como leves** — este é o número honesto do RAG hoje.

O preset `naive_rag_sem_corte` preserva o braço antigo para a ablação e para
reproduzir as rodadas citadas até 11/09.

**O que falta, e é do trilho A:** o limiar 0,70 continua sem fundamento
medido — é o valor que o sistema já reportava, escolhido por coerência
interna e declarado provisório no código. O número certo sai da régua de
recuperação.


**Atualização de 12/09 — o custo do ruído, isolado.** Com o corte valendo
([rodada 10](joao/2026-09-12-10-corte-de-relevancia.md)), o braço com RAG e o braço sem RAG passaram a produzir o
**mesmo** resultado, porque nenhum trecho entra. Comparando os dois braços
que diferem **só** no corte: balanceada 0,893 com corte contra 0,775 sem, e
8 contra 30 falsos não urgentes. Ou seja, os 20 pontos que este item atribuía
ao RAG são o custo de **injetar três trechos irrelevantes**, não de usar
conhecimento recuperado. O item continua aberto porque a base ainda não
cobre os assuntos do conjunto ([B-03](#b-03)).


**Medido em 12/09, e o diagnóstico mudou de natureza.** A [rodada 11](joao/2026-09-12-11-regua-de-recuperacao.md)
construiu a régua de recuperação e mediu os 18 relatos:

| | |
|---|---|
| Protocolo certo em 1º lugar | 5 de 9 |
| Protocolo certo **entre os cinco** devolvidos | **9 de 9** |
| "Trauma, quedas e hemorragias" em 1º lugar | **9 de 18** |

Recall@5 em 1,000 significa que o índice **tem** o documento certo e **o
encontra** — só não o põe em primeiro. O problema não é cobertura nem
chunking: é **ordenação**. Isso reforça o re-ranking e enfraquece a hipótese
de que mais documentos resolveriam sozinhos.

E existe um **protocolo-ímã**: "trauma" aparece em primeiro em metade dos
casos, inclusive para convulsão, picada de abelha e cão urinando gotinhas. A
hipótese é que o texto dele cubra sinais genéricos (dor, sangramento,
prostração, dificuldade de locomoção) presentes em quase todo relato — mas
confirmar exige olhar os trechos, e isso é do trilho A.

Um segundo padrão: a busca casa com o **sintoma literal**, não com a causa.
"Comeu chocolate… e está vomitando" traz o protocolo de vômito em 1º e o de
chocolate em 5º. Para triagem é o inverso do desejado.


**Desbloqueado em 12/09.** A régua de recuperação existe ([rodada 11](joao/2026-09-12-11-regua-de-recuperacao.md)):
`scripts/run_retrieval_eval.py`, com Precision@1, MRR, Recall@5 e a linha de
base já congelada. É o instrumento que faltava para medir reescrita,
multi-query e HyDE ligados e desligados. O trilho B1 pode usá-la assim que
quiser — a régua chama `POST /search/`, que é busca pura; medir as técnicas
de consulta exige uma variante que passe pelo `chat_pipeline` com
`include_debug`, ou uma opção nova na régua para aceitar as consultas já
transformadas.


**Atualização de 12/09 — quatro protocolos que faltam, com nome.** A régua
de recuperação ([rodada 11](joao/2026-09-12-11-regua-de-recuperacao.md)) tem quatro relatos que são emergência e
para os quais **nenhum protocolo da base trata do assunto**:

| Quadro | Caso |
|---|---|
| Dilatação-torção gástrica | cão grande, barriga inchada e dura, vômito improdutivo |
| Hipoglicemia e hipotermia neonatal | filhote de dois meses, molinho, não mama, boca fria |
| Obstrução uretral em **cães** | cão macho urinando gotinhas com dor (o protocolo da base é de **gatos**) |
| Emergência neurológica | cadela idosa sem levantar as pernas de trás, ofegante |

Nos quatro, a busca oferece o protocolo errado com convicção parecida à dos
casos que acerta. São quadros clássicos de pronto-socorro veterinário, e
viram a lista de compras da curadoria.

---

### B-24

**O critério de aceitação do B-04 pode ser inatingível como está escrito**

**Identificado por:** João (B2) · **Onde:** [rodada 6](joao/2026-09-05-06-determinismo-da-consulta.md), 05/09 · **Responsável:** Time (decisão de método) · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** O B-04 pede zero linhas instáveis. Depois da correção
do B1, a instabilidade caiu de 33 para 6 linhas em 98 (concordância de 0,663
para 0,939), mas não chegou a zero. A causa residual não é configuração: a
variação cresce com o comprimento da geração — 8% na reescrita (uma frase),
17% nas multi-queries (três linhas), 30% no HyDE (66 a 154 palavras) —, que
é a assinatura de ruído numérico de ponto flutuante em GPU com decodificação
gulosa. Nem seed nem temperatura controlam isso.

**Por que importa.** Um critério inatingível mantém um item aberto para
sempre e não orienta ninguém. Pior: sugere que o trabalho do B1 não
funcionou, quando os dados mostram o contrário (sem a correção, a reescrita
variaria em ~100% das linhas em vez de 8%).

**O que resolveria.** Trocar o critério por um que diga o que de fato
importa para o artigo: **a instabilidade residual não pode inverter nenhuma
conclusão da matriz de ablação**. Na prática, todo braço que use a etapa de
consulta roda com `--repeat` e é reportado com a faixa, não com um ponto; e
uma diferença entre braços só é afirmada se for maior que a variação interna
de cada um. É decisão de método, do time — não de um trilho. Antes de decidir, vale ter o que o [B-27](#b-27) mede.

---

### B-25

**O `compare` não detecta mudança de código entre rodadas**

**Identificado por:** João (B2) · **Onde:** [rodada 6](joao/2026-09-05-06-determinismo-da-consulta.md), 05/09 · **Responsável:** Trilho B2 · **Prioridade:** Média · **Status:** Resolvido em 11/09 — [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md)

**O que observamos.** Comparando uma rodada de antes com uma de depois do
commit `b907d6e` — que mudou o comportamento da etapa de consulta —, o
`report_evaluation.py compare` imprimiu "diferenças de configuração:
nenhuma". Ele checa configuração, dataset, modelo, base vetorial e prompts,
e o hash dos prompts cobre apenas os três prompts de triagem (do B2). O
código do pipeline e os prompts das etapas de consulta não entram no
fingerprint.

**Por que importa.** O trilho B1 vai mexer nos prompts de consulta (B-08) e
na montagem das consultas (B-10). Depois disso, duas rodadas minhas podem
divergir sem que o instrumento avise que o sistema mudou — e a explicação
mais provável, na hora da escrita, seria atribuir a diferença ao braço
testado. O dado necessário já existe: o manifesto grava o git sha, e como o
compose monta `./backend:/app`, esse sha descreve mesmo o código executado.

**O que resolveria.** Duas coisas pequenas: (1) o `compare` avisar quando o
git sha das duas rodadas diferir, como já faz com modelo e base; (2) o
`/health/fingerprint` hashear também os prompts de consulta de
`query_client.py`. Critério: comparar as rodadas `20260904-024433_r3b_variancia`
e `20260905-133840_b04_confirmacao` deve emitir aviso.


**Como foi resolvido (11/09).** O `compare` passou a avisar quando o
`git.sha` das duas rodadas difere, e também quando alguma delas rodou com a
árvore suja. A comparação do fingerprint passou a olhar **apenas as chaves
presentes nos dois manifestos**: sem isso, os campos que nasceram em 11/09
fariam toda rodada anterior acusar diferença contra toda rodada nova, e um
aviso que aparece sempre deixa de ser lido. Verificado no caso que motivou o
item: R3b contra a rodada 6 agora imprime `a95f895 -> ad7c7b8`. Não cobre
hashear os prompts da etapa de consulta — o aviso de commit já denuncia a
mudança, e hashear prompts de outro trilho é acoplamento que não se paga.

---

### B-26

**O runner não registra o documento gerado pelo HyDE**

**Identificado por:** João (B2) · **Onde:** [rodada 6](joao/2026-09-05-06-determinismo-da-consulta.md), 05/09 · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** Cada linha de `predictions.jsonl` grava
`rewritten_question` e `queries`, mas não o documento hipotético do HyDE em
campo próprio. Ele entra misturado como um dos elementos de `queries`. Para
medir sua variação na rodada 6 foi preciso inferi-lo como "o último elemento
com mais de 200 caracteres" — uma convenção frágil e não documentada.

**Por que importa.** O HyDE é a chamada mais cara e a mais variável da etapa
de consulta (30% das linhas mudam entre execuções idênticas, contra 8% da
reescrita), e é a única sem registro próprio. Qualquer análise futura sobre
o efeito dele — inclusive a hipótese de que atrapalhe a recuperação em vez
de ajudar — depende de reconstruí-lo por heurística.

**O que resolveria.** Um campo `hyde_document` na linha do JSONL, separado de
`queries`, alimentado pelo mesmo bloco de depuração que já devolve a
reescrita. Critério: uma rodada de `rag_query` grava o texto do HyDE em
campo próprio, e `queries` passa a conter só as consultas.

---

### B-27

**Caracterizar o ruído residual antes de decidir o critério do B-04**

**Identificado por:** João (B2) · **Onde:** [rodada 6](joao/2026-09-05-06-determinismo-da-consulta.md), 05/09 · **Responsável:** Trilho B2 · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** A rodada 6 mediu 6 linhas instáveis em 98 e atribuiu a
causa a ruído numérico de GPU, com base no gradiente por comprimento de
geração (8% na reescrita, 17% nas multi-queries, 30% no HyDE) e no
cruzamento "mesmo contexto, mesma decisão, zero exceções". As duas evidências
são fortes, mas **indiretas**: nenhuma isola a etapa de consulta de fato.

**Por que importa.** É insumo direto do [B-24](#b-24), que pede ao time uma
decisão sobre o critério do [B-04](#b-04). Decidir sem saber se as 6 linhas
são sempre as mesmas seria decidir no escuro: "6 linhas frágeis conhecidas"
e "6 sorteadas a cada par de execuções entre muitas candidatas" são
problemas de tamanhos diferentes — no primeiro caso dá para listá-las e
vigiá-las; no segundo, qualquer braço pode virar.

**O que resolveria.** Duas rodadas curtas, cerca de 25 minutos somados:

1. `naive_rag --subset full --repeat 2` — sem nenhuma chamada de consulta.
   Se der **zero** linhas instáveis, confirma a hipótese H1 da rodada 6 e
   prova que o ruído nasce na etapa de consulta. Se oscilar, a hipótese cai
   e o problema é mais amplo do que se pensa.
2. `rag_query --subset full --repeat 3` — para ver se o conjunto de linhas
   instáveis se repete entre pares de execuções ou muda a cada vez.

Critério: as duas rodadas citadas em `data/evaluation/cited/`, com a
resposta registrada numa evidência e levada ao B-24.

---

### B-28

**Efeito de `num_ctx=4096` nas chamadas de consulta não foi verificado**

**Identificado por:** João (B2) · **Onde:** [rodada 6](joao/2026-09-05-06-determinismo-da-consulta.md), 05/09 · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** O commit `b907d6e` passou a enviar `default_options()`
nas três chamadas de consulta, e essa função manda **quatro** parâmetros:
além de `temperature` e `seed`, também `num_ctx=4096` e `num_predict=600`,
que antes ficavam no padrão do servidor. Na rodada 6 verifiquei apenas o
`num_predict`: o documento HyDE mais longo tem 154 palavras (~200 tokens),
bem abaixo do teto, então esse não morde. O `num_ctx` ficou sem verificação.

**Por que importa.** Pouco, provavelmente — os prompts de consulta recebem
relatos de duas linhas e dificilmente passariam do contexto anterior. Mas é
uma mudança de comportamento que entrou junto com outra na mesma rodada, o
que a regra de "uma mudança por rodada" existe para evitar. Enquanto não for
verificada, qualquer diferença futura no braço de consulta tem uma segunda
explicação possível em aberto.

**O que resolveria.** Comparar o tamanho em tokens do maior prompt de
consulta contra o `num_ctx` padrão do `llama3.2:3b` no Ollama. Se couber com
folga, fechar o item como verificado e registrar o número.

---

### B-29

**Fingerprint da base não identifica conteúdo nem embedder**

**Identificado por:** Vinicius (A) · **Onde:** [auditoria do trilho A](vini/2026-09-07-01-auditoria-do-repositorio.md), 07/09 · **Responsável:** Trilho A + B2 · **Prioridade:** Média · **Status:** Resolvido em 11/09 — [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md)

**O que observamos.** O `/health/fingerprint` calcula o hash da base somente
sobre os IDs dos chunks. Esses IDs são derivados de
`caminho:página:índice_do_chunk`, sem conteúdo. Alterar o texto ou os
metadados mantendo o mesmo número de chunks preserva o fingerprint, mesmo que
o conhecimento e os vetores tenham mudado. O manifesto também não identifica
a revisão do modelo de embedding nem os parâmetros do chunking.

**Por que importa.** Duas rodadas podem declarar a mesma base vetorial quando
na verdade usaram conteúdos ou embeddings diferentes. Isso enfraquece a
reprodutibilidade justamente durante a próxima ampliação da base.

**O que resolveria.** Incluir no fingerprint um hash determinístico de IDs,
documentos e metadados, além do nome/revisão do embedder e dos parâmetros de
chunking. Critério: mudar apenas o texto de um documento, sem mudar seu ID,
deve alterar o fingerprint em teste automatizado.


**Como foi resolvido (11/09).** O `/health/fingerprint` passou a trazer, em
`vector_store`: `content_sha256` (hash de id + texto + metadados de todos os
trechos, ordenado, então independe da ordem de leitura do banco),
`embedding_model` e `chunking` (target, overlap, limite). O
`chunk_ids_sha256` ficou **intacto** de propósito — é por ele que as seis
rodadas citadas até 05/09 continuam comparáveis. Critério atendido: sete
testes em `backend/tests/test_api_health.py`, entre eles o que reescreve o
texto de um trecho sem mudar o id e verifica que só o hash de conteúdo muda.
Custo medido da chamada: 19 ms com 18 trechos.

---

### B-30

**Ingestão pode deixar coleção parcial ou registros órfãos**

**Identificado por:** Vinicius (A) · **Onde:** [auditoria do trilho A](vini/2026-09-07-01-auditoria-do-repositorio.md), 07/09 · **Responsável:** Trilho A · **Prioridade:** Alta · **Status:** Aberto

**O que observamos.** Para reingerir um arquivo, o ingestor apaga seus chunks
antes de executar os upserts. Uma falha de embedding ou escrita após essa
exclusão pode deixar a coleção ativa incompleta; com `--reset`, o risco cobre
a base inteira. No sentido oposto, a execução sem reset não remove registros
de documentos que já foram apagados da pasta, pois só visita os arquivos que
ainda existem.

**Por que importa.** A ampliação da base é a próxima atividade do trilho A e
sustentará novas medições. Uma coleção parcial ou com documentos órfãos pode
mudar os resultados sem aparecer como erro explícito.

**O que resolveria.** Preparar a nova base em coleção temporária, validar
contagem/manifesto e só então promover a coleção completa, ou implementar
rollback equivalente. O manifesto da ingestão deve também remover fontes que
deixaram de existir. Critério: uma falha injetada no meio da ingestão mantém a
coleção ativa anterior intacta, e apagar um documento da origem o remove da
base seguinte.

---

### B-31

**Cobertura da ingestão ainda não chega à integração com ChromaDB**

**Identificado por:** Vinicius (A) · **Onde:** [auditoria do trilho A](vini/2026-09-07-01-auditoria-do-repositorio.md), 07/09 · **Responsável:** Trilho A · **Prioridade:** Média · **Status:** Em andamento — limpeza, seções, chunking e inspeção ganharam testes na [rodada 2](vini/2026-09-07-02-ingestao-cientifica-token-aware.md); ainda falta uma integração com Chroma temporário e os cenários transacionais

**O que observamos.** Na auditoria inicial, os testes substituíam Chroma,
recuperação e re-ranking por dublês e não exercitavam o processamento
documental. A rodada 2 passou a cobrir limpeza, seções, PDF/TXT, metadados,
IDs produzidos pelo orquestrador, limites e o paper real. Ainda não existe
teste de reingestão, falha transacional ou consulta sobre Chroma temporário.

**Por que importa.** O núcleo que o trilho A vai modificar pode regredir sem
que as suítes atuais detectem. A falha só apareceria numa rodada
completa, mais lenta e com resultado difícil de diagnosticar.

**O que resolveria.** Testes unitários do processamento documental e ao menos
um teste de integração com armazenamento temporário e função de embedding
determinística, sem download de modelo. Critério: cobrir ingestão inicial,
reingestão, falha intermediária e busca ordenada de um caso conhecido.

---

### B-32

**Upload de voz aceita caminho e tamanho controlados pelo cliente**

**Identificado por:** Vinicius (A), em auditoria cruzada · **Onde:** [auditoria do trilho A](vini/2026-09-07-01-auditoria-do-repositorio.md), 07/09 · **Responsável:** Trilho B1 · **Prioridade:** Alta · **Status:** Resolvido em 08/09 — [rodada 2 do Ryu](ryu/2026-09-08-02-endurecimento-do-upload-de-voz.md)

**O que observamos.** `POST /voice/` concatena `audio.filename` diretamente à
pasta `uploads/` e abre esse caminho para escrita. Não há nome gerado pelo
servidor, validação de permanência na pasta, limite de tamanho/tipo ou remoção
do arquivo depois da transcrição.

**Por que importa.** Um nome com componentes de caminho pode sobrescrever
arquivos fora de `uploads/` sob as permissões do backend; arquivos grandes ou
uploads repetidos podem consumir disco. No Compose, o diretório do backend é
montado a partir do repositório local, ampliando o impacto de uma sobrescrita.

**O que resolveria.** Gerar nome temporário no servidor, validar tipo e limite
de bytes, garantir remoção em `finally` e adicionar testes para path traversal
e excesso de tamanho. Critério: o nome enviado pelo cliente nunca participa do
caminho de escrita e nenhum arquivo temporário permanece após sucesso ou erro.

**Como foi resolvido (08/09).** A rota passa a gravar em
`uploads/<uuid>.<ext>`, com a extensão vinda de uma allowlist (sufixo do nome
ou tipo declarado) — o nome do cliente nunca entra no caminho. A gravação é em
blocos com teto de `MAX_AUDIO_UPLOAD_MB` (padrão 25), abortando com 413; tipo
não suportado recai em 415 e áudio vazio em 422. O arquivo é removido em
`finally`, em sucesso ou erro. Sete testes novos em
`backend/tests/test_api_voice.py` cobrem path traversal, excesso de tamanho,
tipo inválido, áudio vazio, extensão pelo content-type e limpeza após falha
na transcrição. Não resolve o benchmark do Whisper ([B-13](#b-13)) nem a URL
fixa do frontend ([B-23](#b-23)).

---

### B-33

**Healthcheck não verifica modelo nem base vetorial**

**Identificado por:** Vinicius (A) · **Onde:** [auditoria do trilho A](vini/2026-09-07-01-auditoria-do-repositorio.md), 07/09 · **Responsável:** Operação + B2 · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** `GET /health/` sempre devolve `{"status":"ok"}` e é a
rota usada pelo healthcheck do Compose. O serviço é considerado saudável
mesmo sem conexão com Ollama, sem o modelo baixado ou com zero chunks. O
endpoint `/health/fingerprint` expõe parte dessas informações, mas não decide
saúde e não é usado pelo Compose.

**Por que importa.** O frontend pode ser liberado para um backend incapaz de
responder, e uma avaliação pode começar sem RAG efetivo se a conferência
manual for esquecida.

**O que resolveria.** Separar liveness de readiness. A readiness deve conferir
Ollama/modelo e, quando o preset exigir recuperação, coleção não vazia; o
Compose deve depender dela. Critério: ausência do modelo ou base vazia mantém
liveness ativo, mas readiness não saudável.

---

### B-34

**`main` não tem CI nem ambiente totalmente reproduzível**

**Identificado por:** Vinicius (A) · **Onde:** [auditoria do trilho A](vini/2026-09-07-01-auditoria-do-repositorio.md), 07/09 · **Responsável:** Time · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** Não existe workflow de CI, lint ou checagem de tipos.
Parte das dependências está sem versão fixa, incluindo `chromadb` e
`sentence-transformers`, e a imagem do Ollama usa `latest`. A `.venv` presente
nesta máquina não executa a suíte do backend. A contagem do README, que estava
em 49, foi sincronizada para os 92 casos atuais nas rodadas 2 e 3, mas continua
sendo mantida manualmente.

Na [rodada 3 do trilho A](vini/2026-09-07-03-extracao-cientifica-layout-aware.md),
uma reconstrução do backend resolveu versões novas e fez `torch==2.14.0`
baixar vários pacotes CUDA mesmo na imagem padrão. A instalação, inclusive do
PyMuPDF no Python 3.12/Linux, terminou, mas a exportação foi interrompida
quando o disco chegou a 99%. A VM registrou erros de I/O em EXT4 e o Docker
Desktop não voltou após um reinício normal; nenhum reset, prune ou volume foi
apagado. É uma nova reprodução concreta do mesmo problema de dependências não
fixadas e agora exige recuperação operacional do Docker, sem abrir um item
separado.

**Por que importa.** A regra “main sempre rodando” depende de verificação
manual, e instalações feitas em datas diferentes podem usar implementações
distintas justamente no núcleo vetorial.

**O que resolveria.** Workflow mínimo executando as duas suítes, dependências
reprodutíveis e uma única fonte para a contagem/comando dos testes. Critério:
todo pull request exibe as suítes do backend e dos scripts aprovadas em
ambiente criado do zero.

---

### B-35

**Extração do paper multicoluna ainda contém artefatos clínicos**

**Identificado por:** Vinicius (A) · **Onde:** [rodada 2 do trilho A](vini/2026-09-07-02-ingestao-cientifica-token-aware.md), 07/09 · **Responsável:** Trilho A · **Prioridade:** Alta · **Status:** Em andamento

**O que observamos.** A limpeza recompõe hifenização de coluna e o parser
separa corretamente 24 headings no paper real de heatstroke. Mesmo assim, o
texto entregue pelo `pypdf` contém artefatos anteriores ao chunking, entre
eles `58delirium` no início da seção de sinais clínicos, sequências como
`/C14C` em temperaturas e espaços residuais em ligaturas recompostas.

**Por que importa.** A seção de sinais clínicos é uma das mais importantes
para triagem. Texto truncado ou caracteres espúrios prejudicam legibilidade,
embedding e rastreabilidade, mesmo quando seção e limite de tokens estão
corretos.

**O que resolveria.** Criar uma pequena amostra dourada de trechos extraídos
e comparar, em rodada isolada, ajustes determinísticos ou outro extrator de
PDF. Critério: headings e passagens clínicas pré-registradas do paper devem
ser preservados sem texto inventado, e a mudança deve melhorar ou manter a
régua de recuperação.

**Atualização em 07/09 — em andamento.** A
[rodada 3 do trilho A](vini/2026-09-07-03-extracao-cientifica-layout-aware.md)
adotou PyMuPDF com blocos/coordenadas e fallback para `pypdf`. No paper real,
removeu 15 headers, seis captions e quatro blocos editoriais, recompôs a ordem
das 15 páginas multicoluna, corrigiu temperaturas para `°C` em contexto
inequívoco e normalizou ligaturas. `Clinical signs` agora começa na primeira
sentença completa disponível, sem inventar o prefixo ausente no próprio PDF.

O item não é fechado porque o arquivo-fonte ainda codifica algumas palavras
sem espaço nem pista geométrica, como `experimentallyinduced` e
`heatstrokeassociated`. Separá-las exigiria inferência lexical ou um
dicionário, deliberadamente evitados nesta rodada. O critério residual é
encontrar uma correção genérica com evidência estrutural — ou manter essa
limitação explicitamente aceita na curadoria.

---

### B-36

**Rótulo de título e seção embutido no texto do chunk chega ao prompt**

**Identificado por:** João (B2) · **Onde:** [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md), 11/09 · **Responsável:** Trilho A · **Prioridade:** Alta · **Status:** Aberto

**O que observamos.** O chunking novo monta cada chunk como
`"Document title: {título}\nSection: {seção}\n\n" + texto` e grava esse texto
inteiro como documento no ChromaDB. O `RetrievalClient` devolve exatamente
isso em `content`, e o prompt do B2 renderiza `[n] {título} — {content}`.
Depois da reindexação, o modelo vai ler o título duas vezes, um rótulo em
inglês dentro de protocolos em português e, nos sete protocolos antigos, que
caem no fallback de seção única, a palavra `Document` como nome de seção.
Hoje não tem efeito porque a base não foi reindexada.

**Por que importa.** O contrato A → B2 em `docs/CONTRATOS.md` diz que
`content` é "o texto que entra no prompt"; a semântica mudou sem aviso. A
intenção é boa — título e seção participarem do embedding vem do diário
antigo do projeto. Mas qualquer medição com RAG sobre a base nova vai
misturar o efeito do rótulo com o efeito da recuperação, e um modelo de 3B
lendo ruído em inglês não ajuda a decisão.

**O que resolveria.** Separar o que se embeda do que se exibe. Duas opções,
à escolha do dono: gravar o corpo limpo em `documents` e fornecer ao Chroma
os vetores calculados sobre `prefixo + corpo`; ou gravar o corpo limpo num
metadado (`body`) e o `RetrievalClient` devolvê-lo como `content`. Critério:
um chunk recuperado da base nova chega ao prompt sem `Document title` nem
`Section` no início, e o vetor continua considerando título e seção.

---

### B-37

**Virada da base: trocar os 18 trechos pela base nova sem perder comparabilidade**

**Identificado por:** João (B2) · **Onde:** [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md), 11/09 · **Responsável:** Trilho A (passos 2 e 4) + Time (passo 3) + B2 (passos 1, 5 e 6) · **Prioridade:** Alta · **Status:** Em andamento — passo 1 concluído em 11/09; passos 2 e 3 pendentes

**O que observamos.** Em 07/09 o trilho A substituiu a receita de chunking
(fatias de 1200 caracteres → seções, frases e tokens). Os mesmos sete PDFs,
processados hoje, produzem outros trechos, com outros identificadores e
outros vetores — cerca de 73 no lugar de 18, mais 186 do paper novo. **A
receita antiga não existe mais no código**, então a base de 18 trechos só
sobrevive nas máquinas que já a tinham.

O trilho A deliberadamente não reindexou, esperando a régua de recuperação, e
está certo nisso. Mas essa proteção é uma convenção: qualquer um que rode
`ingest_documents` — inclusive seguindo o README raiz, que até 11/09 mandava
fazer isso — troca a base sem aviso.

**Por que importa.** Não é burocracia de "marcar uma data". São três
problemas concretos se a virada acontecer em uma máquina de cada vez, sem
ordem:

1. **Máquinas diferentes gerariam bases diferentes.** A imagem Docker do B2
   não tem `pymupdf` (o `requirements.txt` mudou em 07/09 e as imagens não
   foram reconstruídas). Ali o ingestor cai no fallback `pypdf` com aviso, e
   o paper sai com 200 trechos e os artefatos do [B-35](#b-35), em vez dos
   186 limpos que o trilho A mediu. Duas bases, um só nome, e o time achando
   que mede a mesma coisa.
2. **O [B-36](#b-36) ainda está aberto.** Cada trecho novo carrega um rótulo
   em inglês colado no início do texto, e esse texto é o que chega ao prompt
   do classificador. Virar antes de corrigir significa medir um defeito
   conhecido e remedir tudo depois.
3. **As rodadas citadas dependem da base antiga.** `r3_marco1`,
   `r3c_um_trecho` e `b04_confirmacao` foram medidas sobre os 18 trechos, e
   os números com RAG do README da raiz vêm delas. Sem um caminho de volta,
   elas deixariam de ser reproduzíveis no instante da primeira reindexação.

**O que resolveria.** Esta sequência, nesta ordem. Cada passo tem um dono e
um motivo; o que está entre parênteses é o que quebra se ele for pulado.

| # | Passo | Dono | Por quê |
|---|---|---|---|
| 1 | ✅ **Retrato da base antiga versionado** em [`data/evaluation/cited/base-2026-09-04-18-chunks/`](../data/evaluation/cited/base-2026-09-04-18-chunks/README.md), com os vetores, os dois hashes e um script de restauração testado | B2 (feito 11/09) | É a única parte irrecuperável. Sem ela, as três rodadas citadas morrem na primeira reindexação |
| 2 | **Corrigir o [B-36](#b-36)**: separar o que se embeda do que se exibe | Trilho A | Virar antes é medir um defeito conhecido, e depois medir tudo de novo |
| 3 | **Torch CPU no `Dockerfile`** e reconstruir a imagem nas três máquinas | Time ([B-34](#b-34)) | Sem isso, as bases saem diferentes por máquina (problema 1). O rebuild sem o ajuste é o que levou o disco a 99% e derrubou o Docker do trilho A |
| 4 | **`ingest_documents --reset`** em cada máquina, conferindo que o `content_sha256` do `/health/fingerprint` é o mesmo nas três | cada um | O `--reset` também limpa registros de documentos que saíram da pasta; comparar o hash é o que prova que a virada foi igual para todos |
| 5 | **B2 remede `naive_rag` e `rag_query`** na base nova e cita as rodadas | B2 | Os números com RAG do README e das evidências passam a descrever a base nova |
| 6 | **Registrar a virada**: README raiz e este item com "a partir de DD/MM a base é a nova, porque…"; as evidências anteriores ganham nota de validade | B2 | O que o João pediu desde o começo: virar e documentar, não virar em silêncio |

**Critério.** As três máquinas mostram o mesmo `content_sha256` no
`/health/fingerprint`; o retrato da base antiga está citado e restaurável; o
README raiz diz a data da virada e o motivo; e existe ao menos uma rodada
citada medindo a base nova.

**O que já foi feito (11/09).** Passo 1 concluído: o retrato está versionado
com os 18 trechos, os vetores de 384 dimensões, os dois hashes
(`eeba9f51…` e `89a215ac…`) e a versão do ChromaDB que o gravou. O caminho de
volta foi **testado de ponta a ponta** — apagar a coleção e restaurar
devolveu os mesmos dois hashes, e a busca continuou trazendo o protocolo
certo em primeiro lugar. O README raiz também deixou de prometer "18
trechos" e passou a avisar que o comando gera a base nova.

**Nota sobre a decisão anterior.** Antes desta reescrita, o item dizia
"o trilho A marca a data da virada". A palavra "data" deu a impressão de
cerimônia, e não é: a virada é virar e documentar, como o João apontou. O que
existe é a ordem acima — e ela pode acontecer em poucos dias, assim que os
passos 2 e 3 estiverem prontos.

---

### B-38

**Runner não confere a base antes de uma rodada com recuperação**

**Identificado por:** João (B2) · **Onde:** [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md), 11/09 · **Responsável:** Trilho B2 · **Prioridade:** Alta · **Status:** Resolvido em 11/09

**O que observamos.** O preflight do `run_evaluation.py` checa `/health/`,
faz o aquecimento e grava o fingerprint no manifesto — mas não decide nada
com ele. Com `retrieval_enabled` ligado e `chunk_count` zero, a rodada roda
até o fim e sai como sucesso. Na prática é um `llm_only` rotulado como
`naive_rag`. É o mesmo buraco que o [B-33](#b-33) aponta no healthcheck.

**Por que importa.** Base vazia é o estado padrão de um clone limpo
([B-12](#b-12)), e a virada da base ([B-37](#b-37)) vai mudar o hash sem
aviso. Uma rodada citada com a base errada é um número errado no TCC.

**O que resolveria.** Abortar no preflight se a busca estiver ligada e a
base estiver vazia, com mensagem dizendo o comando de ingestão. Uma opção
`--expect-base-hash` que aborta se o hash da base não for o esperado, para
toda rodada que vá ser citada. Critério: `naive_rag` contra base vazia
aborta antes da primeira linha; com o hash errado, aborta mostrando os dois.


**Como foi resolvido (11/09).** `conferir_base()` no preflight do runner,
chamada em dois momentos: o `--expect-base-hash` antes do aquecimento
(barato, evita pagar o carregamento do modelo para descobrir que a base é
outra) e a checagem de base vazia depois dele, contra o `config` **efetivo**
ecoado pela API — o modo legado desliga a busca no servidor, e ali base
vazia não é problema. O hash declarado entra no manifesto. Sete testes em
`scripts/tests/test_run_evaluation.py`. Não cobre conferir o conteúdo
([B-40](#b-40)) nem obrigar a opção nas rodadas citáveis
([B-39](#b-39)).

---

### B-39

**`--expect-base-hash` é opcional e depende de disciplina**

**Identificado por:** João (B2) · **Onde:** [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md), 11/09 · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** A opção que confere a base é opcional de propósito:
obrigar quebraria um smoke rápido, e a primeira medição de uma base nova não
tem hash conhecido para declarar. O efeito é que nada impede uma rodada ser
citada numa evidência sem ter conferido a base.

**Por que importa.** É a mesma classe de problema do [B-37](#b-37): uma
convenção que o código não garante. Em outubro, montando a matriz de
ablação, uma rodada citada sobre a base errada seria um número errado no
artigo — e o `compare` só denuncia se alguém comparar.

**O que resolveria.** Uma regra que pegue as rodadas do artigo sem atrapalhar
as exploratórias. A candidata é exigir a opção quando `--subset full`, com
um `--no-expect-base-hash` explícito para a primeira medição de uma base
nova. Critério: uma rodada `full` sem hash declarado não começa, e a
mensagem diz como declarar o hash atual.

---

### B-40

**A conferência de base olha o recorte, não o conteúdo**

**Identificado por:** João (B2) · **Onde:** [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md), 11/09 · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** O `--expect-base-hash` compara o `chunk_ids_sha256`,
que muda quando o recorte muda. Duas bases com o mesmo recorte e textos
diferentes — o caso que o `content_sha256` passou a detectar na mesma rodada
([B-29](#b-29)) — passariam pela conferência sem aviso.

**Por que importa.** É o buraco que o B-29 fechou no retrato, mas que a
trava do runner ainda não usa. Reescrever um protocolo sem mudar o número de
trechos continua invisível **na hora de rodar**; só aparece depois, no
`compare`.

**O que resolveria.** Aceitar também o hash de conteúdo na conferência.
Ficou adiado porque as seis rodadas citadas até 05/09 não têm o campo — o
retrato nasceu em 11/09 —, e exigi-lo agora tornaria irreproduzível
justamente a linha de base do Chain-of-Thought. Critério: quando todas as
rodadas citadas tiverem `content_sha256` no manifesto, a opção passa a
comparar os dois hashes.

---

### B-41

**O julgamento de "risco à vida" não se resolve por âncoras no prompt**

**Identificado por:** João (B2) · **Onde:** [rodada 8](joao/2026-09-11-08-chain-of-thought.md), 11/09; reescrito na [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md), 12/09 · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto — bloqueado por [B-45](#b-45) e [B-05](#b-05)

**O que observamos.** Ao preencher o checklist do Chain-of-Thought, o modelo
marca **claudicação** como risco à vida em **24 de 25** ocorrências (contagem
pelo método declarado na rodada 9: primeira marca por sinal, primeira
repetição). Os outros quatro termos leves ele marca bem. Como 21 das 27
linhas leves contêm claudicação, e a regra é "um sinal de risco basta", um
único termo contamina 78% da classe.

**Por que a proposta original não serve.** A primeira versão deste item
propunha âncoras de calibração no prompt, do tipo "mancar não é risco à
vida; convulsão é". Isso é **vazamento por construção**: os cinco termos
leves *são* a classe não emergência do conjunto de avaliação, então
qualquer exemplo que os cite entrega a resposta. E dividir as 15 combinações
distintas em desenvolvimento e teste deixa os dois lados pequenos demais.

**O que mudou no diagnóstico.** A [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md) mostrou que a marcação
errada é a **segunda** causa, não a primeira, e que ela sequer é um
julgamento estável: no braço de controle, as mesmas marcações invertem
conforme a classe já decidida (febre como risco à vida: 2 de 23 com o
raciocínio antes, 22 de 23 com o raciocínio depois). Não há uma escala
clínica para calibrar — há texto gerado para combinar com a conclusão.

**O que resolveria.** Duas rotas, nenhuma por prompt: (1) tirar o julgamento
do modelo, com uma lista de sinais de alerta vinda dos protocolos e validada
pela especialista decidindo em código; ou (2) dar ao modelo a evidência
recuperada que o artigo previa ([B-03](#b-03)). Em qualquer caso, um
conjunto de desenvolvimento separado ([B-45](#b-45)) é pré-requisito.
---

### B-42

**A técnica e o modelo estão confundidos: o CoT nunca rodou com modelo maior**

**Identificado por:** João (B2) · **Onde:** [rodada 8](joao/2026-09-11-08-chain-of-thought.md), 11/09 · **Responsável:** Time (decisão de escopo) · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** O Chain-of-Thought foi medido apenas com
`llama3.2:3b`, e o resultado foi fortemente negativo: −44,7 pontos de
acurácia balanceada, com a classe não emergência indo a zero.

Duas hipóteses explicam esse resultado igualmente bem:

1. A técnica não serve para triagem veterinária.
2. A técnica exige um julgamento clínico que um modelo de 3 bilhões de
   parâmetros não tem ([B-41](#b-41)).

As duas fazem exatamente a mesma previsão nesta rodada, e nada nos dados
atuais as separa.

**Por que importa.** É a diferença entre o TCC afirmar "Chain-of-Thought não
ajuda na pré-triagem" e "Chain-of-Thought não ajuda com modelo pequeno". A
primeira é uma afirmação sobre a técnica que os dados não sustentam; a
segunda é o que foi medido. A literatura reporta ganhos de CoT em modelos
grandes, então a leitura sem essa separação será questionada na banca.

**O que resolveria.** Rodar `llm_only_cot` com um modelo de 7 a 8 bilhões
(por exemplo `llama3.1:8b`), com o mesmo prompt e o mesmo conjunto. Se o
ganho aparecer, a conclusão é sobre o tamanho do modelo; se não aparecer, é
sobre a técnica. Critério: uma rodada citada com modelo maior, e o texto do
artigo escolhendo a afirmação que os dados sustentam.

**A decisão é do time**, não do trilho: o projeto é local-first e declara
`llama3.2:3b`. Rodar um modelo maior só para o estudo de ablação é
compatível com isso (a medição não precisa ser a configuração de produção),
mas muda o tempo das rodadas e exige espaço em disco.

---

### B-43

**A etapa de decisão não é reproduzível entre sessões**

**Identificado por:** João (B2) · **Onde:** [rodada 8](joao/2026-09-11-08-chain-of-thought.md), 11/09 · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** Repetindo o preset `llm_only` sete dias depois, com o
mesmo modelo, o mesmo prompt (hash conferido), a mesma base e a mesma seed:

| | |
|---|---|
| Linhas com saída **byte a byte** idêntica | 31 de 98 |
| Linhas com a mesma classificação | 96 de 98 |

Duas linhas não emergência viraram emergência (843 e 845). A
[rodada 6](joao/2026-09-05-06-determinismo-da-consulta.md) mediu que a etapa
de decisão era determinística **dentro** de uma mesma execução, com zero
exceções — este é outro recorte, entre execuções separadas por dias.

**Por que importa.** É a mesma assinatura de ruído numérico de GPU descrita
na hipótese H1 da rodada 6, e ela não poupa a etapa de decisão. Muda o que
"reproduzir uma rodada" significa: o texto não se reproduz, a decisão quase
sempre sim. Um efeito pequeno, da ordem de 2 a 3 linhas, pode ser ruído de
sessão e não a mudança testada.

**O que resolveria.** Repetir o `llm_only` em três dias diferentes e reportar
a faixa de linhas que mudam, como se fez com o braço de consulta no
[B-27](#b-27). Critério: uma faixa registrada, e uma regra escrita dizendo a
partir de quantas linhas uma diferença deixa de ser atribuível a ruído de
sessão. Hoje não bloqueia nada: o efeito medido na rodada 8 foi 20 vezes
maior que esse ruído.

---

### B-44

**Divergências entre o artigo do TCC1 e o sistema construído**

**Identificado por:** João (B2) · **Onde:** [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md), 12/09 · **Responsável:** Time (escrita do TCC2) · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** Lendo o artigo de ponta a ponta e comparando com o
repositório, cinco itens prometidos não existem no código:

| Prometido no artigo | Estado |
|---|---|
| Orquestração por **LangChain** | Nunca entrou. O código fala direto com Ollama e ChromaDB. A única menção no repositório é uma nota do diário de maio |
| **LightRAG / grafo de conhecimento** e raciocínio multi-hop | Não existe. A recuperação é vetorial simples |
| **Re-ranking por cross-encoder** | O `RerankerClient` apenas reordena pelo mesmo score da busca |
| **RAGAs** (faithfulness, answer relevance, context precision) | Não integrado. Já registrado em [B-21](#b-21) |
| Os **datasets** como fonte de conhecimento indexada | Hoje servem só à avaliação — e **deve continuar assim**, ver abaixo |

**Por que importa.** O TCC2 descreve o que foi construído; divergir do plano
é normal e esperado num projeto de pesquisa. O problema não é divergir, é
divergir **sem registro**: a banca vai perguntar, e hoje não existe uma
justificativa escrita para nenhum dos cinco.

Sobre o último item, vale dizer que a divergência foi uma **melhoria**: os
datasets são o conjunto de avaliação, ou seja, a prova. Indexá-los como
conhecimento faria o sistema acertar por consulta à chave de resposta. A
base foi construída a partir de protocolos, o que separa prova de fonte.

**O que resolveria.** Um parágrafo por item no TCC2, dizendo o que mudou e
por quê. Para o LangChain, a justificativa disponível é: o estudo de ablação
exige controle explícito sobre o texto exato enviado ao modelo, a ordem dos
campos na saída estruturada, os parâmetros de geração e a contagem de
tentativas — o retrato do sistema (`/health/fingerprint`) e o runner são
construídos sobre esse controle. Critério: nenhuma promessa do artigo fica
sem correspondência ou sem justificativa no texto final.

**Também entra aqui** a leitura qualitativa das 39 linhas que mudaram entre
a linha de base e o Chain-of-Thought: material direto para a seção de
resultados, com os dados já em `data/evaluation/cited/`.

---

### B-45

**Não há conjunto de desenvolvimento: todo ajuste de prompt é feito no conjunto de teste**

**Identificado por:** João (B2) · **Onde:** [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md), 12/09 · **Responsável:** Trilho B2 · **Prioridade:** Alta · **Status:** Aberto

**O que observamos.** Existe um único conjunto de 98 relatos, usado ao mesmo
tempo para desenvolver e para medir. O prompt `v1_grounded` foi iterado
sobre ele na rodada 3, de 0,572 para 0,893 de acurácia balanceada. O
Chain-of-Thought teve duas iterações de prompt medidas nos mesmos 98 relatos
na rodada 8, e uma terceira tentativa foi revertida por piorar.

**Por que importa.** Isso é ajuste ao conjunto de teste. Duas consequências
concretas:

1. Comparar um prompt afinado no conjunto com um prompt novo, **no mesmo
   conjunto**, favorece o primeiro. Parte da diferença entre a linha de base
   e o CoT pode ser isso, e não a técnica.
2. Qualquer melhoria futura de prompt herda o problema. As âncoras de
   calibração do [B-41](#b-41) são o caso extremo: os cinco termos leves
   **são** a classe leve, então um exemplo que os cite é vazamento por
   construção.

**O que resolveria.** Separar um conjunto de desenvolvimento antes do
próximo ajuste de prompt. Com 98 linhas e 15 combinações distintas na classe
leve, dividir o conjunto atual deixa os dois lados pequenos demais — então a
saída provável é gerar relatos de desenvolvimento novos, o que liga este
item ao [B-05](#b-05). Critério: nenhum ajuste de prompt é medido no mesmo
conjunto em que foi desenvolvido, e as evidências dizem qual conjunto foi
usado para cada coisa.

---

### B-46

**Teste limpo do efeito da ordem dos campos**

**Identificado por:** João (B2) · **Onde:** [rodada 9](joao/2026-09-12-09-autopsia-do-cot.md), 12/09 · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto — aprovado pelo João em 12/09

**O que observamos.** A rodada 8 comparou o braço com raciocínio antes
contra o braço com raciocínio depois e concluiu que a ordem importa. Mas
essa comparação carrega **três** mudanças de uma vez em relação à linha de
base: o texto do checklist, um campo novo na saída e um prompt 56% maior
(432 para 675 tokens). Só a comparação entre os dois braços de CoT isola a
ordem, e mesmo ela difere numa frase do prompt.

**Por que importa.** "A ordem dos campos na saída estruturada muda a
decisão" é uma afirmação forte e transferível — vale para qualquer sistema
que use saída restrita por gramática, não só para triagem. Se for para o
TCC, precisa de um teste com uma variável.

**O que resolveria.** O formato atual da saída já tem `sinais_de_alerta`
declarado **depois** de `classificacao`, e ele carrega uma rubrica leve
("apenas os sinais preocupantes que aparecem no relato"). Mover **apenas
esse campo** para antes de `classificacao`, sem alterar uma palavra do
prompt, dá o contraste mais limpo possível: mesma instrução, mesmo tamanho,
mesma rubrica, só a ordem muda. Critério: uma rodada `llm_only` com o campo
movido, comparada com a rodada `m0_llm_only` de 11/09. Custo estimado: 4
minutos de GPU.

---

### B-47

**O retrato do sistema inclui estado de momento, e isso gera aviso falso**

**Identificado por:** João (B2) · **Onde:** [rodada 10](joao/2026-09-12-10-corte-de-relevancia.md), 12/09 · **Responsável:** Trilho B2 · **Prioridade:** Baixa · **Status:** Aberto

**O que observamos.** Ao comparar duas rodadas da mesma sessão, o `compare`
avisou que o sistema "não era o mesmo", apontando
`model.loaded_in_vram_bytes`: 2.554.708.622 contra nulo. É a memória de
vídeo ocupada pelo modelo no instante da chamada, que varia conforme ele já
estava carregado ou não.

**Por que importa.** O aviso de fingerprint existe para dizer "o sistema
mudou entre estas duas rodadas". Um campo que muda sozinho, sem nada mudar,
faz o aviso disparar sem motivo — e um aviso que aparece sempre deixa de ser
lido. Foi exatamente o cuidado que motivou, na rodada 7, comparar só as
chaves presentes nos dois manifestos.

**O que resolveria.** Separar no retrato o que **identifica** a versão
(nome do modelo, digest, versão do Ollama, hashes) do que descreve o
**momento** (memória ocupada, se estava carregado). O segundo grupo continua
gravado, porque é útil para ler latência, mas sai da comparação. Critério:
duas rodadas seguidas na mesma máquina, sem nenhuma mudança, não geram aviso
de fingerprint.

---

### B-48

**O gabarito da régua de recuperação é provisório e precisa de validação**

**Identificado por:** João (B2) · **Onde:** [rodada 11](joao/2026-09-12-11-regua-de-recuperacao.md), 12/09 · **Responsável:** Trilho A + especialista · **Prioridade:** Alta · **Status:** Aberto

**O que observamos.** A régua de recuperação foi construída pelo trilho B2
em nome do trilho A, porque estava bloqueando dois trilhos. O instrumento
está pronto e a linha de base medida, mas **quem decide qual protocolo é o
certo para cada relato é quem cuida da base**, com a especialista. O
`cases.csv` traz a coluna `marked_by` dizendo "B2 — provisório, aguardando
validação do trilho A" e uma coluna `note` com o motivo clínico de cada
marcação, para o trilho A discordar de uma linha sem refazer o resto.

**Por que importa.** Enquanto o gabarito não for validado, os números são do
B2, não do time — e a régua mede o que **eu** acho que é o protocolo certo.
Errei duas marcações em dezoito lendo com atenção (b12 e b15, no primeiro
rascunho), o que sugere que uma leitura clínica vai achar mais.

**O que resolveria.** O trilho A revisa as 18 linhas com a especialista, com
atenção a três pontos: (1) os quatro casos marcados como "sem cobertura" —
b12 dilatação-torção gástrica, b14 neonato, b15 obstrução uretral em **cão**
(o protocolo da base é de gatos) e b17 emergência neurológica; (2) b16,
picada de abelha com edema de face, apontado para dificuldade respiratória
por risco de via aérea e **não** para trauma; (3) b10, "manca de leve depois
de correr", marcado como caso leve. Critério: `marked_by` passa a dizer
"validado pelo trilho A em DD/MM", e a linha de base é remedida se alguma
marcação mudar.

**Efeito colateral útil:** os quatro casos sem cobertura são a lista dos
protocolos que faltam na base, e alimentam direto a curadoria
([B-03](#b-03)).

---

### B-49

**A régua de recuperação mede pouco enquanto a base e o conjunto de casos forem pequenos**

**Identificado por:** João (B2) · **Onde:** [rodada 11](joao/2026-09-12-11-regua-de-recuperacao.md), 12/09 · **Responsável:** Trilho A + B2 · **Prioridade:** Média · **Status:** Aberto

**O que observamos.** A régua funciona e já produziu dois achados, mas três
dos seus números ainda não sustentam conclusão forte, e o motivo é o mesmo
nos três: **a base tem 7 documentos e o conjunto tem 18 casos, dos quais só
9 entram na conta principal**.

| Número | Por que ainda mede pouco |
|---|---|
| **Recall@5 = 1,000** | A busca devolve 5 trechos, em média 4,4 documentos distintos, de uma base de 7. "O certo está entre os cinco" é quase geométrico: escolhendo 5 dos 7 ao acaso o recall já seria ≈ 0,71 |
| **Precision@1 = 0,556** | São 5 acertos em 9 casos. Um caso mudando move o número em 11 pontos — diferenças menores que isso entre duas rodadas não significam nada |
| **Silêncio nos leves = 5/5** | Nenhum caso passa do corte de 0,70, então a busca "acerta" os leves por estar sempre quieta. A taxa não mede discernimento |

**Por que importa.** O risco não é o instrumento estar errado — é alguém
ler 1,000 como "a recuperação está resolvida" e desprioritizar a ampliação
da base ([B-03](#b-03)) justamente por causa do número que a base pequena
produziu. O relatório da rodada já emite as duas ressalvas sozinho, mas a
ressalva vive no relatório, não em quem cita o número.

**O que resolveria.** Não é conserto de código; é dado. Com a base ampliada
e o conjunto maior, cada um destes destrava sozinho:

1. **Base acima de ~20 documentos** ([B-03](#b-03)): Recall@5 volta a
   informar, porque 5 de 20 deixa de ser quase o acervo inteiro. Só então
   vale comparar o recall entre duas receitas de chunking.
2. **Mais casos com protocolo** — de 9 para 25 ou 30: Precision@1 passa a
   distinguir diferenças de 5 pontos, e aí faz sentido medir re-ranking
   (entrega 6 do trilho A) por ele. Os relatos podem vir do mesmo lugar que
   os atuais, escritos em português de tutor.
3. **Algum caso passando do corte**: as taxas de silêncio passam a medir
   discernimento, e a régua ganha a capacidade de escolher o limiar, que é a
   parte do [B-11](#b-11) que ficou com o trilho A.
4. **Casos de espécie e de idade** (hoje só b15 toca nisso): mede se a busca
   distingue cão de gato, filhote de idoso — coisa que ela hoje
   demonstravelmente não faz.

Critério de fechamento: uma rodada da régua sobre a base ampliada em que
`share_cases_above_threshold` seja maior que zero e `n_com_protocolo` seja
pelo menos 25.

**Enquanto isso**, a régua já serve para o que foi construída: comparar
**duas versões do mesmo sistema sobre os mesmos casos** — antes e depois da
virada da base, com e sem re-ranking, com e sem reescrita de consulta. Essa
comparação pareada não depende de a base ser grande.

---

## Resolvidos

| ID | Item | Fechado em | Evidência |
|---|---|---|---|
| [B-32](#b-32) | Upload de voz aceita caminho e tamanho controlados pelo cliente | 08/09 | [rodada 2 do Ryu](ryu/2026-09-08-02-endurecimento-do-upload-de-voz.md) |
| [B-13](#b-13) | Whisper com três implementações e sem benchmark | 08/09 | [rodada 3 do Ryu](ryu/2026-09-08-03-whisper-unico-e-wer.md) |
| [B-25](#b-25) | O compare não detecta mudança de código entre rodadas | 11/09 | [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md) |
| [B-29](#b-29) | Fingerprint da base não identifica conteúdo nem embedder | 11/09 | [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md) |
| [B-38](#b-38) | Runner não confere a base antes de uma rodada com recuperação | 11/09 | [rodada 7 do João](joao/2026-09-11-07-endurecimento-do-instrumento.md) |
