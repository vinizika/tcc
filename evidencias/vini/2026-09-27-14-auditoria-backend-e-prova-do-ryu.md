# Auditoria do backend e da prova nova do Ryu

> **Nota de escopo (27/09):** esta auditoria descreve as rodadas do Ryu até
> `fceab20`. Ela foi produzida após eu interpretar incorretamente “Pet” como
> Ryu e **não responde** ao pedido sobre João Peterutto. A auditoria correta
> dos commits mais recentes do João está na
> [rodada seguinte](2026-09-27-15-auditoria-joao-peterutto.md).

**Data:** 27/09/2026  
**Escopo:** leitura integral das novas rodadas 11 a 16 do Ryu, inspeção dos
commits entre `4f45b99` e `fceab20`, conferência dos artefatos de avaliação e
comparação com a árvore local que contém a POC React.  
**Regra desta rodada:** somente análise. Nenhum merge, rebase ou ajuste
funcional foi feito.

## Resumo executivo

O trabalho novo não reconstrói todo o backend. A mudança funcional é
concentrada em duas frentes:

1. uma prova de texto livre com 150 casos, instrumentos contra vazamento e
   três baselines triviais;
2. um cliente híbrido para a etapa de **consulta** do RAG: Gemini primeiro,
   Ollama como fallback para reescrita e Multi-Query, e ausência de fallback
   para HyDE.

O classificador que produz a triagem final continua sendo o `LLMClient` com
`llama3.2:3b` no Ollama. Portanto, a integração do Gemini não elimina a
dependência do Ollama nem resolve, sozinha, falhas de geração/OOM na resposta
final.

Também há diferença entre código remoto e sistema executado nesta máquina:
`origin/main` contém o cliente híbrido, mas a imagem local em execução não o
contém. Além disso, o endpoint do workspace usado pelo frontend força
rewriting, Multi-Query e HyDE para `False`; mesmo depois de trazer os commits,
ele continuará sem usar a novidade enquanto essa decisão não for revisada.

## Recorte auditado

- Branch local: `codex/evaluate-rag-variants`, commit `4f45b99`.
- Último commit remoto auditado: `origin/main`, `fceab20`.
- Distância: a árvore local está 7 commits atrás de `origin/main` e não possui
  commits próprios à frente, embora tenha muitas alterações não commitadas.
- Delta remoto: 37 arquivos, com grande parte do volume formada pelo CSV de
  prova e por JSONs/evidências. No backend de execução, os pontos centrais são
  os clientes Gemini/híbrido, configuração e `ChatPipeline`.
- Commits funcionais: lote `dev`, lote `teste` e verificador de overlap,
  baselines/congelamento, comparador Gemini/Ollama e integração híbrida.

## O que mudou

### Prova oficial de texto livre

`data/prova/casos_oficiais.csv` agora possui:

- 150 casos: 50 em `dev` e 100 em `teste`;
- 77 `EMERGENCIA`, 70 `NAO_EMERGENCIA` e 3 `INCERTO`;
- cobertura dos 61 tópicos do mapa;
- 23 pares de confusão;
- nenhum ID ou texto duplicado.

O verificador `check_prova_overlap.py` compara n-gramas de seis palavras dos
casos contra os chunks do Chroma. A rodada registrada contra 3.481 chunks não
encontrou colisões. Isso reduz cópia literal, mas não prova ausência de
vazamento semântico ou de estilo.

O runner de triagem passou a aceitar arquivo, split e diretório de saída. Se
existir manifesto de congelamento, ele falha antes da avaliação quando o hash
do split mudou.

### Baselines e congelamento

Foram adicionados baselines de palavra de alarme, comprimento e Naive Bayes
com saco de palavras. Reexecutei o instrumento diretamente sobre o conteúdo de
`origin/main`:

| Baseline | Acurácia | n binário | Veredito B-05 |
|---|---:|---:|---|
| Palavra de alarme | 0,5714 | 147 | abaixo de 0,90 |
| Comprimento | 0,5918 | 147 | abaixo de 0,90 |
| Saco de palavras | **0,9116** | 147 | **reprovado** |

Logo, a prova melhorou muito em relação ao conjunto antigo, mas ainda é
separável acima do limite escolhido por um classificador lexical simples. A
causa mais plausível registrada é estilo de um único autor. O split `teste`
**não está congelado**: o comando de conferência recusou a execução porque não
existe `casos_oficiais.teste.freeze.json`.

