Vini:
@GitHub https://github.com/vinizika/tcc analise o estado que está o repositório que o código agora, eu vi que o pet fez bastante coisa relacionada a base documental, acredito que até criou alguns agentes e um mapa de conhecinmento e o julian (ryu) fez avanço na parte de testes. tudo isso está documentado no repositorio nos docs e no evidencias. por favor faça um scan complelto do repositorio e de tudo o que foi feito. eu (vini) ficarei responsavel aparentemente pela ingestao de documentos na base de conhecimento e preciso que voce me confirme em que estado estamos, o que foi feito, analise tambem se o trabalho feito pelos os outros membros está com qualidade boa e tambem se é preciso arrumar alguma coisa ou seguir por talvez outro caminho. analise tambem a tecnica que estamos usando para inserir documentos novos no banco vetorial, a chunkinização, se isso esta sendo feito de bao forma ja e completamente pronto. assegure que todos os testes, metricas e numeros estao sendo documentados tambem. por agora, nao faca nenhuma modificacao no projeot, apenas escreva aqui para mim essa analise e faça um scan completo, traçando no final tambem uma lista completa de atividades e proximos passos meus (vini) com ordem de prioridade e impato
Chat:
## Conclusão direta

O projeto está em um bom estado de engenharia experimental, com testes e rastreabilidade muito acima do habitual para um TCC. Porém, o RAG ainda não está cientificamente validado e a ingestão documental ainda não está pronta para uso definitivo.

O gargalo agora não é “conseguir ler PDFs”. Essa parte está bem encaminhada. O caminho crítico é:

1. definir e validar clinicamente o corpus;
2. tornar a ingestão atômica e reproduzível;
3. medir a base nova contra a antiga;
4. corrigir ranking, limiar e embeddings com uma régua válida.

