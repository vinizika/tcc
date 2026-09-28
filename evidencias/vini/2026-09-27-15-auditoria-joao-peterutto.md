# Auditoria das mudanças de João Peterutto — arquitetura das fichas

**Data:** 27/09/2026  
**Escopo correto:** commits de João Peterutto entre `fceab20` e `e365f3e`,
rodadas 14 a 30 do trilho B2, código, coleções, provas e resultados.  
**Regra:** análise somente. Nenhum merge, rebase ou ajuste funcional.

## Correção do ponto de partida

A primeira auditoria desta data examinou o Ryu porque as referências locais
estavam paradas em `fceab20`, de 22/09, e “Pet” foi interpretado
incorretamente. Depois de `git fetch --all --prune`, `origin/main` avançou para
`e365f3e`, de 26/09. O intervalo novo contém 31 commits de `jpeterutto`, 711
arquivos alterados, 129.959 inserções e 428 remoções.

O volume é real, mas não equivale a 130 mil linhas de lógica: a maior parte é
formada por resultados de avaliação, fichas JSON, fontes capturadas, a nova
prova e um snapshot Chroma. Ainda assim, ao contrário do lote anterior do Ryu,
João efetivamente mudou a arquitetura principal do backend.

## Mudança arquitetural

### Antes, em 23/09

O sistema usava:

`relato -> tradução de consulta -> 3.481 trechos acadêmicos/MiniLM -> roteador
+ reranker + corte 0,72 -> llama3.2:3b`.

A autópsia encontrou:

- em 232 casos, ligar RAG consertava 2 e quebrava 8 (`p=0,11`);
- 116 de 122 relatos independentes chegavam ao classificador sem contexto;
- a coleção tinha 66 documentos, 3.481 trechos e 61 tópicos, mas 96% do texto
  estava em inglês e apenas 0,3% tinha orientação de urgência pela heurística
  estrita;
- o `llama3.2:3b` acertava somente 1 de 38 emergências contadas com calma;
- naqueles relatos, o sistema perdia 40 de 76 emergências e gerava 22 falsos
  alarmes em 46 casos leves;
- o roteador e o piso artificial de 0,721, não a similaridade vetorial,
  colocavam a maioria dos trechos acima da porta de 0,72;
- âncoras lexicais podiam vetar obstrução uretral mesmo quando o roteador
  identificava corretamente o tópico.

### Agora, no `origin/main`

O fluxo padrão passou a ser:

`relato cru -> BGE-M3 -> 61 fichas de busca -> top 3 sem corte -> fichas de
leitura correspondentes -> Gemini -> JSON estruturado + fontes + procedência`.

Mudanças concretas:

- a coleção ativa contém 61 fichas, uma por quadro do mapa;
- embedding `BAAI/bge-m3`, revisão fixa, 1.024 dimensões e limite de 512
  tokens;
- busca `vector` pura por padrão;
- três resultados sempre entram no contexto, com corte `0.0`;
- roteador lexical, reranker, âncoras e veto de espécie saíram do caminho
  padrão, mas permanecem como braço `routed_rerank` da ablação;
- reescrita, Multi-Query e HyDE ficam desligados por padrão;
- atendente padrão é `gemini-3.5-flash-lite`;
- `qwen3:8b` e `llama3.2:3b` permanecem opções locais;
- sem chave Gemini, o padrão é HTTP 503; não há troca silenciosa;
- fallback para Ollama só ocorre quando `ATTENDANT_FALLBACK=ollama` foi
  autorizado, e aparece na resposta;
- a API devolve provedor, modelo, versão, `thinking` e rastro da etapa de
  consulta;
- a resposta cita a ficha e as referências reais associadas, com título,
  periódico, ano e URL.

## Por que as fichas substituíram os artigos

João separou duas necessidades:

- **ficha de busca:** texto coloquial, desenhado para casar com o jeito do
  tutor relatar;
- **ficha de leitura:** conteúdo curto e controlado que o atendente usa para
  decidir urgência.

