# Correção conservadora da recuperação vetorial

**Data:** 20/09/2026
**Branch:** `codex/improve-retrieval`
**HEAD inicial:** `66bcce7d92ee5065b9452f1ddb782f278a44efe7`
**Estado:** pronto para revisão em PR, sem ativação

## O que foi corrigido

- A busca passa até 50 candidatos ao reordenador, em vez de cortar cedo demais.
- O reordenador agora compara o relato com título e conteúdo, diversifica fontes e preserva o score vetorial original.
- Fontes que dependem de exposição explícita (carrapato, uva/xilitol, cobra/escorpião, pulga e obstrução urinária) receberam âncoras. Sem o termo no relato, elas não entram.
- Âncoras casam palavras completas: `passa` não casa mais com `passando mal`.
- Somente o relato original pode liberar uma âncora; uma consulta reescrita pela IA não pode inventar uma exposição.
- Documentos exclusivos de gato não entram em relatos de cão, e vice-versa.
- O corte para enviar contexto ao modelo passou de `0.70` para `0.72`, valor comparado na avaliação completa.
- As mesmas regras são usadas na triagem e no endpoint de busca.
- Foi gerado um vocabulário reproduzível a partir de `quadro` e
  `sinais_que_o_tutor_relata` do mapa de assuntos. Ele aproxima a linguagem
  cotidiana em português dos identificadores estáveis dos 61 assuntos.
- A busca agora funde os candidatos vetoriais gerais com uma segunda busca
  restrita aos três assuntos mais prováveis. Assim, um documento correto que
  ficou fora dos 50 primeiros ainda pode chegar ao reordenador.
- A rota usa somente o relato original. Reescritas e textos gerados pela IA
  não podem escolher um assunto clínico.
- Uma rota só libera contexto acima do corte quando há confiança de pelo
  menos `0,60` e vantagem de `0,30` sobre o segundo assunto. A nota vetorial
  original continua disponível separadamente.
- A régua passou a medir o mesmo `ranking_score` que o chat usa, com fallback
  para o score vetorial em snapshots antigos.
- Em uma rota inequívoca, a busca mantém o melhor trecho e seus vizinhos no
  documento. Isso corrigiu o corte que separava a exposição a cebola/alho do
  trecho seguinte sobre anemia, fraqueza e gengiva pálida.
- Trechos que usam literalmente linguagem de encaminhamento emergencial são
  marcados no prompt, sem alterar o texto da fonte nem classificar o caso
  automaticamente.
- Foi adicionada somente ao perfil experimental uma fonte de teletriagem de
  2026 com 1.575 cães. O PDF é CC BY-NC 4.0 e permanece registrado como
  `published_not_locally_validated`.
- Os dois sidecars antigos ainda pendentes (`gastric_dilatation_volvulus` e
  `single_vomiting_or_mild_diarrhea`) foram alinhados à validação da ASAVET
  já informada pelo responsável. Isso não inclui a fonte nova de teletriagem.

## Base de staging

- Coleção final de teste: `veterinary_documents__20260920T233307713518Z__b4fd334d`
- Documentos: 67
- Chunks: 3.494
- Tópicos: 61
- Hash dos IDs: `fd9b72d2e64eb92b79714d375652df6a538fff359d6a27120039374f838943af`
- Ativada apenas numa cópia em `/private/tmp` para os testes. O ponteiro da
  coleção do repositório não foi alterado.

## Resultados reproduzidos

| Cenário | Acertos | Acurácia balanceada | Falsos não urgentes | Falsos urgentes |
|---|---:|---:|---:|---:|
| Sem RAG (referência) | 85/98 | 0,8740 | 8 | 3 |
| RAG anterior | 80/98 | 0,8159 | 11 | 5 |
| RAG corrigido, corte 0,70 | 83/98 | 0,8599 | 10 | 3 |
| RAG corrigido final, corte 0,72 e filtro de espécie | 84/98 | 0,8670 | 9 | 3 |

