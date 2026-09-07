# Auditoria do repositório e estado do trilho A

**Data:** 07/09/2026 · **Trilho:** A (Recuperação e Conhecimento) · **Rodada:** 1  
**Commits:** nenhum — registro ainda não commitado

## O que foi feito

Auditoria somente leitura do repositório local e comparação direta com o
remoto. Foram revisados integralmente os documentos de `docs/` e
`evidencias/`, o código do pipeline, a base Chroma local, os metadados dos
documentos, as rodadas citadas e as suítes de testes disponíveis.

O objetivo desta rodada não foi implementar uma solução. Foi construir o
ponto de partida do trilho A, separar descobertas já feitas pelo time de
achados novos e definir uma sequência mensurável para ampliar a base.

## Por quê

O pipeline completo já existe, mas a melhor configuração medida ainda é o
LLM sem RAG. Antes de inserir mais documentos, é necessário saber exatamente
o que já foi diagnosticado, que decisões pertencem a cada trilho e como uma
mudança na base será comparada com o estado anterior.

Sem essa consolidação haveria dois riscos: apresentar como nova uma descoberta
que João ou Ryu já mediram, ou alterar documentos e embeddings sem uma régua
capaz de dizer se a recuperação melhorou.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| Tratar `docs/` e `evidencias/` como fonte normativa | Esses arquivos definem autoria, contratos, métricas, ritual de experimentação e histórico das decisões |
| Não modificar `docs/CONTRATOS.md` | A auditoria não mudou nenhuma interface; mudanças de contrato exigem commit separado e aviso ao dono do outro lado |
| Classificar cada finding como “já conhecido”, “novo” ou “verificação nova de fato conhecido” | Evita apagar a autoria das descobertas anteriores e deixa claro o valor incremental da auditoria |
| Não ingerir os próximos documentos antes da régua do trilho A | Adicionar conteúdo sem Precision@1/MRR produz mudança, mas não evidência de melhoria |
| Levar achados novos que exigem ação ao backlog | É a regra do processo: a rodada registra onde nasceram; o backlog acompanha dono, prioridade e resolução |

## Resultado esperado

Antes da leitura cruzada, a expectativa era encontrar o problema central do
RAG já bem mapeado pelo time — base pequena, chunking ruim e ranking fraco — e
que a auditoria acrescentasse principalmente riscos de reprodutibilidade e de
operação que não aparecem nas métricas de classificação.

Também se esperava confirmar se a base local era a mesma usada nas rodadas
citadas, sem executar nova ingestão.

## Resultado obtido

### Estado verificável do repositório

| Verificação | Resultado |
|---|---|
| Branch | `main` |
| HEAD local e `main` remota | `f242aa1a14b70962dae5dff594c22e893d1e73a1` |
| Diferença local/remoto | 0 commits à frente, 0 atrás |
| Working tree antes da documentação desta rodada | Limpa |
| Histórico da `main` | 45 commits |
| Arquivos rastreados | 175 |
| Tags | 0 |
| Workflows de CI | 0 |
| Banco Chroma local | 18 chunks de 7 PDFs |
| Fingerprint dos IDs da base | `eeba9f51d239e2f6167d18ffe87ef5e6f505de0497b222555a3cb953dd12a914` |

O fingerprint coincide com o manifesto da rodada completa de 05/09. É uma
verificação nova de um estado já documentado: a máquina local tem, no nível
dos IDs, a mesma base de 18 chunks usada naquela medição.

Os 48 testes dos scripts passaram. A suíte do backend não pôde ser executada
nesta máquina porque a `.venv` existente não contém `pytest`,
`pydantic-settings`, `chromadb`, `sentence-transformers` nem `pypdf`. Isso não
é resultado negativo dos testes; é uma limitação do ambiente local. Todos os
arquivos Python rastreados passaram pela análise sintática.

### Findings que a equipe já havia registrado

