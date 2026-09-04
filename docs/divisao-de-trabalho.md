# Divisão de Trabalho — Três Trilhos (v2)

> Escrito em 31/08/2026, sobre o estado atual do projeto (commit `397fdbc`).
>
> **Revisão v2:** o antigo trilho C (avaliação/produto/operação) foi congelado
> por decisão do time — a prioridade agora é tração no núcleo do produto.
> O antigo trilho B foi dividido em dois. A avaliação não sumiu: ela virou
> responsabilidade distribuída **com dono único da régua** e um ritual de
> registro a cada rodada de implementação.

## A lógica da divisão

1. **Um trilho por pessoa, cortado nas emendas naturais do pipeline:**
   antes da busca (B1), a busca em si (A), depois da busca (B2).
   Assim quase nenhum arquivo tem dois donos, e conflito de merge vira exceção.
2. **Cada trilho tem missão própria e régua própria.**
   Ninguém espera código dos outros para avançar — o que cruza a fronteira
   é um formato de dados combinado (contrato), não código.
3. **Uma régua só, com dono.** Os números que valem são os do runner
   compartilhado (dono: B2) e da régua de recuperação (dono: A).
   Registro de rodada sem número da régua não conta como resultado.
4. **Produto e operação ficam na geladeira até outubro** — congelados de
   propósito, com data de volta (lista no fim).

---

## Trilho A — Recuperação & Conhecimento *(inalterado da v1)*

*Para quem já está na busca semântica (SBERT + ChromaDB).*

**Missão:** dado um relato de tutor, os trechos certos da base aparecem nas
primeiras posições — comprovadamente, não no olhômetro.

**Responsabilidades:**
- Criar a **régua de recuperação**: conjunto fixo de relatos de teste com o
  documento esperado para cada um. É ela que mede o trilho A **e o trilho B1**.
- Melhorar a **preparação dos documentos e o chunking** (plano do handover de
  30/08) e recriar a base.
- Melhorar a **ordenação**: fusão melhor das buscas do multi-query e
  re-ranking de verdade (hoje é só casca).
- **Comparar modelos de embedding** e decidir com número.
- **Curar a base real** com a especialista — os protocolos atuais são
  sintéticos de teste. Depende de gente, não de código: começar cedo.
- Fase 2: LightRAG / grafo de conhecimento.

**Entregas imediatas:** (1) régua rodando com número de partida; (2) base
reprocessada com antes/depois; (3) decisão do modelo de embedding.

**Não é deste trilho:** prompts, geração, avaliação de sistema.

**Pastas:** `backend/app/database/`, `backend/data/documents/`,
`retrieval_client`, `reranker_client`.

---

## Trilho B1 — Consulta *(do relato do tutor até a busca)*

*Para quem já fez Whisper, Query Rewriting e Multi-Query — continua no próprio código.*

**Missão:** maximizar a chance de a busca encontrar o documento certo a partir
de um relato leigo, por texto ou por voz.

**Responsabilidades:**
- **Query Rewriting como "tradutor clínico"**: linguagem leiga → terminologia
  veterinária, como o artigo descreve (hoje o prompt só pede "clareza").
- **Multi-Query com saída limpa** (sem a numeração que o modelo devolve entrar
  na busca) e sem variações duplicadas.
- **HyDE**, que ainda não existe.
- **Whisper consolidado em uma implementação só** (hoje são três, com dois
  tamanhos de modelo) e qualidade de transcrição medida com áudios gravados
  pelo próprio time.
- **Flags de liga/desliga das etapas de consulta** (rewriting, multi-query,
  HyDE) — cada medição ligado × desligado já é uma linha do estudo de ablação.

**Régua do trilho:** a régua de recuperação do trilho A. B1 melhora a
*consulta*; A melhora a *base e a busca*; o número é o mesmo — documento certo
na primeira posição.

**Entregas imediatas:** (1) Whisper único com qualidade medida (não depende de
ninguém — bom primeiro passo); (2) QR clínico medido ligado × desligado na
régua do A; (3) HyDE primeira versão medida.

**Não é deste trilho:** prompt de triagem, geração, orquestração do pipeline,
chunking/embeddings.

**Pastas:** `clients/query_client`, `ai/`, `api/voice`.

---

## Trilho B2 — Decisão *(da evidência recuperada até a resposta)*

*Para quem estava sem escopo — ganha o coração do produto e a régua de sistema.*

**Missão:** substituir a resposta simulada pela **decisão real de triagem**,
ancorada nos documentos e estruturada — e ser o dono da régua que mede o
sistema inteiro.