O RAG corrigido recuperou quatro acertos em relação ao RAG anterior e ficou a um acerto do modelo sem RAG. A diferença de um caso não é estatisticamente conclusiva neste conjunto. Os dois falsos alarmes provocados indevidamente pelo documento de carrapatos foram removidos. A rodada final `20260920-171451_native_gpu_reranker_ancoras_especie_v2` foi retomada e concluída; suas 98 previsões são idênticas às da rodada de corte 0,72 anterior.

Régua de recuperação final (`20260920-171310_reranker_ancoras_especie_v2`): Precision@1 `0,2121`, MRR `0,2912`, 1 caso de 66 acima de `0,70`; o principal documento-ímã caiu de 12 para 11 primeiros lugares. A ordenação ainda é o principal gargalo.

### Segunda etapa: recuperação híbrida pelo mapa

| Rodada | Precision@1 | MRR | Recall@5 | Assuntos encontráveis |
|---|---:|---:|---:|---:|
| Âncoras + espécie (`171310`) | 0,2121 | 0,2912 | — | 15/66 |
| Vocabulário do mapa (`190059`) | 0,4545 | 0,4790 | — | 18/66 |
| Busca roteada (`191623`) | 0,4848 | 0,5515 | 0,6818 | 24/66 |
| Rota com confiança conservadora (`192041`) | **0,5000** | **0,5629** | **0,6818** | 24/66 |
| Vizinhança + teletriagem (`204653`) | **0,5152** | **0,5699** | 0,6667 | 34/66 em primeiro |

Entre o vocabulário sem rota e a busca roteada, 10 casos melhoraram de
posição e nenhum piorou. Contra o estado inicial desta correção, o assunto
certo em primeiro passou de 14/66 para 33/66. O maior documento-ímã caiu de
11 para 5 primeiros lugares.

Com o corte real de `0,72`, 11/66 casos receberam contexto; nos 11 o assunto
esperado estava em primeiro. O caso de cebola/alho (`b08`) é o exemplo do
defeito corrigido: o documento existia, mas não entrava nos 50 candidatos;
agora `allium_toxicosis` fica em primeiro e passa o corte pela rota de alta
confiança.

Na rodada final, 18/66 casos passaram o corte de `0,72`. O assunto correto
ficou em primeiro em 34/66 casos. O Recall@5 oscilou de 0,6818 para 0,6667;
portanto, a melhora foi de ordenação e seleção de contexto, não uma melhora
uniforme em todas as métricas.

### Teste ponta a ponta em português

| Rodada de 10 casos | Acertos | Falsos não urgentes | Falsos urgentes | Casos com contexto |
|---|---:|---:|---:|---:|
| Sem RAG, prompt curto (`194416`) | 8/10 | 2 | 0 | 0 |
| Híbrido v6 (`195827`) | 8/10 | 2 | 0 | 3 |
| Híbrido v8 final (`204758`) | **10/10** | **0** | **0** | 4 |

Os erros `b07` e `b08` foram repetidos isoladamente antes da rodada final.
`b08` passou depois da continuidade entre chunks. `b07` só passou depois de
recuperar a fonte de teletriagem adequada e destacar que o próprio trecho
fala em encaminhamento emergencial. O checklist CoT também foi testado em
`b07`, mas continuou classificando como não emergência e misturou sinais da
fonte com sinais do tutor; por isso ele não foi habilitado.

### Amostra ampliada pareada de 30 casos

Os mesmos 30 relatos foram executados com o mesmo modelo, prompt e ambiente;
a única diferença foi ligar ou desligar o RAG.

| Braço | Acertos | Acurácia balanceada | Falsos não urgentes | Falsos urgentes | Casos com contexto |
|---|---:|---:|---:|---:|---:|
| Sem RAG (`20260920-221607`) | 24/30 | 0,8571 | 6 | 0 | 0 |
| RAG v8 (`20260920-212052`) | **26/30** | **0,9048** | **4** | 0 | 14 |

O RAG corrigiu `b07` (vômito e diarreia repetidos), `b08` (cebola/alho com
palidez) e `b14` (neonato frio e sem mamar). Ele piorou `b27`: o relato de
colapso com gengiva quase branca era correto sem RAG, mas o artigo recuperado
fala de choque e ressuscitação sem ligar de forma direta o trecho aos sinais
do tutor, e o modelo rebaixou o caso. `b15`, `b16` e `b30` falharam nos dois
braços. Portanto, houve ganho líquido de dois casos e de 0,0476 na acurácia
balanceada, mas a amostra ainda deriva do mapa usado pelo roteador; não é uma
prova clínica independente nem justifica ativação.