Com o assunto correto conhecido, os trechos acadêmicos não ajudaram de forma
consistente. Em prova + régua, o llama perdeu 14 emergências sem contexto e
16 com os trechos acadêmicos corretos. Com a ficha correta, perdeu zero. No
qwen, 7 perdas sem contexto viraram zero com a ficha correta.

Também foi demonstrado que não bastava escrever a decisão pronta. Retirando a
linha de conduta, o conteúdo da ficha ainda reduziu as perdas do qwen de 21
para 4 nos relatos independentes; a conduta fechou as perdas restantes e
reduziu falsos alarmes.

## Busca e ablação dos componentes

### BGE-M3

Nas fichas, BGE-M3 levou a ficha correta ao primeiro lugar em aproximadamente
80% da prova + régua, contra cerca de 20% do MiniLM. Na réplica final da busca:

- 296 de 296 trios reproduziram exatamente a autópsia;
- prova + régua: 107/129 no primeiro lugar e 123/129 no top 3;
- relatos independentes: 74/122 no primeiro lugar e 94/122 no top 3;
- piloto da prova 2: 16/40 no primeiro lugar e 32/40 no top 3.

A coleção ativa está versionada como
`veterinary_documents__20260925T061349534255Z__280baf13`. O ponteiro anterior
preserva a coleção acadêmica de 3.481 trechos para rollback e ablação. O
manifesto escolhe a receita de embedding correta para cada coleção.

### Sem porta de confiança

Com relatos independentes, a porta barrava também a ficha certa: 89 de 122
casos chegavam ao qwen sem ficha. Passar sempre as três mais próximas reduziu
as emergências perdidas de 21 para 7, com pareamento 15 × 1 (`p=0,0005`).

Esse desenho deliberadamente aceita fichas menos similares no contexto. É uma
troca entre cobertura e ruído, não uma prova de que todo top 3 seja relevante.

### Tradutor de consulta desligado

As três técnicas foram avaliadas com Ollama e Gemini:

- com llama, a reescrita inventava sinais em 54% das saídas;
- Multi-Query nomeava diagnóstico em 45% e falava de conduta em 81%;
- HyDE nomeava diagnóstico em 86% e falava de conduta em 100%;
- no Gemini, reescrita era mais fiel, mas Multi-Query e HyDE continuavam
  antecipando diagnóstico/conduta porque os prompts pediam isso;
- nas fichas, qualquer uma dessas técnicas reduziu o primeiro lugar da ficha
  correta; o relato cru foi superior.

Conclusão: o tradutor ajudava a aproximar linguagem de tutor de artigos
técnicos em inglês. Quando a base passou a usar português coloquial, virou
ruído. Ele foi preservado apenas para ablação.

## Escolha do atendente

Sem contexto, nos relatos independentes:

| Atendente | Emergências perdidas | Falsos alarmes |
|---|---:|---:|
| llama3.2:3b | 40/76 | 22/46 |
| qwen3:8b | 21/76 | 9/46 |
| Gemini | 5/76 | 10/46 |

Com as mesmas três fichas, qwen e Gemini ficaram estatisticamente empatados:

| Atendente | Prova + régua | Independentes | Tom calmo |
|---|---|---|---:|
| qwen3:8b | 2 perdas · 1 alarme | 5 · 7 | 4 perdas |
| Gemini | 2 · 1 | 6 · 3 | 3 perdas |

João escolheu Gemini como produto porque apresentou menos alarmes, mediana de
1,1 s, não exige GPU e se comportou melhor quando a busca falhou. O custo é
enviar o relato ao Google, depender de rede/cota e ter cauda de latência: 1%
das chamadas passaram de 20 s e o pior caso da autópsia levou 190 s.

O novo cliente agora possui timeout configurável, espaçamento, retries para
429/503, detecção de cota diária e erro explícito. Isso corrige a deficiência
do cliente de consulta anterior, que não tinha timeout explícito.

## Resultado do sistema proposto

Na réplica final pela API:

| Configuração | Prova + régua (74 E · 58 N) | Independentes (76 E · 46 N) |
|---|---|---|
| Gemini + fichas | **2 perdas · 1 alarme** | **6 · 3** |
| qwen + fichas | 2 · 1 | 5 · 7 |
| sistema anterior, llama/artigos | 15 · 4 | 40 · 22 |

Nos relatos independentes, o ganho contra o sistema anterior foi 35 × 1 em
emergências (`p < 0,0001`). No teste de tom, as perdas caíram de 46/74 para
3/74. Na prova 1, a comparação contra o sistema anterior com tradutor não foi
significativa (`8 × 2`, `p=0,11`), confirmando que essa prova é fácil e tem
pouco poder para diferenciar sistemas bons.

O runner reproduziu a autópsia caso a caso:

- Gemini: 134/134, 122/122, 40/40 e 74/74 nos quatro lotes;
- qwen: mesma resposta em todos os casos dos lotes correspondentes;
- busca: 296/296 trios na mesma ordem;
- repetição Gemini no `dev`: 50/50 classes e justificativas iguais.

## Nova prova 2

A prova 2 possui 330 relatos produzidos por nove agentes isolados:

- 194 emergências, 126 não emergências e 10 incertos;
- 61 tópicos do mapa e 25 casos especiais;
- nove autores, nenhum texto duplicado;
- tons e uso de “mas” balanceados por classe;
- 330 rótulos registrados como validados pela ASAVET, sem alteração.

A busca nela é mais difícil que na prova 1: nos 305 casos com tópico do mapa,
a ficha correta aparece em primeiro em 54% e no top 3 em 79%.

Ela **ainda não está pronta para produzir o número final**:

- falta a conferência completa de vazamento e separabilidade;
- existem nove pares do mesmo quadro com seis ou mais palavras consecutivas
  iguais;
- falta divisão por assunto em 66 calibração / 264 teste;
- falta congelamento por hash;
- a evidência de validação é um registro declarativo no repositório; não há
  artefato assinado independente para auditoria externa.

A prova 1, por outro lado, foi congelada em 25/09: 100 casos de teste, hash
`d370a0a51d59…8781`. Ela continua com rótulos provisórios do Ryu e com o
problema lexical B-05.

## Curadoria e validação das fichas

O gerador `sync_fichas.py` produz deterministicamente as 61 fichas consumidas
pelo backend. Os textos reproduzem byte a byte o que foi medido na autópsia.
A folha de certificação registra:

- 513 itens aceitos;
- 47 fontes aprovadas clinicamente;
- 36 das 53 frases antes sem fonte receberam trecho literal;
- os 330 rótulos da prova 2 confirmados.

Porém, “validado” não significa que tudo já está no texto de leitura usado
pelo sistema. A rodada 30 deliberadamente não mudou os 61 textos. Ainda falta
levar às fichas de leitura as 60 células certificadas da etapa 2 e limpar
notas internas. Essa mudança será uma nova rodada medida.

Riscos de conteúdo ainda abertos:

- seis documentos aprovados tratam de assunto diferente do tópico associado;
- cinco capturas da VCA possuem restrição explícita de redistribuição e uso
  por IA; outras fontes têm copyright sem autorização clara;
- direitos e validação clínica são processos diferentes;
- metadados de autoria ainda estão errados em alguns sidecars;
- uma frase ficou sem fonte e 16 possuem apoio parcial, embora tenham sido
  aceitas pelo registro de especialista.

## Qualidade do código e operação

Melhorias importantes:

- duas receitas de embedding coexistem por manifesto, evitando consultar uma
  coleção com o modelo errado;
- coleção e ponteiro ativos versionados; clone limpo abre a base correta;
- citações agora representam somente fichas que realmente couberam no prompt;
- procedência do atendente e das transformações de consulta;
- 503 estruturado para ausência de chave, indisponibilidade e cota;
- presets explícitos para produção, qwen, llama e braços históricos;
- runner aceita qualquer CSV de casos e registra procedência;
- documentação foi atualizada para refletir o código.

Limitações operacionais:

- BGE-M3 baixa aproximadamente 2,2 GB no primeiro uso;
- versionar o Chroma adiciona cerca de 73 MB por reindexação ao histórico;
- apenas abrir o Chroma altera arquivos binários versionados;
- qwen precisa de GPU para latência adequada: mediana 2,6 s na RTX 4060 e 34
  s somente em CPU;
- Gemini tem cota, latência de cauda, dependência externa e implicação LGPD;
- o modo vetorial padrão não veta espécie; uma ficha exclusiva de gato pode
  aparecer para cachorro entre as três;
- a arquitetura sempre fornece três fichas, mesmo com similaridade baixa;
- CoT piorou llama e qwen e permanece desligado; Self-Refine não existe.

## Estado da validação técnica desta auditoria

Executado numa cópia temporária de `origin/main`:

- `compileall` do backend e scripts: limpo;
- `sync_fichas.py --check`: limpo;
- `sync_retrieval_terms.py --check`: limpo;
- `prova2_montar.py --check`: limpo;
- congelamento da prova 1: hash confirmado;
- 185 testes de scripts fora da captura: aprovados;
- suíte completa no host: 191 aprovados e 26 falharam exclusivamente porque
  `trafilatura` não está instalado nesse Python; o total coletado é 217;
- as evidências do João registram 285 testes de backend, 217 de scripts e 10
  do mock aprovados no ambiente dele;
- a suíte do backend remoto não foi reproduzida localmente porque o ambiente
  desta máquina ainda executa a imagem anterior e não tem as novas
  dependências instaladas.

## Diferença para o frontend React local

O ambiente que roda nesta máquina ainda é a POC anterior:

- imagem sem as mudanças do João;
- coleção legada principal vazia;
- workspace React apontando explicitamente para a coleção acadêmica de 3.481
  chunks;
- classificação final pelo Ollama;
- rewriting, Multi-Query e HyDE já desligados no workspace.

Depois da integração textual, o workspace **não adotará automaticamente a
arquitetura completa**:

1. `POC_RAG_COLLECTION` continuará forçando a coleção acadêmica de 3.481
   chunks, em vez das 61 fichas;
2. o adaptador local do `RetrievalClient` precisa ser conciliado com a nova
   assinatura e a receita BGE-M3;
3. sem `GEMINI_API_KEY`, o atendente padrão produzirá 503;
4. `WorkspaceService` hoje captura qualquer exceção e converte o 503
   estruturado em uma mensagem genérica;
5. o workspace não persiste nem mostra `provenance`, portanto “Respondido por”
   ainda não aparece;
6. o React precisa explicar envio de dados ao Google e oferecer modo local;
7. o novo snapshot e o modelo BGE-M3 exigem rebuild e download inicial.

Há nove colisões diretas entre arquivos modificados localmente e pelo João:

- `.env.example`;
- `README.md`;
- `backend/app/clients/retrieval_client.py`;
- `backend/app/core/config.py`;
- `backend/app/services/chat_service.py`;
- `backend/chroma_db/chroma.sqlite3`;
- `backend/tests/conftest.py`;
- `docker-compose.yml`;
- `docs/CONTRATOS.md`.

Não há colisão nominal entre os arquivos não rastreados da POC e os arquivos
novos remotos, mas há forte conflito comportamental. A árvore local precisa
ser salva em um commit recuperável antes de qualquer integração.

## Conclusão

João transformou o sistema de um RAG sobre artigos acadêmicos para uma busca
semântica sobre fichas de triagem e também trocou o decisor padrão do llama
local para o Gemini. A melhoria experimental é grande e foi replicada pela
API, especialmente em emergências contadas com calma. É a versão correta a
ser levada ao frontend.

Ainda não é correto chamá-la de produção pública: faltam integrar o frontend,
resolver LGPD e direitos das fontes, transportar o conteúdo certificado às
fichas de leitura, concluir/congelar a prova 2 e validar o ambiente combinado.
Esses pontos precisam sobreviver à resolução de conflitos, não ser apagados
por um merge que apenas compile.