**Responsabilidades:**
- **Matar o mock:** o LLM classifica (EMERGENCIA / NAO_EMERGENCIA / INCERTO)
  usando os documentos recuperados, devolvendo JSON estruturado
  (classificação, justificativa, sinais de alerta, recomendação, fontes).
  Unificar com a classificação antiga que ficou isolada fora do pipeline.
- **Chain-of-Thought e Self-Refine de verdade** (hoje o self-correct não faz nada).
- **Orquestração do pipeline** e as flags das etapas de geração.
- **Runner de métricas compartilhado** (herdado do antigo C): consertar o
  script que aponta para o endpoint desativado, rodar o dataset contra a API,
  calcular acurácia/recall/F1 + tempo de resposta, salvar resultados
  versionados. É a régua oficial do time — os números de todos saem daqui.
- **Higiene do repositório** (herdada do antigo C, dia 1): des-rastrear os
  arquivos gerados que causam conflito entre as máquinas; exemplo de
  configuração; centralizar endereços/modelo que hoje estão escritos à mão em
  vários arquivos.

**Régua do trilho:** acurácia, recall por classe e F1 contra o baseline já
medido — 70,41% de acurácia, com o chute ingênuo em 72%. O objetivo do RAG é
mover esse número; o antes/depois é o resultado central do artigo.

**Entregas imediatas:** (1) higiene do repo mergeada; (2) runner re-medindo o
baseline atual, provando que é reproduzível; (3) mock morto — `/chat`
respondendo com classificação ancorada citando fontes.

**Não é deste trilho:** reescrita de consulta, Whisper, chunking/embeddings.

**Pastas:** `clients/llm_client`, `pipeline/`, `schemas/`, `llm.py` (absorver),
`scripts/` (runner).

---

## O ritual de cada rodada (o "diário de experimentos")

A cada rodada de implementação, quem fez registra um arquivo em
[`evidencias/<seu-nome>/`](../evidencias/README.md), respondendo sempre:

```
# Título da rodada
Data · Trilho · Commits

## O que foi feito
## Por quê                     (o problema concreto que resolve)
## Resultado esperado          (escrito ANTES de medir)
## Resultado obtido            (com números; resultado negativo também conta)
## O que mudou no repositório  (arquivos + link do commit)
## Próximo passo
```

Cada um escreve **só na própria pasta** — três pessoas editando o mesmo arquivo
de diário disputariam as mesmas linhas toda semana.

Três regras para os registros valerem alguma coisa:

1. **Número da régua compartilhada, sempre** — sem número, é opinião.
2. **Uma mudança por rodada** (ou o resultado não diz qual mudança causou o quê).
3. **Revisão cruzada na sync semanal** — cada um lê os registros dos outros.

O "resultado esperado" precisa ser escrito antes de medir: depois do resultado
é fácil convencer a si mesmo de que era o que se previa, e é justamente a
diferença entre os dois que tem valor para o TCC.

**Atenção à diferença:** este diário **complementa** o estudo de ablação do
artigo, não o substitui. O estudo formal é a matriz sistemática (cada flag
ligada/desligada × dataset completo) — as flags vão sendo construídas de graça
durante o desenvolvimento, e em outubro a matriz roda em ~1 semana com os três.
O diário conta a história; a matriz gera a tabela do artigo.

---

## Contratos entre os trilhos

Uma conversa de 30 minutos fecha isto; depois só muda por PR marcando o dono
do outro lado.

1. **Consulta pronta para busca** (B1 → A): o formato do que a etapa de
   consulta entrega — lista de variações e, com HyDE, o documento hipotético.
2. **Documento recuperado** (A → B2): os campos que a busca devolve.
3. **Resposta de triagem** (B2 → runner e futuro frontend): o JSON com
   classificação, justificativa, sinais de alerta, recomendação e fontes.
4. **Flags com dono:** B1 (rewriting, multi-query, HyDE) · A (re-ranking) ·
   B2 (CoT, self-refine). Nomes combinados antes de existir código.

## Acordos de trabalho

- Cada trilho edita **só as próprias pastas**; mexeu na pasta alheia, o dono revisa.
- Branch curta por tarefa, PR pequeno, **main sempre rodando**.
- **Arquivo gerado não entra no git** (cache de Python, banco vetorial, uploads).
- Toda melhoria vem com **antes/depois na régua** (é o ritual acima).
- **Evidência por rodada** em `evidencias/<seu-nome>/`, uma por implementação.

---