## Verificações

- Backend: `226 passed`.
- Scripts: `187 passed`.
- `git diff --check`: aprovado.
- `pip check`: nenhuma dependência quebrada.
- `compileall` de `backend/app` e `scripts`: aprovado.
- JSON alterados: válidos; YAML do CI válido.
- `docker compose config --quiet` e composição com o override GPU: aprovados.
  Os containers não foram recriados nesta etapa.
- Régua final de recuperação: 66/66 casos executados.
- Smoke final ponta a ponta: 10/10 casos executados.
- Comparação ampliada pareada: 30/30 com RAG e 30/30 sem RAG.
- A primeira chamada dos testes de backend herdou `DEBUG=release` do shell e
  falhou na validação de configuração antes de coletar testes. Reexecutada com
  `env -u DEBUG`, concluiu normalmente; não foi uma falha do código.

## Limitações e próximo passo

O smoke reproduzido melhorou de 8/10 para 10/10 e a amostra de 30 manteve um
ganho líquido de dois casos. Ainda assim, 30 casos são insuficientes para uma
conclusão clínica. A avaliação histórica completa de 98 casos não foi repetida
com esta última versão porque o `llama3.2:3b` local levou de aproximadamente
um a quatro minutos por resposta. A lentidão está na geração; a recuperação
normalmente concluiu em poucos segundos.

O vocabulário deriva do mesmo mapa usado para elaborar a régua. Portanto, o
ganho de recuperação pode estar otimista e precisa ser confirmado com relatos
parafraseados e separados desse mapa. A nova fonte de teletriagem também deve
ser revisada pela ASAVET antes de qualquer perfil curado. A coleção deve
continuar em staging. Antes de qualquer ativação: executar uma amostra maior
com um modelo de inferência mais rápido, criar um conjunto independente de
relatos, revisar o diff completo e tomar decisão explícita de ativação. O
próximo defeito de recuperação a atacar é a escolha de chunks no tópico
`collapse_and_pale_gums`; os casos `b15` e `b30` também mostram que o
vocabulário ainda não usa os discriminadores de segurança do mapa. Não ativar
automaticamente.

## Repasse para os outros trilhos

### Pet / João — decisão (B2)

- Usar o conjunto independente produzido pelo Ryu para comparar, de forma
  pareada, o mesmo modelo com e sem RAG. As métricas principais continuam
  sendo acurácia balanceada e falsos não urgentes.
- Examinar separadamente os casos em que o contexto mudou a decisão e conferir
  se a justificativa contém apenas sinais relatados pelo tutor. O checklist
  Chain-of-Thought deve permanecer desligado: ele já misturou sinais da fonte
  com sinais do relato no caso `b07`.
- Concluir o driver da matriz de ablação, cruzando as opções dos três trilhos,
  sem ajustar prompt ou limiar sobre o conjunto oficial de teste.

### Ryu — consulta e prova (B1)

- Priorizar a prova oficial independente, com aproximadamente 50 casos de
  desenvolvimento e 100 de teste, redigidos sem copiar o mapa ou os documentos
  da base. Adaptar o runner para texto livre em português e congelar o hash do
  teste.
- Medir novamente Query Rewriting e Multi-Query contra esta coleção; HyDE deve
  continuar desligado enquanto não houver ganho reproduzido.
- Finalizar a medição de latência com o modelo aquecido e substituir o WER de
  voz sintética por uma amostra de áudio real.

### Sequência recomendada para o projeto

1. Revisar este PR e submeter a nova fonte de teletriagem à ASAVET.
2. Produzir e validar a prova independente do Ryu.
3. Rodar no conjunto de desenvolvimento os braços sem RAG e com RAG, mantendo
   modelo, seed, prompt e hardware iguais.
4. Corrigir os erros observados sem consultar o conjunto oficial de teste.
5. Executar a matriz de ablação do Pet e só então avaliar ativação explícita da
   coleção. Até lá, o localhost normal continua usando a coleção ativa antiga.