| Finding confirmado na auditoria | Onde já havia sido descoberto |
|---|---|
| Ligar o RAG atual piora a classificação e aumenta o erro clinicamente perigoso | João, [B-01](../backlog.md#b-01) e rodada 4 |
| A ordenação não separa assunto; score alto não implica relevância | Handover de 30/08, João, [B-02](../backlog.md#b-02) e [B-11](../backlog.md#b-11) |
| Chunks grandes começam no meio de palavras e carregam cabeçalhos, rodapés e referências | `docs/anotacoes.md` e [B-02](../backlog.md#b-02) |
| Título, tema e espécie precisam participar do texto embedado | `docs/anotacoes.md`, [B-02](../backlog.md#b-02) e contrato A → B2 |
| A base contém sete protocolos sintéticos, não validados e apenas de emergência | João, [B-03](../backlog.md#b-03) |
| O limiar de 0,70 é inócuo e pode dar falsa segurança | João, [B-11](../backlog.md#b-11) |
| O re-ranking atual é apenas uma nova ordenação pelo mesmo score | Divisão de trabalho e [B-17](../backlog.md#b-17) |
| O banco não é versionado e precisa ser ingerido em cada máquina | João, [B-12](../backlog.md#b-12) |
| `RERANK_TOP_K` não é usado e pode conflitar com `CONTEXT_TOP_K` | João, [B-17](../backlog.md#b-17) |
| `CHROMA_PATH` e outras settings continuam sem uso | João, [B-18](../backlog.md#b-18) |
| Os relatos avaliados estão em inglês contra documentos em português | João, [B-15](../backlog.md#b-15) |
| O conjunto de avaliação é trivialmente separável e confunde rótulo com origem | João, [B-05](../backlog.md#b-05) |

Portanto, esses pontos **não são findings novos desta auditoria**. A inspeção
do código e do banco apenas os confirmou.

### Descobertas da equipe que a auditoria inicial não havia explicitado

A leitura integral das evidências acrescentou detalhes importantes à primeira
análise feita nesta máquina:

1. O mecanismo do dano do RAG foi identificado como **recalibração do limiar
   de gravidade**, não simplesmente citação ou alucinação de fonte errada. Nas
   linhas rebaixadas, o modelo geralmente não citou nenhum dos trechos.
2. No pipeline completo mais recente, o erro ficou sistematicamente no sentido
   inseguro: **40 falsos não urgentes e zero falsos urgentes**.
3. O HyDE já gerou uma doença inexistente — “Síndrome de Sífilo da Cadeia de
   Reações Imunes” — e esse texto inventado foi usado como consulta vetorial.
4. Depois da correção do Ryu, a variação residual cresce com a extensão da
   geração: 8% na reescrita, 17% nas multi-queries e 30% no HyDE.
5. A etapa de decisão foi determinística quando recebeu o mesmo contexto: zero
   casos com contexto idêntico e classificação diferente. Das 24 linhas cujo
   contexto mudou, 18 preservaram a decisão.
6. Reduzir o contexto de três para um trecho não resolveu o dano: os falsos não
   urgentes caíram de 30 para 19, ainda acima dos 8 do braço sem RAG.
7. A ausência da régua de recuperação do trilho A bloqueia formalmente a
   avaliação de Query Rewriting, Multi-Query e HyDE pelo trilho B1.

Esses achados pertencem às rodadas de João e Ryu; esta rodada apenas registra
que foram incorporados ao entendimento do trilho A.

### Findings novos desta auditoria

#### 1. O fingerprint da base não identifica seu conteúdo

O endpoint calcula o hash apenas da lista de IDs. Cada ID, por sua vez, é
derivado de `caminho:página:índice_do_chunk`. Se o texto ou os metadados de um
PDF mudarem sem alterar esse recorte, o fingerprint permanece igual embora os
embeddings e o conhecimento disponível ao RAG tenham mudado.

O fingerprint também não registra o nome com revisão/digest do modelo de
embedding, os parâmetros de chunking nem versões de `chromadb` e
`sentence-transformers`, que não estão fixadas. Duas bases materialmente
diferentes podem, portanto, parecer equivalentes no manifesto. Registrado como
[B-29](../backlog.md#b-29).

#### 2. A ingestão não é atômica nem sincroniza remoções

Para reingerir um documento, o ingestor apaga seus chunks antes do upsert. Se
a geração do embedding ou a escrita falhar depois da exclusão, a coleção ativa
pode ficar sem aquele documento ou com um lote parcial. Com `--reset`, uma
falha deixa toda a base incompleta.

No sentido oposto, executar sem `--reset` não remove da coleção documentos que
foram apagados da pasta: somente os arquivos ainda encontrados são
reprocessados. O resultado pode acumular registros órfãos. Registrado como
[B-30](../backlog.md#b-30).

#### 3. O núcleo real de recuperação não tem cobertura automatizada

Os testes do pipeline usam dublês para Chroma, recuperação e re-ranking. Não
há teste do `split_text`, extração de PDF/TXT, metadados, limpeza de registros
antigos, score cosseno ou busca sobre uma coleção real temporária. Uma
regressão nesses pontos pode passar pelos testes atuais e aparecer apenas numa
rodada cara do sistema. Registrado como [B-31](../backlog.md#b-31).

#### 4. O endpoint de voz aceita nome e tamanho controlados pelo cliente

O nome enviado no upload é concatenado diretamente a `uploads/`, sem gerar um
nome no servidor ou validar que o caminho final permanece nessa pasta. Também
não há limite de tamanho/tipo nem remoção após transcrever. Isso permite
sobrescrita fora da pasta e crescimento indefinido dos uploads. É fora do
trilho A e foi levado ao backlog como [B-32](../backlog.md#b-32), para o B1.

#### 5. O healthcheck pode declarar saudável um sistema sem RAG ou sem modelo

`GET /health/` sempre devolve `{"status":"ok"}`. É essa rota que o Compose
usa para liberar o frontend, mesmo quando Ollama está indisponível, o modelo
não foi baixado ou a coleção está vazia. Registrado como
[B-33](../backlog.md#b-33).

#### 6. A `main` não tem verificação automatizada

Não existe workflow de CI, lock completo de dependências, lint ou checagem de
tipos. A contagem documentada do backend também ficou em 49 enquanto hoje há
51 funções de teste. Registrado como [B-34](../backlog.md#b-34).

### Estado observado dos chunks

Dos 18 chunks atuais, 11 são continuações. Pelo menos 9 começam com fragmentos
ASCII em minúsculas, confirmando objetivamente o corte no meio de palavra já
descrito no handover. Além disso, vários primeiros chunks carregam o mesmo
cabeçalho sobre “conteúdo sintético não validado”, aproximando protocolos pelo
template em vez do assunto clínico.

## O que mudou no repositório

Nenhuma lógica de produto, documento clínico ou banco vetorial foi alterado.

| Arquivo | Mudança |
|---|---|
| `evidencias/vini/2026-09-07-01-auditoria-do-repositorio.md` | novo — esta rodada |
| `evidencias/vini/README.md` | novo — índice e estado do trilho A |
| `evidencias/vini/planejamento.md` | novo — roteiro, próxima entrega e bloqueios |
| `evidencias/backlog.md` | novos itens B-29 a B-34 para os findings ainda não registrados |

## Observações

1. A documentação anterior chama o ingestor de “maduro” e o reprocessamento
   de “seguro”. IDs estáveis e metadados são bons fundamentos, mas a ordem
   delete→upsert e a ausência de sincronização de arquivos removidos não
   sustentam segurança transacional.
2. O banco local possui o mesmo hash de IDs da última rodada, mas isso não
   prova igualdade de conteúdo justamente pela limitação do fingerprint
   registrada em B-29.
3. Adicionar mais PDFs é necessário, porém insuficiente. Sem conteúdo de não
   emergência, limpeza do texto e ranking por assunto, uma base maior pode
   aumentar a quantidade de contexto plausível e irrelevante — o mecanismo
   que já elevou scores enquanto piorava a classificação.
4. Para documentos reais, os metadados atuais são mínimos. Antes da curadoria
   deve-se combinar como registrar instituição/autoria, título, URL ou
   publicação, data de acesso, versão, licença, idioma e validação da
   especialista. Isso detalha o critério do B-03, não é registrado como item
   separado para evitar duplicidade.

## Deixado para depois

**Ingestão dos novos documentos.** Adiada até que os arquivos sejam
inventariados e exista ao menos a régua mínima de recuperação. Volta quando os
documentos forem disponibilizados com procedência e o conjunto de consultas
esperadas estiver pré-registrado.

**Alterações no chunking, embedding e re-ranking.** A auditoria identifica os
pontos, mas mudar os três juntos impediria atribuir o resultado. Cada um será
uma rodada própria, com antes/depois na mesma régua.

**Correções fora do trilho A.** Upload de voz, healthcheck e CI foram apenas
registrados no backlog com seus responsáveis; esta rodada não altera arquivos
dos outros trilhos.

## Próximo passo

Construir a régua de recuperação do trilho A antes da ampliação da base:
casos fixos, documento esperado e métricas Precision@1, MRR e Recall@5. Em
seguida, preparar e inserir os novos documentos em uma rodada separada,
registrando fingerprint de conteúdo e comparando o ranking antes/depois.