## Geladeira — congelado de propósito, com data de volta

| Item | Volta quando |
|---|---|
| Frontend da triagem (exibir classificação/justificativa/fontes) | Outubro, quando o JSON do B2 estabilizar |
| RAGAs (métricas de qualidade do RAG) | Outubro — pluga direto no runner do B2 |
| Geolocalização de clínicas + resumo MIST | Outubro — **promessa do artigo, não esquecer** |
| Deploy no VPS | Outubro/novembro |
| Estudo de ablação formal (matriz completa) | Outubro, ~1 semana, os três juntos |

A interface atual de chat continua servindo para desenvolvimento e demo até lá.

## Sequência até novembro

| Quando | O quê |
|---|---|
| 1–7 set | Contratos fechados · higiene do repo (B2) · régua de recuperação de pé (A) · Whisper único (B1) · geração real começando (B2) |
| 8–19 set | **Marco 1 — primeira triagem RAG de ponta a ponta, medida**: relato → classificação ancorada → runner comparando com o baseline de 70,41% |
| 20–30 set | Iteração guiada pelas réguas (A: base/busca · B1: consulta · B2: prompts/refine) |
| Outubro | **Marco 2 — matriz de ablação completa** · sai da geladeira: RAGAs, frontend, geolocalização/MIST, deploy |
| Novembro | **Marco 3 — números congelados**, escrita final |

---

## Diagnóstico em alto nível (graus de atenção)

### 🔴 Vermelho — estrutural, atacar já

| O quê | Situação | Trilho |
|---|---|---|
| Resposta final é simulada | A geração devolve texto fixo; a autocorreção não faz nada; a classificação real ficou isolada fora do pipeline. | B2 |
| Avaliação quebrada | O script de métricas aponta para um endpoint desativado — os números atuais não são reproduzíveis. E nunca houve régua de recuperação. | B2 + A |
| Ranking da recuperação | O documento certo aparece no top-5, mas não em 1º (causas diagnosticadas em 30/08). Sem isso o RAG não ancora nada. | A |
| Classificador perde do chute | 70,41% contra 72% de quem sempre grita "emergência"; quase não reconhece não-emergências. É o número que o RAG existe para mover. | B2 constrói e mede; revisão cruzada dos três |
| Arquivos gerados no git | Caches de Python e áudios versionados = conflito de merge garantido entre 3 máquinas. Correção de 30 minutos. | B2 |

### 🟡 Amarelo — dívida que atrapalha o paralelismo

- **Configuração fragmentada:** endereços e nome do modelo escritos à mão em
  vários arquivos; em Docker uma parte funciona, local outra quebra. (B2)
- **Código morto e duplicado:** três Whispers (B1), dois frontends (geladeira),
  dois schemas de chat (B2), arquivos órfãos. Apagar sem dó — o git guarda.
- **Zero testes automatizados:** o mínimo (schemas, chunking, pipeline com
  fakes) é uma tarde e deixa três pessoas mexerem sem medo. (cada trilho no seu)
- **Query Rewriting / Multi-Query sem medição:** rodam, mas ninguém sabe se
  ajudam. Ligar na régua. (B1)
- **Whisper sem número:** o artigo cita ~97,5%; não existe benchmark. (B1)
- **Base de conhecimento 100% sintética:** curadoria real com a especialista é
  gargalo humano — começar já. (A)
- **Rótulo do data augmentation impreciso:** a geração foi combinatória (bom!),
  mas está rotulada "via LLM". No texto do TCC, descrever o método real.

### 🟢 Verde — está bom, preservar

- Arquitetura em camadas do backend — é o que torna a divisão possível.
- Ingestor de documentos maduro (IDs estáveis, metadados, reprocessamento seguro).
- Disciplina de medição honesta nas anotações — o rigor que banca a seção de
  resultados.
- Diário `anotacoes.md` com handovers — agora evolui para o ritual por rodada.
- Data augmentation controlado com curadoria de especialista.
- docker-compose na medida.

---

## Primeiro passo de cada um

- **A:** escrever o conjunto de relatos de teste (incluindo o caso cebola),
  apontando qual documento deveria vir em 1º; rodar contra a base atual e
  registrar o número de partida.
- **B1:** consolidar o Whisper em uma implementação (não depende de ninguém) e
  escrever o prompt do "tradutor clínico" para medir assim que a régua do A
  existir.
- **B2:** abrir o PR de higiene, apontar o runner para o endpoint novo,
  re-medir o baseline — e começar o prompt de triagem ancorado que mata o mock.