### Gemini na preparação da consulta

O `GeminiQueryClient` reutiliza os mesmos prompts e a mesma interface do
cliente Ollama para:

- reescrever o relato;
- gerar até três variações Multi-Query;
- gerar o documento hipotético do HyDE.

O `HybridQueryClient` virou o padrão do `ChatPipeline` remoto:

1. tenta Gemini;
2. se houver `LLMException`, reescrita e Multi-Query caem para Ollama;
3. se o Gemini falhar no HyDE, devolve vazio, sem chamar Ollama;
4. Multi-Query e HyDE continuam paralelos;
5. `HYDE_ENABLED` voltou a `True` por padrão.

Nos 25 casos registrados, os números reproduzidos dos JSONs foram:

| Provedor | Precision@1 | MRR |
|---|---:|---:|
| Ollama | 0,280 | 0,365 |
| Gemini | 0,320 | 0,433 |

A diferença quantitativa é pequena e a amostra não sustenta superioridade
estatística. O achado mais forte é qualitativo: as revisões registram cinco
alucinações claras do Ollama e nenhuma do Gemini. Isso justifica testar o
Gemini como provedor de consulta, não declarar que o sistema clínico inteiro
ficou superior.

### Dependências e configuração

- entrada de `google-genai==2.24.0`;
- atualização de Pydantic de 2.11.7 para 2.13.5;
- `GEMINI_API_KEY` e `GEMINI_MODEL=gemini-3.5-flash-lite` nas configurações;
- chave real deve existir somente no `.env` local;
- nova pendência B-58: imagem Docker antiga pode sobreviver a mudanças de
  dependência; recriar contêiner não substitui `docker compose up --build`.

## Como o sistema remoto passa a funcionar

No endpoint legado `/chat/`, com as opções padrão, o fluxo pretendido é:

`relato original -> Gemini (reescrita + Multi-Query + HyDE) -> recuperação ->
reranking/corte -> Ollama llama3.2:3b (triagem final) -> resposta estruturada`.

Sem chave Gemini, reescrita e Multi-Query voltam ao Ollama e o HyDE é omitido.
O fallback só ocorre depois que o SDK devolve erro; não foi configurado timeout
explícito no cliente Gemini. Assim, a afirmação de que o tutor nunca aguardará
uma API externa lenta ainda não está garantida pelo código.

A coleção ativa registrada nos fingerprints da prova continua vazia. A
coleção candidata com 3.481 chunks não foi promovida pelo trabalho do Ryu.
Portanto, o novo cliente melhora a formulação da busca, mas não corrige a
ativação da base nem o gargalo conhecido de ordenação/reranking.

## O que está efetivamente rodando nesta máquina

Em 27/09, a inspeção somente leitura encontrou:

- `backend-api`, `frontend-app`, Mongo e Ollama ativos; backend saudável e
  frontend respondendo HTTP 200;
- imagem do backend sem `HybridQueryClient`, sem configurações Gemini e sem
  chave Gemini;
- defaults da imagem: rewriting `True`, Multi-Query `True`, HyDE `False`;
- coleção legada `veterinary_documents`: 0 chunks;
- workspace do frontend configurado para a candidata
  `veterinary_documents__20260920T160842289762Z__388f518d`: 3.481 chunks;
- suíte local combinada: 254 testes aprovados.

No fluxo React atual, `WorkspaceService.process()` força retrieval ligado e
as três técnicas de consulta desligadas. O fluxo real é, portanto:

`relato + contexto do animal -> busca pela consulta original nos 3.481 chunks
-> reranking/corte -> Ollama -> conversa persistida`.

Isso explica por que a mudança do Pet ainda não beneficia o frontend e por que
uma falha/OOM do Ollama na classificação continua aparecendo como “Não
conseguimos concluir a análise”.

## Melhorias reais

- instrumento de prova muito mais próximo de relatos reais e balanceado;
- cobertura explícita de todos os 61 tópicos e pares difíceis;
- prevenção automática de cópia literal entre base e prova;
- proteção por hash disponível para evitar deriva futura;
- baseline lexical expôs honestamente um viés residual do conjunto;
- Gemini isolado atrás de uma interface compatível e com fallback seletivo;
- redução registrada da etapa de consulta de dezenas de segundos no Ollama
  CPU para uma chamada ao vivo de 3,3 s com Gemini;