Auditei a `main` pública no commit [`c3f09ec`](https://github.com/vinizika/tcc/commit/c3f09ec5c6a5608e2039a0651a0dec437d19479b), todo o histórico Git, os 335 arquivos versionados, código, testes, `docs/`, `evidencias/`, dados, mapa, agentes e os dois anexos. Não alterei nada; o repositório permaneceu limpo.

## Estado real do projeto

| Área                     | Estado                                                                     | Parecer                               |
| ------------------------ | -------------------------------------------------------------------------- | ------------------------------------- |
| Pipeline principal       | Classifica de verdade, aceita texto/voz, retorna JSON estruturado e fontes | Bom                                   |
| Infraestrutura de testes | 181 testes do backend + 164 dos scripts                                    | Muito boa, mas sem integração real/CI |
| Ingestão e extração      | Layout, seções, tokens, metadados e inspeção implementados                 | Boa base técnica, ainda incompleta    |
| Base de conhecimento     | Sete protocolos sintéticos e um paper real não validado localmente         | Fraca para conclusão científica       |
| Recuperação              | Documento correto em primeiro em apenas 5/9 casos cobertos                 | Insuficiente                          |
| Avaliação antiga         | 98 relatos, mas separáveis por regras triviais                             | Não serve como prova final            |
| Prova nova               | Primeiro lote de 18 casos, ainda de calibração                             | Direção correta, muito preliminar     |
| Curadoria clínica        | Todo o mapa e todas as fontes continuam sem validação de especialista      | Bloqueador                            |
| Produção/segurança       | Protótipo local; persistência sem autenticação                             | Não pronto para exposição pública     |

A maior ambiguidade atual é que não existe uma única “base vetorial atual” definida pelo Git:

* A base histórica preservada tem **18 chunks de sete protocolos sintéticos**.
* A receita atual de ingestão produziria cerca de **259 chunks de oito documentos**.
* O Chroma gerado não é versionado.
* Portanto, duas máquinas podem estar executando bases diferentes mesmo usando a mesma `main`.

O próprio [README](https://github.com/vinizika/tcc/blob/main/README.md) reconhece essa transição, e o [retrato dos 18 chunks](https://github.com/vinizika/tcc/blob/main/data/evaluation/cited/base-2026-09-04-18-chunks/README.md) preserva corretamente a base anterior.

## O que João/Pet fez

O trabalho do João/Pet é, em geral, de qualidade muito boa.

Ele entregou:

* runner de avaliação versionado;
* manifestos com hash do dataset, modelo, prompts e base;
* métricas, previsões e relatórios derivados;
* comparação estatística entre rodadas;
* experimentos de Chain-of-Thought e corte de relevância;
* régua isolada de recuperação;
* comparação antes/depois da recuperação;
* mapa de assuntos;
* roteiros de cartógrafo e pesquisador;
* captura de fontes com hash e metadados;
* documentação explícita de resultados negativos.

A melhor qualidade desse trabalho é a honestidade experimental: o CoT piorou muito e isso foi registrado, em vez de ser escondido; o cutoff de 0,70 tornou o RAG silencioso e isso também foi corretamente explicado.

### Mapa de assuntos

O [mapa](https://github.com/vinizika/tcc/blob/main/data/curadoria/mapa-de-assuntos.csv) contém:

* 61 quadros únicos;
* 38 emergências e 23 casos que podem esperar;
* 31 quadros na etapa 1 e 30 na etapa 2;
* 27 prioridades A, 25 B e 9 C;
* 51 sem documento;
* 7 cobertos apenas por protocolo sintético;
* 2 com fonte encontrada;
* 1 marcado como indexado;
* **61 de 61 ainda em estado `rascunho`**.

É um mapa de cobertura/taxonomia, não um grafo de conhecimento. Ele é útil para coordenar corpus e prova, mas não deve ser tratado como verdade clínica antes da revisão dos especialistas. As referências estão bem rastreadas e diferenciam leitura direta, resumo e conteúdo bloqueado, o que é excelente.

### Agentes

Dos quatro agentes planejados, apenas dois existem:

* `cartografo.md`;
* `pesquisador.md`.

Ainda faltam:

* `redator-de-lacuna.md`;
* `ingestao.md`.

E eles são corretamente descritos como agentes de construção, não como parte da arquitetura executada pelo produto. Portanto, não se deve apresentar o projeto como “sistema multiagente”. Veja o [README dos agentes](https://github.com/vinizika/tcc/blob/main/agentes/README.md).

### Problema que encontrei no trabalho do João

O item B-55 afirma que o paper de heatstroke está indexado, mas nunca é recuperado. Essa conclusão ainda não está demonstrada.

O snapshot dos 18 chunks contém apenas sete tópicos sintéticos, e o manifesto da régua também aponta para essa mesma base. O paper de heatstroke não aparece no snapshot. O `compare` aparentemente inferiu “indexado” a partir do mapa/sidecar do disco, não do conteúdo efetivo do Chroma.

Assim, a conclusão correta neste momento é:

> O heatstroke está preparado no repositório, mas não há evidência de que estivesse na coleção usada pela régua.

Antes de usar B-55 no artigo, é necessário rodar a base nova e confirmar sua presença pelo fingerprint/manifesto.

## O que Ryu/Julian fez

O trabalho do Ryu também é tecnicamente bom e bem testado.

Entregas principais:

* temperatura e seed aplicadas à geração das consultas;
* redução da instabilidade de 33 para 6 linhas em 98;
* upload de voz protegido contra path traversal, tipo inválido, excesso de tamanho e arquivos temporários;
* consolidação do Whisper;
* benchmark de WER;
* primeiro lote da prova nova;
* cadastro de tutor/pet com Supabase;
* histórico de conversa com MongoDB;
* 47 testes novos na última rodada.

### Benchmark de voz

O resultado documentado foi:

* WER: **5,2%**;
* CER: **1,8%**;
* 18 áudios;
* 345 palavras;
* latência mediana de 4,5 segundos.

Está muito bem registrado no [relatório do Whisper](https://github.com/vinizika/tcc/blob/main/data/voice_benchmark/report.md), mas é fala sintética e limpa. É um limite otimista, não uma medida de uso real.

### Prova nova

O primeiro lote possui 18 casos PT-BR, sete pares de confusão e distribuição bem mais saudável. O LLM sem RAG acertou 15/18, mas as três falhas foram falsos não urgentes:

* medicamento humano em gato;
* torção gástrica descrita em tom calmo;
* obstrução uretral interpretada como comportamento.

Esse é um achado importante e clinicamente mais útil que a avaliação antiga. Porém, o próprio Ryu documentou corretamente que foi uma rodada manual, pequena e sem validação de especialista. Veja a [evidência da calibração](https://github.com/vinizika/tcc/blob/main/evidencias/ryu/2026-09-13-04-primeiro-lote-da-prova-nova.md).

### Persistência

A implementação está modular e degrada sem derrubar a triagem, mas não está pronta para dados reais:

* não há autenticação;
* as políticas RLS estão abertas;
* os testes usam dublês de Supabase/Mongo;
* Mongo está exposto localmente sem autenticação;
* um `conversation_id` inexistente pode ser retornado como se tivesse sido atualizado, mesmo com zero registros correspondentes;
* não há validação de que `tutor_id`, `pet_id` e conversa pertençam uns aos outros.

É uma entrega tecnicamente razoável, mas está fora do caminho científico mais urgente. Eu congelaria novas expansões de persistência até base, prova e recuperação estarem consolidadas.

## Ingestão e chunking do Vini

### O que está bem feito

A implementação é boa e mostra cuidado real:

* extração por blocos e coordenadas com PyMuPDF;
* fallback para `pypdf`;
* recomposição de páginas com uma ou duas colunas;
* remoção conservadora de cabeçalhos, rodapés, captions e blocos editoriais;
* detecção e filtragem de seções;
* sidecars com procedência, espécie, tópico e validação;
* chunking por frases e tokens;
* overlap lexical;
* limite contado com prefixo e tokens especiais;
* IDs determinísticos;
* modo `--inspect`/`--dry-run` sem abrir o Chroma;
* proteção contra leitura fora da pasta;
* fingerprint de conteúdo da base.

Os parâmetros atuais são:

* target: 96 tokens;
* overlap: 16;
* máximo: 128.

O limite de 128 está correto para o modelo usado: a [ficha oficial do `paraphrase-multilingual-MiniLM-L12-v2`](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) informa `max_seq_length=128`, vetores de 384 dimensões e suporte multilíngue. Portanto, o chunker respeita corretamente a fronteira técnica do embedder.

No paper de heatstroke, a extração passou de 200 para 186 chunks, com máximo de 119 tokens, removendo 15 headers, seis captions e quatro blocos editoriais. Isso é uma evolução concreta.

### O que impede considerar a ingestão pronta

1. **B-36: o prefixo chega ao prompt.**
   O texto armazenado começa com `Document title:` e `Section:`. Isso pode ajudar o embedding, mas o mesmo conteúdo é entregue ao LLM, duplicando título, introduzindo inglês e contaminando a comparação. É necessário separar `embedding_text` de `body/content`.

2. **B-30: não há atomicidade.**
   O ingestor apaga os chunks antigos e depois faz `upsert` em lotes. Se o embedding ou uma escrita falhar no meio, a coleção ativa fica parcial. Com `--reset`, o risco cobre toda a base. O [Chroma documenta `delete` e `upsert` como operações separadas](https://docs.trychroma.com/docs/collections/update-data); portanto, a falta de atomicidade é uma inferência direta do fluxo atual.

3. **Não há trava clínica.**
   Um arquivo sem sidecar recebe `not_informed` e ainda pode ser indexado. Também não há recusa para `not_validated`, `pending_specialist` ou fonte sem licença registrada.

4. **Falta integração real.**
   Os testes cobrem bem extração e orquestração, mas não fazem ingestão, reingestão, falha intermediária e busca em um Chroma temporário real.

5. **Reprodutibilidade incompleta.**
   `chromadb`, `sentence-transformers`, `transformers`, `pypdf` e várias dependências não estão fixadas. O modelo é identificado pelo nome, mas não por revisão/digest. `Ollama` usa `latest`.

6. **Configuração declarada não é a usada.**
   `CHROMA_PATH` existe nas settings, mas o cliente grava num caminho fixo dentro do backend. `VECTOR_DB` também não governa a implementação.

7. **O corpus novo ficaria desequilibrado.**
   Dos aproximadamente 259 chunks, 186 seriam do paper de heatstroke: **71,8% da base**. Além disso, é um paper de fisiopatologia em inglês, não orientação para tutor. Isso provavelmente introduziria ruído e concentração.

8. **O limiar de 0,70 não foi calibrado.**
   Nenhum dos 18 casos da régua passou desse valor. Hoje ele funciona como interruptor que desliga o RAG, não como detector validado de relevância.

9. **O re-ranking ainda não existe de verdade.**
   Ele apenas ordena novamente pelo mesmo score. `RERANK_TOP_K` não é efetivamente usado, não há diversidade por documento e a fusão multi-query fica com o maior score.

10. **Limitações documentais permanecem.**
    Não há OCR nem reconstrução robusta de tabelas. Isso é aceitável agora; eu não priorizaria essas funções sem uma fonte real que exija isso.

### Veredito sobre o chunking

A mecânica está bem projetada, mas os valores 96/16 são apenas um baseline plausível. Eles ainda não foram comparados empiricamente contra alternativas numa base validada.

Portanto:

> O chunking está tecnicamente bom, mas não está comprovadamente otimizado nem completamente pronto.

Eu manteria o RAG vetorial simples e mudaria ligeiramente a estratégia documental: preservar a fonte original e seu hash numa camada de procedência, mas indexar somente trechos/seções aprovados para pré-triagem. Não indexaria papers inteiros “como estão”. LightRAG/grafo deve continuar adiado até o baseline denso funcionar.

## Testes, métricas e documentação

Rodei as suítes no estado atual:

* backend: **181/181 passaram**;
* scripts: **164/164 passaram**;
* total: **345 testes passando**;
* apenas avisos de depreciação das dependências;
* Docker e serviços reais não estavam disponíveis no ambiente de auditoria.

A documentação experimental é forte:

* 14 rodadas de classificação citadas;
* cada uma com manifesto, métricas, previsões e relatório;
* snapshot restaurável da base antiga;
* régua de recuperação com resultados por caso;
* comparação antes/depois;
* benchmark de voz;
* calibração nova.

### Principais números

| Medição                                       |                                   Resultado | Interpretação correta                        |
| --------------------------------------------- | ------------------------------------------: | -------------------------------------------- |
| Regra trivial “só sinais leves”               |                                       98/98 | Prova antiga é inválida como avaliação final |
| Melhor resultado registrado sem contexto útil |                            0,893 balanceada | Não demonstra RAG                            |
| RAG sem corte                                 | 0,775 balanceada; 30/71 falsos não urgentes | Contexto ruim prejudica                      |
| RAG com corte 0,70                            |                     0,893; contexto em 0/98 | Igual ao LLM porque o RAG ficou desligado    |
| Recuperação Precision@1                       |                                 5/9 = 0,556 | Ordenação insuficiente                       |
| Recuperação MRR                               |                                       0,698 | Parcial                                      |
| Recall@5                                      |                                         1,0 | Pouco informativo com apenas sete documentos |
| Documento “trauma” em primeiro                |                                        9/18 | Protocolo-ímã                                |
| Calibração nova                               |                                       15/18 | Promissora, mas três falsos não urgentes     |
| Whisper sintético                             |                                    WER 5,2% | Otimista; falta áudio real                   |

A [régua de recuperação](https://github.com/vinizika/tcc/blob/main/data/retrieval/cited/20260911-202505_linha_de_base/report.md) documenta corretamente que Recall@5=1,0 é quase geométrico num acervo tão pequeno.

### O que ainda não está bem documentado ou sincronizado

* O README ainda anuncia 102 testes do backend e 57 dos scripts, não 181/164.
* O planejamento do Vini diz que a régua de recuperação não existe, embora João já a tenha entregue.
* `docs/CONTRATOS.md` ainda diz que CoT não foi implementado, mas o código e as evidências mostram o contrário.
* O README das fontes lista apenas torção gástrica, embora o piloto de vômito também exista.
* O status `indexada` do heatstroke conflita com o snapshot efetivo de 18 chunks.
* A primeira das duas execuções usadas para provar determinismo da régua não foi promovida integralmente para `cited/`; somente o comparativo preserva seus resultados.
* Cinco rodadas antigas citadas possuem `git.dirty=true`; as mais recentes estão limpas.
* Não existe CI em `.github/`.
* Não existe manifesto de cada ingestão com hashes das fontes, direitos/licenças, contagens, warnings e revisão exata do embedder.

## Risco de fontes e licença

O repositório continua público, sem arquivo `LICENSE`, e contém:

* o PDF completo do paper de heatstroke;
* capturas integrais de páginas de terceiros;
* PyMuPDF, que oficialmente é oferecido sob AGPL ou licença comercial ([documentação oficial](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)).

Tornar o repositório privado agora reduz a exposição futura, mas não desfaz o histórico que já foi público. Isso exige decisão do time/orientador sobre:

* permissão para redistribuir cada fonte;
* manter apenas URL, hash, metadados e trechos permitidos no Git;
* armazenar originais fora do repositório;
* adotar AGPL ou substituir/licenciar PyMuPDF.

Não é aconselhamento jurídico, mas é um risco real e prioritário.

## Divergências nos anexos

Os anexos não representam o mesmo projeto atual:

* A [Descrição do projeto](sandbox:/workspace/scratch/f3f90d2963cd/project_sources/01-Descri-o-do-projeto-de-TCC.txt) promete especialidade médica, roteamento hospitalar, Flutter, webhook e prontuário antecipado. Nada disso está implementado atualmente.
* O [Checklist](sandbox:/workspace/scratch/f3f90d2963cd/project_sources/02-Checklist.pdf) descreve outro TCC: previsão de abandono escolar com Databricks, outro tema e outro orientador.
* O repositório atual declara Rafael Gomes Alves como orientador; o checklist menciona Leonardo Anjoletto Ferreira.

Essa inconsistência administrativa precisa ser resolvida antes de qualquer entrega formal.

## Próximos passos do Vini, em ordem

|  # | Prioridade | Atividade do Vini                                                      | Impacto / critério de conclusão                                                               |
| -: | ---------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
|  1 | P0         | Fazer uma sync e definir o escopo canônico, orientador e divisão atual | Evita escrever/implementar dois TCCs diferentes; decisão registrada                           |
|  2 | P0         | Congelar novos commits de fontes e decidir privacidade/licenças        | Nenhuma fonte entra sem direito e status explícitos                                           |
|  3 | P0         | Corrigir conceitualmente o estado da base e o B-55                     | Confirmar, pelo conteúdo real do Chroma, o que está ou não indexado                           |
|  4 | P0         | Fechar B-36                                                            | `content` entregue ao LLM sem prefixos; embedding ainda pode considerar título/seção          |
|  5 | P0         | Fechar ou aceitar formalmente B-35                                     | Amostra dourada do PDF e limitações residuais registradas                                     |
|  6 | P0         | Fixar ambiente reprodutível                                            | Torch CPU, dependências travadas, revisão do embedder, imagem e Chroma identificados          |
|  7 | P0         | Resolver B-30 e B-31                                                   | Coleção temporária/staging, promoção atômica, rollback e teste com Chroma real                |
|  8 | P0         | Executar a virada controlada                                           | Rodar antiga e nova sob o mesmo código; hashes iguais nas máquinas; `compare.md` versionado   |
|  9 | P1         | Validar os instrumentos com especialistas                              | Mapa, casos da régua, 18 casos de calibração e fontes com nome/data/veredito                  |
| 10 | P1         | Montar primeiro lote pequeno e equilibrado                             | Fontes aprovadas, orientadas ao tutor, PT quando possível, cobrindo ambos os lados dos pares  |
| 11 | P1         | Reavaliar o paper de heatstroke                                        | Excluir da primeira base ou indexar apenas seções úteis; criar caso próprio antes de julgá-lo |
| 12 | P1         | Calibrar limiar, ranking e embeddings                                  | Comparação controlada, uma variável por rodada; medir P@1, MRR, ruído e falsos contextos      |
| 13 | P1         | Implementar o ciclo de ingestão num comando                            | Manifesto, inspeção, ingestão, fingerprint, régua, compare e evidência com fail-stop          |
| 14 | P2         | Sincronizar documentação e CI                                          | README com 181/164, estados corretos, workflow automático e números vinculados a artefatos    |

Até concluir os passos 1–8, eu não adicionaria mais documentos à coleção ativa, não iniciaria LightRAG e não trataria 0,70 como limiar validado. O trabalho mais valioso do Vini agora é transformar a boa engenharia de ingestão numa base controlada, clinicamente aprovada e experimentalmente comparável.
Vini:
@GitHub ok entao resolva os pontos de 1 até 8 pois eu quero adicionar mais documentos na base vetorial para melhorarmos nosso rag. voce consegue resolver por aqui ou preciso ir pro codex do vscode?
Pensamento do chat que interrompeu no meio:
Consigo resolver por aqui — você não precisa ir ao Codex do VS Code. Vou trabalhar diretamente no repositório, implementar os itens técnicos, rodar as suítes e preparar a entrega no GitHub. Só deixarei separados os pontos que dependem de decisão humana ou acesso externo: confirmar formalmente orientador/escopo, alterar a visibilidade do repositório, validar direitos autorais e conferir o mesmo hash nas três máquinas. Primeiro vou criar uma linha de trabalho segura e transformar os itens 3–7 em código testado; depois fechamos essas decisões e fazemos a virada controlada do item 8.

Consigo resolver por aqui; você não precisa migrar para o Codex do VS Code. Já deixei o trabalho isolado em uma branch local e agora vou fechar as mudanças técnicas, rodar toda a suíte e só então publicar no GitHub. Os únicos trechos que não podem ser “automatizados por decreto” são aprovações humanas (orientador/especialista/licenças) e a validação final nas três máquinas — nesses casos vou deixar bloqueios, evidências e comandos reproduzíveis, sem inventar aprovações.

Achei um defeito importante antes de mexer na base: o relatório de cobertura tratava todos os JSONs presentes no disco como se já estivessem no Chroma. Foi isso que criou o falso “8 documentos indexados / heatstroke nunca recuperado”; a base preservada tinha apenas 7 assuntos e 18 chunks. Vou corrigir o instrumento para usar o conteúdo real do banco e manter o relatório histórico como evidência, com uma errata explícita.

Revisão automática interrompida
Verificou espaço disponível e versões de pacotes
Revisão automática interrompida
Inspecionou a implementação da função de embeddings
Revisão automática interrompida

A correção do B‑36 já está aplicada no código: o embedding continua recebendo título e seção, mas o prompt/API passa a receber somente o texto original do trecho. Também acrescentei ao fingerprint a composição real da coleção (assuntos, arquivos, estados de validação e revisão exata do modelo), que é a base para métricas confiáveis e comparação entre máquinas. Agora estou trocando a reindexação destrutiva por “staging + promoção atômica”.

A camada de segurança já está pronta: a ingestão curada agora recusa automaticamente fonte sem hash, aprovação identificada do especialista, declaração de direitos e revisão de extração de PDF. A ingestão experimental continua possível, mas exige --profile experimental e registra cada ressalva no manifesto. Também pinnei o Torch CPU e as versões do núcleo vetorial; a instalação limpa acabou de resolver sem conflito. Vou validar agora com ChromaDB real, além dos testes unitários.

A parte estrutural já está encaminhada: ingestão em staging, promoção atômica, rollback, perfis curated/experimental, metadados limpos para busca e correção da métrica que confundia “arquivo presente” com “documento indexado”. Agora estou fechando a documentação/evidências e rodando a validação reproduzível em ambiente novo, inclusive com Chroma real e o modelo de embedding fixado.

O ambiente limpo revelou uma diferença útil: o backend passou integralmente (189 testes), mas a suíte dos scripts falhou porque esse ambiente havia sido criado antes de instalar a dependência já declarada trafilatura. Vou reinstalar exatamente os arquivos de requisitos atuais e repetir; isso distingue falha de código de falha de preparação do ambiente e ficará registrado nas evidências.

O modelo fixado também foi validado de verdade, não só por dublê: o tokenizer abriu na revisão congelada e o embedding gerou vetor de 384 dimensões. Agora vou fazer uma ingestão completa em uma base temporária, fora do banco do projeto, para provar extração → chunks → upsert → manifesto sem alterar a coleção ativa de ninguém.

A parte mais delicada já está encaminhada: a ingestão curada agora é separada do corpus sintético/legado e falha de forma segura enquanto não houver uma fonte aprovada. Estou fechando a auditoria das métricas históricas — encontrei um relatório antigo que inferia “indexado” a partir dos arquivos atuais, e vou marcá-lo explicitamente como histórico parcialmente inválido, sem reescrever números que não podem ser reproduzidos. Depois disso rodo a bateria completa e publico tudo em uma branch/PR para você usar sem depender do VS Code.

O diagnóstico da régua ficou preciso: os resultados de ordenação e o “protocolo-ímã” continuam válidos, mas a afirmação de que heatstroke estava naquele índice não é recuperável nem suportada pelo manifesto. Vou preservar o artefato como registro histórico, acrescentando uma errata legível tanto no Markdown quanto no JSON; assim ninguém usa silenciosamente um número corrigido sem saber de onde veio.

As validações estáticas já passaram: não há erro de whitespace no diff, os 48 JSONs e os dois YAMLs carregam corretamente, e todo o Python compila. Agora vou executar em paralelo os testes completos do backend e dos scripts; estes são os números que entrarão na evidência final, em vez de manter contagens antigas escritas à mão.

O ensaio real, em uma base temporária, concluiu a promoção atômica: 8 documentos, 259 chunks, mínimo 48, média 86,768, mediana 92 e máximo 128 tokens. Ele também revelou uma lacuna útil antes da entrega: o manifesto da ingestão ainda não carregava todos os campos que o verificador das três máquinas dizia comparar. Vou fechar isso agora e fazer o verificador reprovar quando um campo obrigatório estiver ausente — dois arquivos incompletos não poderão mais parecer “equivalentes”.

Também vou confrontar as mudanças com os dois arquivos de referência anexados (descrição do TCC e checklist), para que “pronto” não signifique apenas testes verdes. Como um deles é PDF, vou seguir o fluxo de leitura/inspeção de PDF para preservar tabelas e marcações que uma extração simples poderia perder.

Há um bloqueio externo que o código não consegue resolver: o Checklist.pdf anexado é de outro TCC — previsão de rendimento/abandono escolar com Databricks — enquanto o repositório e o arquivo de descrição são de pré-triagem veterinária. Confirmei isso também visualmente nas duas páginas. Vou manter o código coerente com o repositório veterinário, mas a troca/correção desse documento institucional precisa entrar como prioridade máxima antes de qualquer submissão acadêmica.

A revisão das instruções encontrou mais duas brechas antes de chamar o fluxo de “pronto”: o contrato dizia que o tópico precisava existir no mapa e que a fonte precisava sair de curated_candidate para curated, mas o código ainda aceitava qualquer tópico não vazio e tratava o estado candidato como elegível. Vou alinhar a porta ao próprio contrato; assim, copiar uma captura pendente para a pasta da base não basta para indexá-la por acidente.

A auditoria da régua encontrou uma terceira inconsistência conceitual importante: a documentação dizia que cobertura era conferida por tópico e espécie, mas o cálculo só verificava tópico e apenas mostrava a espécie como aviso. Vou corrigir a métrica para que uma fonte apenas de gato não “cubra” uma linha que exige cão e gato; dog_and_cat ou a combinação de documentos de ambas as espécies será necessária para uma linha ambos.

A porta e a régua agora refletem o contrato real: tópico obrigatório no mapa, estado curated, somente fonte original, datas/vereditos coerentes, seções declaradas realmente detectadas e cobertura completa por espécie. Vou consultar agora o estado remoto pelo conector do GitHub antes de preparar a branch; ainda não vou publicar enquanto a evidência e a última bateria completa não estiverem fechadas.

Ao seguir o número até a definição, encontrei mais uma fonte de inflação: “encontrável” estava contando um tópico que aparecesse em qualquer caso, inclusive como resultado errado de outra queixa. A porta escrita pelo time exige o tópico no top‑5 do seu próprio caso. Vou separar “observado no índice” de “recuperado no caso esperado”; isso mantém o inventário histórico conservador sem transformar ruído em cobertura.

A promoção já era atômica, mas o comando administrativo de rollback ainda confiava apenas em “coleção não vazia”. Vou apertar esse último elo: coleções versionadas só poderão ser ativadas se o manifesto existir e os hashes/contagem baterem com o conteúdo real. A única exceção será a coleção-base legada, necessária para o primeiro rollback de quem ainda tem o snapshot antigo sem manifesto.

O plano antigo da “virada 18 → 259” mistura duas variáveis: troca o chunking e adiciona o paper de heatstroke. Isso não permite atribuir eventual ganho à chunkinização. Vou acrescentar um perfil explícito de ensaio legacy_rechunk, com os mesmos sete protocolos do índice histórico (estimativa já observada: 73 chunks), deixando experimental para os oito arquivos e curated para a base clínica real. Assim o experimento metodológico e a futura ingestão do Vini deixam de disputar a mesma coleção lógica.

Estou concluindo a validação final agora: vou conferir as duas ingestões reais em diretórios temporários, rodar as suítes completas e então publicar tudo em uma branch/PR. O ponto central já está claro: o pipeline técnico pode ficar pronto por aqui, mas a ingestão “curada” continuará bloqueada de propósito até existirem fontes aprovadas, direitos de uso e pareceres humanos.

Verificados manifestos de ingestão documental

As duas execuções reais terminaram corretamente: o perfil comparável aos sete documentos antigos gerou 73 chunks; o perfil experimental com os oito documentos gerou 259. Nenhuma delas tocou a base do projeto — usei apenas diretórios temporários. Agora estou rodando as suítes completas e fechando os números que entrarão na evidência.

Validação de testes fechada: 196 testes do backend e 176 dos scripts passaram; há apenas dois avisos de depreciação vindos de dependências externas, sem falhas. Estou usando esses totais exatos para corrigir os READMEs e preparar a evidência auditável da mudança.

A revisão final encontrou uma proteção adicional que vale fechar antes do PR: se o ponteiro ativo apontasse para uma coleção inexistente, o cliente poderia recriá-la vazia silenciosamente. Vou transformar isso em falha explícita e cobrir com ChromaDB real; assim um ponteiro quebrado não se disfarça de “base válida, porém vazia”.

A última proteção passou no Chroma real. O total definitivo é 197 testes do backend + 176 dos scripts = 373. Também confirmei que o perfil curado falha antes de criar qualquer banco quando não há fonte aprovada, exatamente o comportamento seguro esperado.
Você atingiu seu limite de uso. Faça upgrade do plano ou adicione créditos para continuar, ou tente novamente em 19 de set. de 2026, 13:50.
Vini:
voce parou pelo limite de tokens, eu vejo nas etapas que faltava consolidar evidencias, revisar diff e publicar branch, e vc tava executando executar testes completos e ingestoes reais temporarias. veja o que faltava e me diga para tentarmos terminar o mais critico que faltava
Chat:
Você está certo: a parte mais importante já foi executada. O que faltou foi o fechamento operacional.

Concluído:

* 197 testes do backend passaram.
* 176 testes dos scripts passaram.
* 373 testes no total.
* 4 testes usam ChromaDB real temporário.
* Ingestão temporária `legacy_rechunk`: 7 documentos, 73 chunks.
* Ingestão temporária `experimental`: 8 documentos, 259 chunks.
* Perfil `curated` recusou corretamente a execução, pois ainda existem 0 fontes aprovadas.
* Staging, manifesto, hashes, promoção atômica, rollback e proteção contra ponteiro quebrado foram implementados.
* Evidências e estado canônico foram consolidados:

  * [Evidência principal](sandbox:/workspace/scratch/f3f90d2963cd/repo_audit/evidencias/vini/2026-09-13-04-endurecimento-da-ingestao-vetorial.md)
  * [Dados estruturados da evidência](sandbox:/workspace/scratch/f3f90d2963cd/repo_audit/evidencias/vini/2026-09-13-04-endurecimento-da-ingestao-vetorial.json)

O que ainda falta:

1. Rodar a verificação final do diff e validar os arquivos de evidência.
2. Criar o commit local.
3. Publicar a branch `codex/harden-vector-ingestion`.
4. Abrir o Pull Request contra `main`.
5. Aguardar o GitHub Actions ficar verde.

Confirmei pelo GitHub que a branch e o PR ainda não existem. A `main` continua no commit `c3f09ec`.

O ambiente de execução caiu com erro de conexão do `exec-server`, então não consegui executar essa última sequência nem publicar a branch. Esse é o ponto técnico mais crítico agora. Você não precisa ir para o VS Code; podemos terminar aqui assim que o ambiente de execução for restabelecido.

Depois da publicação, ainda existirão bloqueios humanos para a ingestão real:

* confirmar o escopo correto do TCC;
* substituir o `Checklist.pdf`, que pertence a outro projeto;
* resolver direitos do paper e a visibilidade pública do repositório;
* obter aprovação dos especialistas;
* validar o primeiro lote curado;
* repetir o fingerprint nas três máquinas.

Portanto, o próximo passo imediato é: restabelecer a sessão, revisar o diff, commitar e publicar o PR. Não devemos adicionar novos documentos à base curada antes dessas aprovações.
Vini:
Você passou mais de 100 minutos pensando e editando arquivos localmente em um ambiente isolado (sandbox) para criar e publicar uma branch com as modificações que havíamos planejado. No entanto, o limite de créditos/tokens esgotou e o processo foi interrompido antes que a branch fosse enviada para o meu repositório remoto.

Como o ambiente local onde você estava trabalhando pode ter sido descartado, preciso recuperar o progresso. Por favor, me responda detalhadamente:

1. PLANO DE AÇÃO EXECUTADO: Qual foi a lógica exata que você implementou e quais problemas você conseguiu resolver enquanto pensava?
2. ARQUIVOS MODIFICADOS: Quais arquivos do projeto você chegou a alterar ou criar? (Liste os caminhos/nomes dos arquivos).
3. CÓDIGO PRODUZIDO: Você consegue reconstruir ou me fornecer os trechos de código mais importantes que você havia escrito para essas alterações?
4. PRÓXIMOS PASSOS: Como posso aplicar essas alterações manualmente ou qual é o caminho mais rápido para continuarmos de onde você parou, agora que o ambiente local anterior sumiu?

Traga as respostas em formato de texto estruturado para que eu possa reconstruir o trabalho. Um arquico md seria o ideal
Chat:
# Relatório de recuperação — endurecimento da ingestão vetorial

**Repositório:** `vinizika/tcc`
**Branch planejada:** `codex/harden-vector-ingestion`
**Commit-base:** `c3f09ec5c6a5608e2039a0651a0dec437d19479b`
**Estado remoto confirmado:** branch e Pull Request não existem; `main` não foi alterada.

> Este relatório reconstrói o trabalho realizado a partir do histórico da sessão. Ele contém a lógica, os arquivos e os trechos principais, mas não substitui o diff completo perdido do workspace.

---

## 1. Plano de ação executado

A lógica implementada foi organizada em oito frentes.

### 1.1 Separação entre estado técnico e decisões humanas

Foi criado um estado canônico do projeto em:

```text
docs/estado-atual.md
```

O documento passou a separar:

* o que existe no código;
* o que foi medido;
* o que está tecnicamente pronto;
* o que depende de especialista, orientador ou decisão do time;
* o que ainda não pode ser chamado de validação clínica.

Também foi registrada uma inconsistência importante:

* `Checklist.pdf` pertence a outro projeto, relacionado a previsão de rendimento escolar com Databricks;
* a descrição textual do projeto fala em especialidade veterinária, roteamento hospitalar, Flutter, webhook, SaaS e “pré-diagnóstico”, enquanto o repositório atual implementa pré-triagem veterinária em três classes.

A conclusão foi que a descrição institucional correta precisa ser confirmada antes da entrega final.

---

### 1.2 Separação entre corpus experimental e corpus curado

O problema original era que os documentos sintéticos e o paper de heatstroke podiam ser indexados como se fossem uma base clínica validada.

Foi criado o campo:

```json
"ingestion_scope": "experimental_only"
```

E foram definidos três perfis:

```text
curated
experimental
legacy_rechunk
```

#### `curated`

Aceita somente fontes aprovadas, com:

* sidecar JSON;
* hash do arquivo;
* tópico existente no mapa;
* espécie canônica;
* aprovação de especialista;
* direitos de uso;
* revisão de extração;
* seleção explícita de seções para PDF.

#### `experimental`

Serve somente para ensaios técnicos. Aceita documentos pendentes, mas registra advertências.

#### `legacy_rechunk`

Seleciona exclusivamente os sete protocolos sintéticos históricos para comparar:

```text
18 chunks antigos × 73 chunks com a nova técnica
```

Esse perfil evita misturar o efeito do novo chunking com o efeito da entrada do paper de heatstroke.

---

### 1.3 Correção do problema B-36

O chunk original era armazenado assim:

```text
Document title: ...
Section: ...

corpo do documento
```

Esse texto era usado tanto para gerar o embedding quanto para chegar ao prompt do modelo.

A implementação foi alterada para manter duas representações:

```python
@dataclass(frozen=True)
class DocumentChunk:
    text: str
    section: str
    page_start: int
    page_end: int
    token_count: int
    body: str = ""
```

O vetor continua usando o texto contextualizado:

```text
título + seção + corpo
```

Mas o prompt recebe somente:

```python
metadata["body"]
```

No cliente de recuperação:

```python
content=metadata.get("body", content)
```

O fallback para `content` preserva compatibilidade com snapshots antigos que ainda não possuem o campo `body`.

---

### 1.4 Chunking por tokens, frases e seções

A técnica passou a:

* detectar seções;
* normalizar acentos e Unicode;
* dividir preferencialmente em frases;
* dividir frases longas por palavras inteiras;
* respeitar o limite real do tokenizer;
* usar alvo de 96 tokens;
* usar overlap de 16 tokens;
* respeitar teto de 128 tokens;
* registrar página inicial e final;
* registrar seção;
* registrar contagem de tokens;
* registrar fallback de divisão;
* registrar fragmentos corrompidos removidos.

A configuração consolidada ficou:

```python
CHUNK_TARGET_TOKENS = 96
CHUNK_OVERLAP_TOKENS = 16
EMBEDDING_MAX_TOKENS = 128
```

A revisão do modelo também foi congelada:

```python
EMBEDDING_MODEL_NAME = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

EMBEDDING_MODEL_REVISION = (
    "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
)
```

---

### 1.5 Staging, manifesto, promoção atômica e rollback

O fluxo anterior podia alterar diretamente a coleção ativa.

Foi substituído por:

```text
1. selecionar as fontes;
2. validar todos os sidecars;
3. extrair e dividir todos os documentos;
4. criar coleção versionada de staging;
5. inserir todos os chunks;
6. conferir IDs e contagem;
7. calcular hashes;
8. gravar manifesto;
9. validar o manifesto contra o conteúdo real;
10. trocar o ponteiro ativo atomicamente.
```

A coleção anterior não é removida.

O ponteiro ativo passou a ser:

```text
backend/data/chroma/active_collection.json
```

A substituição ocorre com:

```python
os.replace(temporary_path, path)
```

Também foi adicionada a proteção para ponteiros quebrados. Se o ponteiro apontar para uma coleção inexistente, o cliente falha explicitamente em vez de criar uma coleção vazia silenciosamente.

---

### 1.6 Fingerprint completo da base

O fingerprint passou a registrar:

```json
{
  "collection": "...",
  "chunk_count": 259,
  "chunk_ids_sha256": "...",
  "content_sha256": "...",
  "embedding_model": "...",
  "embedding_revision": "...",
  "chunking": {
    "target_tokens": 96,
    "overlap_tokens": 16,
    "max_tokens": 128
  },
  "topic_counts": {},
  "species_counts_by_topic": {},
  "source_file_counts": {},
  "validation_status_counts": {}
}
```

Isso permite descobrir se duas máquinas realmente materializaram a mesma base.

---

### 1.7 Correção do compare histórico

O compare antigo usava sidecars atuais do disco para inferir o que existia em coleções antigas.

Isso gerou uma conclusão inválida sobre o paper de heatstroke.

A correção fez o compare usar:

```text
topic_counts
species_counts_by_topic
```

registrados no fingerprint de cada rodada.

Também foi corrigida a definição de “encontrável”:

* o tópico precisa aparecer no top-5;
* o caso precisa esperar aquele tópico;
* a espécie da fonte precisa cobrir a espécie exigida pelo mapa.

A errata concluiu:

```text
A coleção histórica tinha 18 chunks.
Os resultados observavam 7 tópicos.
Somente 6 linhas eram plenamente cobertas por espécie.
O paper de heatstroke não estava naquela coleção.
```

O item B-55 foi descartado porque sua premissa histórica era inválida.

---

### 1.8 Reprodutibilidade e CI

Foram fixadas versões diretas de:

* ChromaDB;
* Sentence Transformers;
* Transformers;
* PyMuPDF;
* pypdf;
* fonttools;
* FastAPI;
* pytest;
* Ollama;
* MongoDB.

Foi criado um arquivo separado para Torch CPU:

```text
backend/requirements-torch-cpu.txt
```

A imagem Docker passou a instalar Torch pelo índice CPU, evitando download de pacotes CUDA.

Também foi criado:

```text
.github/workflows/tests.yml
```

O workflow executa:

```text
backend/tests
scripts/tests
```

O CI ainda não foi confirmado porque o Pull Request nunca chegou a ser criado.

---

## 2. Resultados medidos

### Testes

Resultados finais obtidos antes da interrupção:

| Suíte                               |     Resultado |
| ----------------------------------- | ------------: |
| Backend                             | 197 aprovados |
| Scripts                             | 176 aprovados |
| Total                               | 373 aprovados |
| Testes com ChromaDB real temporário |             4 |
| `pip check`                         |      aprovado |

Foram observados somente avisos de depreciação em dependências externas.

---

### Perfil `legacy_rechunk`

Execução real em ChromaDB temporário:

```text
Documentos: 7
Chunks: 73
Mínimo: 55 tokens
Média: 82,658 tokens
Mediana: 82 tokens
Máximo: 128 tokens
Fallbacks: 0
Fragmentos corrompidos removidos: 0
```

---

### Perfil `experimental`

Execução real em ChromaDB temporário:

```text
Documentos: 8
Chunks: 259
Mínimo: 48 tokens
Média: 86,768 tokens
Mediana: 92 tokens
Máximo: 128 tokens
Fallbacks: 31
Fragmentos corrompidos removidos: 1
```

O paper de heatstroke gerou:

```text
186 de 259 chunks
71,8% do corpus experimental
```

Isso demonstra que o chunking funciona tecnicamente, mas a base ainda está desbalanceada.

---

### Perfil curado

O comando curado foi executado e recusou a ingestão:

```text
exit code: 2
```

Motivo:

```text
Nenhuma fonte elegível foi selecionada.
```

Também foi confirmado que a pasta do Chroma não foi criada durante essa recusa.

---

### Smoke test de recuperação

Consulta:

```text
cachorro muito quente, ofegante e desmaiando depois de ficar no sol
```

Resultados:

| Posição | Tópico            |  Score |
| ------: | ----------------- | -----: |
|       1 | canine_heatstroke | 0,6986 |
|       2 | canine_heatstroke | 0,6905 |
|       3 | canine_heatstroke | 0,6645 |
|       4 | canine_heatstroke | 0,6500 |
|       5 | canine_heatstroke | 0,6499 |

Todos os corpos retornados estavam limpos, sem:

```text
Document title:
Section:
```

O score máximo ficou abaixo do corte de 0,70. Portanto, isso confirma a integração, mas não comprova qualidade clínica nem melhoria do RAG.

---

## 3. Arquivos modificados

### Arquivos de configuração e infraestrutura

```text
.env.example
README.md
backend/Dockerfile
backend/requirements.txt
backend/requirements-dev.txt
backend/requirements-torch-cpu.txt
docker-compose.yml
frontend/requirements.txt
scripts/requirements.txt
.github/workflows/tests.yml
```

### Backend principal

```text
backend/app/clients/retrieval_client.py
backend/app/core/config.py
backend/app/database/chroma_client.py
backend/app/database/document_processing.py
backend/app/database/embedding_config.py
backend/app/database/ingest_documents.py
backend/app/services/fingerprint_service.py
```

### Documentos e metadados

```text
backend/data/documents/README.md
backend/data/documents/convulsoes.json
backend/data/documents/dificuldade_respiratoria.json
backend/data/documents/intoxicacao_cebola_alho.json
backend/data/documents/intoxicacao_chocolate.json
backend/data/documents/obstrucao_urinaria_gatos.json
backend/data/documents/pathophysiology_heatstroke_dogs_2017.json
backend/data/documents/trauma_hemorragia.json
backend/data/documents/vomito_diarreia.json
```

Os oito documentos legados foram marcados como:

```json
"ingestion_scope": "experimental_only"
```

### Testes do backend

```text
backend/tests/test_api_health.py
backend/tests/test_api_search.py
backend/tests/test_document_processing.py
backend/tests/test_pdf_layout_extraction.py
backend/tests/test_chroma_ingestion_integration.py
backend/tests/test_ingestion_safety.py
```

### Curadoria

```text
data/curadoria/README.md
data/curadoria/mapa-de-assuntos.csv
data/curadoria/fontes/README.md
data/curadoria/fontes/capturas/gastric_dilatation_volvulus__pdsa.json
data/curadoria/fontes/capturas/gastric_dilatation_volvulus__scielo_2012.json
data/curadoria/fontes/capturas/single_vomiting_or_mild_diarrhea__cornell_bola_pelo.json
data/curadoria/fontes/capturas/single_vomiting_or_mild_diarrhea__crmvsp.json
data/curadoria/fontes/capturas/single_vomiting_or_mild_diarrhea__pdsa_vomito.json
```

### Scripts

```text
scripts/capturar_fonte.py
scripts/retrieval_compare.py
scripts/retrieval_compare_report.py
scripts/run_ingestion_cycle.py
scripts/verify_vector_consensus.py
```

### Testes dos scripts

```text
scripts/tests/test_capturar_fonte.py
scripts/tests/test_retrieval_compare.py
scripts/tests/test_vector_consensus.py
```

### Documentação e evidências

```text
docs/CONTRATOS.md
docs/README.md
docs/ingestao-documental.md
docs/plano-base-e-prova.md
docs/estado-atual.md
evidencias/backlog.md
evidencias/joao/2026-09-12-14-compare-da-regua.md
evidencias/vini/README.md
evidencias/vini/planejamento.md
evidencias/vini/2026-09-13-04-endurecimento-da-ingestao-vetorial.md
evidencias/vini/2026-09-13-04-endurecimento-da-ingestao-vetorial.json
agentes/README.md
agentes/ingestao.md
.claude/agents/ingestao.md
```

### Artefatos históricos corrigidos

```text
data/retrieval/README.md
data/retrieval/cited/20260911-202505_linha_de_base/compare__vs_20260911-201429_linha_de_base.json
data/retrieval/cited/20260911-202505_linha_de_base/compare__vs_20260911-201429_linha_de_base.md
```

---

## 4. Trechos de código mais importantes

### Configuração do embedding

```python
EMBEDDING_MODEL_NAME = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

EMBEDDING_MODEL_REVISION = (
    "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
)

CHUNK_TARGET_TOKENS = 96
CHUNK_OVERLAP_TOKENS = 16
EMBEDDING_MAX_TOKENS = 128
```

---

### Separação entre vetor e prompt

```python
@dataclass(frozen=True)
class DocumentChunk:
    text: str
    section: str
    page_start: int
    page_end: int
    token_count: int
    body: str = ""
```

Na criação do chunk:

```python
DocumentChunk(
    text=prefix + content,
    section=section.title,
    page_start=min(unit.page_start for unit in current),
    page_end=max(unit.page_end for unit in current),
    token_count=token_count,
    body=content,
)
```

Nos metadados:

```python
{
    "section": chunk.section,
    "chunk_index": chunk_index,
    "token_count": chunk.token_count,
    "body": chunk.body or chunk.text,
}
```

Na recuperação:

```python
content=metadata.get("body", content)
```

---

### Porta de curadoria

A lógica central era equivalente a:

```python
if metadata["ingestion_scope"] != "curated":
    reject("ingestion_scope deve ser curated")

if metadata["species"] not in {
    "dog",
    "cat",
    "dog_and_cat",
}:
    reject("species fora do vocabulário canônico")

if metadata["document_type"] not in CURATED_DOCUMENT_TYPES:
    reject("tipo de documento não aceito")

if metadata["validation_status"] not in {
    "approved_by_specialist",
    "approved_with_reservations",
}:
    reject("especialista ainda não aprovou")

if not specialist["name"]:
    reject("especialista sem nome")

if not specialist["date"]:
    reject("especialista sem data")

if not rights["basis"]:
    reject("direitos sem fundamento")

if not rights["checked_by"]:
    reject("direitos sem responsável")

if pdf and not indexing["include_sections"]:
    reject("PDF curado precisa de whitelist de seções")
```

---

### Seleção de perfis

```python
if profile == "experimental":
    return all_paths

if profile == "legacy_rechunk":
    return [
        path
        for path in all_paths
        if document_type(path) == "synthetic_protocol"
    ]

if profile == "curated":
    return [
        path
        for path in all_paths
        if ingestion_scope(path) != "experimental_only"
    ]
```

Depois dessa seleção, o perfil curado ainda executa todas as validações detalhadas.

---

### Ativação atômica

A lógica implementada foi:

```python
staging_name = f"{base_name}__{run_id}"

collection = create_staging_collection(
    staging_name,
    profile=profile,
    source_set_sha256=source_set_sha256,
)

write_all_documents(collection)

assert collection.count() == expected_chunk_count
assert set(collection.get()["ids"]) == set(expected_ids)

manifest = build_ingestion_manifest(
    collection=collection,
    prepared_documents=prepared_documents,
)

write_manifest(staging_name, manifest)

validate_manifest_against_collection(
    staging_name,
    manifest,
)

atomic_write_json(
    active_pointer,
    {
        "schema_version": 1,
        "collection": staging_name,
        "previous_collection": previous_collection,
    },
)
```

A coleção anterior fica preservada para rollback.

---

### Fingerprint

```python
return {
    "chunk_count": len(identifiers),
    "chunk_ids_sha256": sha256(
        "\n".join(sorted(identifiers))
    ),
    "content_sha256": hash_content(
        identifiers,
        documents,
        metadatas,
    ),
    "embedding_model": EMBEDDING_MODEL_NAME,
    "embedding_revision": EMBEDDING_MODEL_REVISION,
    "chunking": {
        "target_tokens": CHUNK_TARGET_TOKENS,
        "overlap_tokens": CHUNK_OVERLAP_TOKENS,
        "max_tokens": EMBEDDING_MAX_TOKENS,
    },
    "topic_counts": topic_counts,
    "species_counts_by_topic": species_counts,
    "source_file_counts": source_counts,
    "validation_status_counts": validation_counts,
}
```

---

### Comparação histórica

A correção principal foi substituir a inferência baseada em sidecars atuais:

```python
# comportamento incorreto antigo
topics = read_topics_from_current_sidecars()
```

por dados registrados na própria rodada:

```python
vector_store = (
    rodada["manifesto"]
    .get("backend_fingerprint", {})
    .get("vector_store", {})
)

topics_indexed = vector_store.get("topic_counts", {})
species_indexed = vector_store.get(
    "species_counts_by_topic",
    {},
)
```

A cobertura passou a exigir também espécie compatível:

```python
def species_covers(required, available):
    has_dog = {"cao", "ambos"} & available
    has_cat = {"gato", "ambos"} & available

    if required == "ambos":
        return bool(has_dog and has_cat)

    if required == "cao":
        return bool(has_dog)

    if required == "gato":
        return bool(has_cat)

    return False
```

---

### Ciclo antes/depois

Foi criado:

```text
scripts/run_ingestion_cycle.py
```

O ciclo executa:

```text
1. fingerprint antes;
2. régua antes;
3. ingestão;
4. fingerprint depois;
5. régua depois;
6. compare;
7. diário;
8. comando de rollback.
```

Em caso de falha, o script mostra explicitamente o comando para reativar a coleção anterior.

---

## 5. O que não foi concluído

Estas partes não foram perdidas por erro de implementação; simplesmente dependiam de ações externas:

* branch não publicada;
* Pull Request não criado;
* CI não executado;
* Docker não estava disponível no ambiente;
* consenso entre três máquinas não executado;
* especialistas ainda não aprovaram as cinco capturas;
* direitos do paper não foram resolvidos;
* repositório continua público;
* mapa clínico continua em rascunho;
* base curada continua vazia.

---

## 6. Como reconstruir rapidamente

### Opção recomendada: novo Codex/Work Mode

Clone o repositório e crie uma branch:

```bash
git clone https://github.com/vinizika/tcc.git
cd tcc
git checkout -b codex/harden-vector-ingestion
```

Depois forneça ao Codex este contexto:

```text
Estou recuperando uma implementação interrompida do repositório
vinizika/tcc.

Commit-base:
c3f09ec5c6a5608e2039a0651a0dec437d19479b

Objetivo:
reimplementar e publicar o endurecimento da ingestão vetorial.

Requisitos:
1. separar corpus curated, experimental e legacy_rechunk;
2. exigir sidecar, hash, especialista, direitos e revisão de PDF;
3. implementar chunking por tokens com target 96, overlap 16 e max 128;
4. separar texto do embedding de metadata.body usado no prompt;
5. implementar staging, manifesto, fingerprint, ponteiro atômico e rollback;
6. corrigir retrieval_compare para usar fingerprints históricos;
7. adicionar species_counts_by_topic;
8. criar ciclo run_ingestion_cycle.py;
9. fixar dependências e Torch CPU;
10. criar GitHub Actions para backend e scripts;
11. adicionar testes unitários e integração real temporária com ChromaDB;
12. atualizar docs, backlog e evidências.

Antes de alterar:
- inspecione o repositório;
- confirme o estado da branch;
- não altere main;
- não indexe documentos experimentais como curated.

Depois:
- rode todos os testes;
- faça git diff --check;
- crie o commit;
- publique a branch;
- abra um PR contra main.
```

---

### Instalação para validação

```bash
python -m venv .venv
source .venv/bin/activate

pip install \
  --index-url https://download.pytorch.org/whl/cpu \
  -r backend/requirements-torch-cpu.txt

pip install \
  -r backend/requirements.txt \
  -r backend/requirements-dev.txt \
  -r scripts/requirements.txt
```

Testes:

```bash
cd backend
python -m pytest -q

cd ../scripts
python -m pytest -q
```

Verificações:

```bash
git diff --check
python -m compileall -q backend/app scripts
pip check
```

---

### Commit e publicação

```bash
git add -A

git commit -m \
  "Harden vector ingestion and document corpus gates"

git push -u origin codex/harden-vector-ingestion
```

Depois, abrir:

```text
https://github.com/vinizika/tcc/compare/main...codex/harden-vector-ingestion
```

E criar o Pull Request com o título:

```text
Endurece ingestão vetorial e separa corpus curado
```

---

## 7. Recomendação prática

O caminho mais rápido é abrir uma nova sessão funcional do Codex e usar este relatório como instrução de recuperação.

Não recomendo adicionar novos documentos ainda. Primeiro devem ser resolvidos:

1. escopo correto do TCC;
2. checklist institucional correto;
3. direitos e visibilidade do repositório;
4. aprovação dos especialistas;
5. validação do mapa e dos casos de recuperação.

A implementação técnica estava avançada e testada, mas nunca chegou ao GitHub remoto.