- testes unitários específicos para cliente Gemini, fallback e overlap.

## Limitações, inconsistências e riscos encontrados

1. **Não há melhora medida da triagem completa.** Os dois smokes oficiais têm
   apenas 5 e 3 casos, sem RAG. Não existe rodada completa dos 150 casos nem
   comparação da classificação final antes/depois do Gemini.
2. **B-05 continua reprovado.** O Naive Bayes chega a 0,9116 no conjunto
   combinado; a recomendação correta é diversificar autoria antes de congelar.
3. **Teste ainda não congelado.** A ferramenta existe, mas o manifesto não.
4. **Gemini atua somente na consulta.** A decisão final permanece no Ollama e
   mantém custo, latência e risco de OOM.
5. **Reranking continua sendo gargalo.** O ganho de MRR não resolve a baixa
   Precision@1 absoluta.
6. **Coleção principal vazia.** O endpoint legado ainda não usa a candidata
   de 3.481 chunks.
7. **Sem timeout Gemini explícito.** Fallback não protege contra espera
   indefinida antes de uma exceção do SDK.
8. **Dados do tutor saem da máquina.** Com Gemini ativo, o relato é enviado ao
   Google em até três transformações. Isso exige consentimento, política de
   privacidade e decisão LGPD antes de uso público.
9. **Documentação desatualizada.** O docstring do `GeminiQueryClient` e o
   comparador ainda dizem que nada de produção usa Gemini; o início do README
   da prova ainda diz que existe apenas `dev`, apesar dos 150 casos.
10. **Algumas descrições qualitativas divergem.** O docstring do cliente
    híbrido lista exemplos de erro diferentes dos consolidados nas evidências;
    os JSONs devem ser a fonte primária ao escrever os resultados.
11. **Latência de 3,3 s é observação única.** Não é distribuição, percentil ou
    SLA de produção.
12. **Credencial exposta no histórico.** A chave Google enviada anteriormente
    no chat deve ser revogada/rotacionada e substituída por chaves separadas e
    restritas. Ela não está no `.env` local auditado e não foi copiada para esta
    evidência.

## Impacto previsto na integração com o frontend

Há somente dois arquivos modificados dos dois lados com colisão direta de
Git: `.env.example` e `backend/app/core/config.py`. Não há colisão nominal
entre os novos arquivos remotos e os arquivos não rastreados da POC. Mesmo
assim, existem conflitos de comportamento que o merge textual não detecta:

- decidir se o workspace deve adotar Gemini/Hybrid ou preservar consulta
  original para comparabilidade científica;
- garantir timeout, privacidade e mensagens de falha da API externa;
- manter `POC_RAG_COLLECTION` sem alterar o ponteiro científico principal;
- reconstruir a imagem por causa da nova dependência;
- preservar o tratamento assíncrono e a persistência do frontend;
- tratar separadamente a dependência do Ollama na classificação final.

Antes de integrar, as alterações locais devem ser salvas em commit próprio (ou
outro mecanismo recuperável), pois hoje a árvore contém código importante não
rastreado. A integração não deve começar com merge sobre esse estado sem uma
âncora recuperável.

## Verificações desta auditoria

- leitura das evidências existentes e das seis novas rodadas do Ryu;
- inspeção do histórico e diff completo até `origin/main`;
- conferência programática das 150 linhas da prova;
- reprodução dos números P@1/MRR nos dois JSONs;
- reprodução dos três baselines e do veredito B-05;
- confirmação de que o split `teste` não está congelado;
- 10/10 testes puros de baseline/congelamento aprovados em cópia temporária de
  `origin/main`;
- testes backend remotos não executados no host por ausência de
  `pydantic-settings`; a evidência do Ryu registra 242 aprovados;
- 254 testes do backend local em execução aprovados;
- inspeção somente leitura dos contêineres, fingerprints e duas coleções.

## Conclusão

O Pet entregou uma evolução metodológica importante e uma integração útil do
Gemini na preparação das consultas. Ainda não há evidência de que a triagem
final melhorou, a prova oficial não está pronta para congelamento e a versão
que roda no frontend permanece anterior. A próxima etapa deve integrar os sete
commits com preservação da POC, decidir conscientemente a política de consulta
do workspace e validar o fluxo completo — inclusive falha do Gemini, OOM do
Ollama, privacidade e avaliação nos 150 casos — antes de chamar o resultado de
produção.
