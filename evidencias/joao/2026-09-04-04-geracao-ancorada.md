# Geração de triagem ancorada nos documentos (matar o mock)

**Data:** 04/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 3
**Commits:** [`a2b9f3c`](https://github.com/vinizika/tcc/commit/a2b9f3c) (estrutura) · [`3b617f0`](https://github.com/vinizika/tcc/commit/3b617f0) (geração real) · limpeza e contratos

> As seções "Resultado esperado" e "Decisões" foram escritas **antes** de
> medir, como manda o padrão destas evidências.

## O que foi feito

A entrega substitui a resposta simulada pela **classificação real de
urgência ancorada nos trechos recuperados**. Ela vai à `main` em três
passos, para o repositório nunca ficar quebrado para quem puxar:

1. **Estrutura** (feito): o pipeline passa a ser configurável por
   requisição — cada etapa pode ser ligada ou desligada, e a resposta diz o
   que rodou, quanto tempo cada etapa levou e o que a busca encontrou. A
   geração continua simulada de propósito, para este passo ser só estrutura.
2. **Geração real** (feito): o modelo classifica usando os documentos, com
   saída estruturada e fontes citadas por número; o mock morreu.
3. **Limpeza** (feito): o classificador antigo e a rota desligada foram
   removidos, e os contratos entre os trilhos ficaram registrados em
   [`docs/CONTRATOS.md`](../../docs/CONTRATOS.md).

## Por quê

O coração do produto ainda não existia. `LLMClient.generate` devolvia um
texto fixo, e a única classificação real do projeto (`llm.py`) estava
desligada e nunca tinha visto um documento recuperado. Sem esta entrega não
há o que medir no Marco 1, e o runner de avaliação não tem alvo.

O passo 1 é o que torna o **estudo de ablação** possível: cada técnica
prevista no artigo (reescrita, multi-query, HyDE, RAG, e depois CoT e
Self-Refine) vira uma chave que o runner liga e desliga por requisição, sem
reiniciar o backend. Sem isso, cada linha da tabela de resultados exigiria
editar código e subir o serviço de novo — o que, além de lento, torna
impossível garantir que só uma variável mudou entre duas medições.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Falha dupla do modelo → `INCERTO` com orientação de procurar atendimento; a API responde 200 e marca a resposta como não estruturada | Conservador e honesto. Não infla nenhuma classe, e mantém a taxonomia de rótulos do baseline antigo, que contava esses casos como JSON inválido |
| 2 | Entrega em três commits (estrutura · geração · limpeza) | A `main` é compartilhada pelos três integrantes; cada passo é revisável sozinho |
| 3 | Documentos abaixo do limiar da busca ainda vão ao classificador, com o score registrado em toda resposta | Descartá-los equivaleria a rodar sem RAG. Passar e medir é o que gera evidência sobre a qualidade da base |
| 4 | O **relato original** vai ao classificador, não a versão reescrita; a reescrita só entra sob uma chave própria, desligada por padrão | A reescrita adiciona julgamento clínico (ver Observações). Usá-la na decisão misturaria a etapa do trilho B1 dentro do resultado do B2 e confundiria a ablação |
| 5 | Um trecho **relevante** pode elevar a classificação e deve ser citado; um trecho sobre **outro** problema é ignorado. Um único sinal grave basta, e a ausência de outros sintomas não torna o caso leve | Escrita em duas etapas: a primeira versão só deixava os documentos "qualificarem" a gravidade, para que um documento irrelevante não empurrasse tudo para emergência. Isso produziu um falso não urgente num caso grave — ver a seção da regressão. A distinção correta é relevância, não impedir que o documento eleve |
| 6 | Modo legado fiel ao `llm.py`: prompt literal, sem documentos, saída apenas em JSON, sem teto de tokens e leitura tolerante dos campos | É a única forma de a comparação com os 70,41% medir a mesma coisa. Verificado: 7 das 98 respostas antigas tinham campos faltando ou com o nome errado |
| 7 | Toda etapa ainda não implementada é **recusada** com erro 400, e nome de opção desconhecido também falha | Uma chave aceita e ignorada produziria uma linha de ablação idêntica à do braço sem ela, sugerindo que a técnica não teve efeito |
| 8 | Sem busca, as etapas de consulta são desligadas automaticamente | Sem recuperação não há consulta a otimizar; gastaria chamadas ao modelo e a configuração ecoada mentiria sobre o que rodou |
| 9 | `sources` passa a listar só os trechos que o classificador viu; a lista completa da busca fica no bloco de depuração | O campo dizia "fontes" mas trazia documentos que não embasaram nada |
| 10 | Estatísticas da busca (quantos vieram, quantos passaram do limiar, score máximo) ficam **fora** do bloco de depuração | O runner precisa delas em toda linha para separar "a geração errou" de "a busca não trouxe nada útil" |
| 11 | Fontes citadas por **número**, resolvido para o documento depois; índice fora do intervalo é descartado e contado | Um modelo de 3B cita índice com confiança, mas não reproduz um identificador de 64 caracteres. Índice inventado não pode virar fonte falsa na tela, mas precisa virar métrica de ancoragem |
| 12 | Sem documentos, o formato de saída **não tem** o campo de fontes | Não havendo o que citar, a restrição de decodificação impede fisicamente o modelo de inventar um número |
| 13 | Repetição consciente do motivo: resposta cortada por limite de tokens é repetida com o dobro de espaço; saída mal formada é repetida com o erro anexado | Com temperatura zero, anexar mensagem a uma resposta truncada faria a segunda tentativa truncar no mesmo ponto |
| 14 | O texto que o tutor lê é montado em código, com o conteúdo do modelo escapado | A interface renderiza markdown: um asterisco solto viraria itálico, "R$ 50" viraria fórmula, ":red[...]" viraria diretiva de cor. Também economiza tokens que seriam gastos gerando cabeçalho e aviso legal |

## Resultado esperado

*(escrito antes de rodar a geração real)*

- **Caso de aceitação:** o relato *"meu cachorro comeu uma barra de chocolate
  inteira há uma hora e está tremendo e vomitando"*, classificado como **não
  emergência** num teste anterior, deve virar **emergência** citando o
  protocolo de intoxicação por chocolate.
- **Controle 1** (mesmo relato, busca desligada): deve continuar errando ou
  ficar incerto. Este braço é o que separa o efeito do **prompt novo** do
  efeito do **RAG** — sem ele, um acerto poderia ser creditado ao RAG sem
  ter vindo dele.
- **Controle 2** (modo legado): deve reproduzir o comportamento antigo.
- Dois relatos adicionais: gata sem urinar há 24h (espera-se emergência) e
  gato espirrando sem outros sinais (espera-se não emergência) — este
  segundo é o tipo de caso em que o sistema falha hoje, com recall de não
  emergência em 14,81%.

Se o resultado for contrário, ele é registrado do mesmo jeito: o valor está
na diferença entre o previsto e o medido.

---

## Resultado obtido

### Testes automatizados: 43

Os primeiros do projeto. Rodam em 0,9s porque nenhum deles sobe o modelo ou
o banco vetorial: o módulo do Chroma é substituído por um dublê antes de
qualquer import, e o modelo por um objeto que devolve respostas fixas.

| Arquivo | Testes | O que garante |
|---|---|---|
| `test_chat_pipeline.py` | 19 | Que cada chave liga e desliga a etapa certa; que o relato original vai ao classificador; que fonte inventada é descartada; que falha vira INCERTO |
| `test_config_resolver.py` | 10 | A semântica de cada braço da ablação: precedência das opções, modo legado forçando as condições antigas, etapa não implementada falhando |
| `test_answer_renderer.py` | 7 | Que o texto do modelo não quebra a formatação da tela, e que pontuação comum não é escapada |
| `test_api_chat.py` | 7 | O contrato HTTP: o frontend continua funcionando, e os campos que a avaliação precisa existem |

O teste mais importante é o que verifica que **a versão reescrita não chega
ao classificador**: é uma regra que se perderia num refactor futuro, e cujo
efeito só apareceria como um número estranho na ablação, meses depois.

### Os 9 cenários medidos

Três relatos × três braços. Os braços existem para responder "quem merece o
crédito pelo acerto": o RAG, o prompt novo, ou nenhum dos dois.

| Caso | Esperado | Com RAG | Sem RAG (só prompt) | Modo legado |
|---|---|---|---|---|
| Cão comeu chocolate, tremendo e vomitando | EMERGENCIA | **EMERGENCIA** ✓ | EMERGENCIA ✓ | EMERGENCIA ✓ |
| Gata sem urinar há 24h | EMERGENCIA | **EMERGENCIA** ✓ | NAO_EMERGENCIA ✗ | EMERGENCIA ✓ |
| Gato espirrando, comendo e brincando | NAO_EMERGENCIA | **NAO_EMERGENCIA** ✓ | NAO_EMERGENCIA ✓ | NAO_EMERGENCIA ✓ |

Formato válido na primeira tentativa em **9 de 9**. Nenhuma citação de
índice inexistente.

#### Caso 1 — chocolate: o acerto não é do RAG

Os três braços acertam. O relato tinha sido classificado como não emergência
num teste anterior, mas aquele teste usava um prompt mínimo, sem definição
das classes nem regras de decisão. Com o prompt completo, o modelo acerta
**mesmo sem documento nenhum** — e o prompt antigo do `llm.py` também.

O detalhe que mais ensina está na recuperação: dos 5 trechos devolvidos pela
busca, **o protocolo de intoxicação por chocolate não estava entre os 3
melhores**. O modelo recebeu "Vômito e diarreia" (0,643), "Intoxicação por
cebola e alho" (0,623) e "Trauma, quedas e hemorragias" (0,600), citou o
primeiro, e ainda assim classificou corretamente — usando conhecimento
próprio, não os documentos. **Nenhum trecho passou do limiar de 0,7 nesta
execução.**

Ou seja: aqui o RAG não ajudou nem atrapalhou, e a citação está tecnicamente
errada, apontando um protocolo genérico de vômito para um caso de
intoxicação.

#### Caso 2 — obstrução urinária: aqui o RAG decide

É o único caso em que os braços divergem, e a diferença é exatamente a
recuperação:

- **Com RAG:** a busca trouxe um único trecho, "Suspeita de obstrução
  urinária em gatos", com 0,7215 — o único acima do limiar. O modelo
  classificou como **emergência** e citou essa fonte.
- **Sem RAG:** mesma pergunta, mesmo prompt, sem documento. Resposta: **não
  emergência**, justificando que *"a gata não está apresentando sintomas
  graves, como dificuldade para respirar ou convulsões"*. Nenhum sinal de
  alerta listado.

**É a primeira evidência concreta, no projeto, de que a recuperação muda a
decisão clínica.** E num caso em que errar é grave: obstrução urinária em
gato mata em poucas horas. O modelo sozinho não sabe que "não urina há um
dia" é emergência; com o protocolo na frente, sabe.

Um caso não é medição — o número que vale virá do runner sobre os 98
relatos. Mas é o primeiro sinal de que o mecanismo funciona, e é o tipo de
caso que a tabela de resultados do TCC precisa mostrar.

#### Caso 3 — espirro: o filtro de relevância funciona

O modelo respondeu não emergência e **não citou fonte nenhuma**, que é o
comportamento correto. O interessante é o que ele ignorou: a busca devolveu
5 trechos, **todos acima do limiar**, sendo o primeiro "Suspeita de
obstrução urinária em gatos" com **0,8183** — o maior score de toda a
rodada, para um relato de espirro.

Isso testa a regra da decisão 5 na prática: o modelo recebeu três protocolos
de emergência irrelevantes e não se deixou levar. Se a regra não existisse,
este seria um falso urgente — exatamente o erro que acontece 19 vezes em 27
no baseline.

### Estabilidade: o mesmo relato dá respostas diferentes

Ao repetir o caso da gata sem urinar, apareceu algo que uma execução só
esconde. **Quatro execuções do relato idêntico, com RAG ligado:**

| Execução | Classificação | Trechos recuperados | Score máximo | Fonte citada |
|---|---|---|---|---|
| 1 | EMERGENCIA ✓ | 1 | 0,7409 | obstrução urinária |
| 2 | EMERGENCIA ✓ | 1 | 0,8205 | obstrução urinária |
| 3 | **NAO_EMERGENCIA** ✗ | 4 | 0,8553 | nenhuma |
| 4 | EMERGENCIA ✓ | 1 | 0,7561 | obstrução urinária |

**Uma em quatro erra**, e erra no sentido perigoso. A causa não é o
classificador, que roda com temperatura zero e seed fixa: é a **etapa de
consulta**, que usa a temperatura padrão do Ollama com seed aleatória. Cada
execução gera consultas diferentes, que recuperam conjuntos diferentes de
trechos. Na execução 3 vieram 4 trechos em vez de 1, e o excesso de contexto
irrelevante levou o modelo a não citar nenhum e rebaixar o caso.

Desligando a etapa de consulta e buscando **direto pelo texto do tutor**, o
resultado muda de figura:

| Execução | Classificação | Score máximo | Primeiro trecho |
|---|---|---|---|
| 1 | EMERGENCIA ✓ | 0,4865 | obstrução urinária |
| 2 | EMERGENCIA ✓ | 0,4865 | obstrução urinária |
| 3 | EMERGENCIA ✓ | 0,4865 | obstrução urinária |

**Idêntico nas três, e correto nas três.** O mesmo vale para o caso do
chocolate: com a etapa de consulta ligada, os trechos e os scores mudam entre
execuções (0,6092 e 0,6709 em duas rodadas); desligada, o resultado é sempre
o mesmo (0,4469).

Três leituras que saem daqui:

1. **A etapa de consulta é a fonte da instabilidade do sistema todo.** Três
   linhas de correção no trilho B1 (fixar temperatura e seed) resolvem, e
   sem isso nenhuma rodada de avaliação com RAG é reproduzível — o que
   inviabiliza comparar duas configurações no estudo de ablação.
2. **Score alto não significa recuperação melhor.** A busca direta teve o
   *menor* score de todos (0,4865 contra 0,74–0,86) e foi a única a acertar
   sempre. A reescrita e o HyDE inflam a similaridade porque aproximam a
   consulta do vocabulário técnico da base — mas aproximam de trechos que não
   são os certos. Isso reforça que o limiar de 0,7 não deve ser usado como
   critério de qualidade enquanto a ordenação não estiver resolvida.
3. **Mais contexto piorou a decisão.** Na execução que errou, o modelo
   recebeu 4 trechos em vez de 1 e se perdeu. Vale testar reduzir o número de
   trechos enviados, o que já é uma chave configurável.

Isto qualifica a conclusão do caso 2: o RAG **muda** a decisão clínica, e para
melhor na maioria das execuções, mas hoje a variação da etapa de consulta faz
o mesmo relato oscilar entre acerto e erro grave. É mais um argumento para o
runner medir sobre os 98 relatos em vez de casos isolados.

### Desempenho por braço

| Braço | Tempo total | Chamadas ao modelo | Tokens de entrada |
|---|---|---|---|
| Modo legado | 1,2 – 1,5s | 1 | ~270 |
| Sem RAG | 1,5 – 2,1s | 1 | ~425 |
| Com RAG | 5,3 – 6,3s | 4 | 870 – 1.460 |

Vazão estável em 85 – 92 tokens/s na GPU. **A etapa de consulta domina o
custo:** 3,2 – 3,6s dos ~5,5s totais, porque são três chamadas ao modelo
(reescrita, multi-query e HyDE) antes de qualquer busca. A classificação em
si leva 1,2 – 2,6s.

Isso importa para o artigo, que trata a latência como requisito ligado ao
conceito de *golden hour*: hoje **63% do tempo é gasto preparando a consulta,
não decidindo**. As três chamadas são independentes entre si e poderiam
rodar em paralelo, ou ser fundidas em uma só. É uma otimização do trilho B1
que valeria medir.

### A regressão que os controles pegaram

A primeira versão do prompt classificou a gata sem urinar como **não
emergência**, com esta justificativa:

> *"O relato do tutor não menciona sinais de dor, vômito, fraqueza ou
> prostração, que são indicadores de urgência. Além disso, a gata está indo
> na caixa de areia, o que pode ser um comportamento normal para um gato que
> não está se sentindo bem."*

O prompt antigo do `llm.py`, mais simples, acertava o mesmo caso. Ou seja: o
prompt novo era **pior** que o antigo, no erro mais grave possível.

**Diagnóstico.** A busca tinha funcionado: trouxe o protocolo certo com
score 0,72. O modelo recebeu o documento correto e mesmo assim rebaixou o
caso, sem citar fonte nenhuma. Não era falha de recuperação, era do prompt.

**Causa.** Uma regra que eu mesmo escrevi para evitar o problema oposto.
Como a busca devolve o trecho mais próximo mesmo sem relevância, e os 7
protocolos da base são todos de emergência, eu queria impedir que um
documento errado empurrasse tudo para emergência. A regra dizia que os
trechos servem apenas para *"julgar a gravidade dos sinais relatados"*. O
modelo interpretou que precisava de sinais **adicionais** para caracterizar
urgência, procurou dor e vômito, não achou, e rebaixou — ignorando que não
urinar já é a emergência.

**Correção**, mantendo a proteção original:

- um único sinal grave basta para emergência, e a ausência de outros
  sintomas não torna o caso leve;
- se um trecho **descrever a situação do relato** e indicar risco,
  classifique como emergência e cite esse trecho;
- se um trecho tratar de **outro** problema, ignore-o.

A distinção passou a ser **relevância**, e não "documento nunca eleva a
gravidade". O caso 3 confirma que a proteção sobreviveu: três protocolos de
emergência irrelevantes, com scores altos, e o modelo os ignorou.

**Insight.** A regra que protege contra um erro pode criar o erro oposto, e
os dois são invisíveis num caso só. Foi preciso um caso de cada lado —
espirro para o falso urgente, obstrução para o falso não urgente — para
achar a formulação que atende aos dois. Isso reforça o desenho do conjunto
de avaliação: medir só emergências esconderia metade dos problemas.

### O que cada mudança impactou

| Mudança | Impacto observado |
|---|---|
| Saída restrita por schema | 9 de 9 respostas válidas na primeira tentativa. Na medição de 04/05, 97 de 98 eram JSON inválido |
| Relato original em vez do reescrito | Sem efeito visível nestes casos, mas evita que o julgamento do reescritor entre na decisão (ver Observações) |
| Fontes citadas por número | Zero citações inventadas em 9 execuções; o mapeamento índice→documento permite marcar quais trechos de fato embasaram a resposta |
| Regra de relevância corrigida | Eliminou o falso não urgente do caso 2, sem reintroduzir falso urgente no caso 3 |
| Formato sem campo de fontes quando não há contexto | O braço sem RAG não tem como inventar citação: a restrição resolve por construção, não por instrução |
| Texto montado em código | Formato idêntico em toda resposta e aviso legal garantido, sem gastar tokens gerando isso |

---

## Observações

Coisas notadas de passagem, para não se perderem. As primeiras afetam outros
trilhos.

1. **A base vetorial estava vazia nesta máquina** (0 registros), porque o
   banco não é versionado e a ingestão precisa rodar uma vez por máquina.
   Depois de rodar: 18 trechos dos 7 protocolos. **Isso muda a leitura do
   commit de 03/09 do Ryu**, que concluiu, ao ver nenhum documento acima de
   0,7 de similaridade, que faltava curadoria na base. Vale conferir se o
   ambiente dele tinha a base populada. Sugestão para o trilho A: colocar o
   passo de ingestão no README.
2. **A ordenação da busca é o problema mais visível do sistema.** Três
   exemplos desta rodada: para o relato de chocolate, o protocolo de
   chocolate não apareceu entre os três melhores, perdendo para "vômito e
   diarreia" e "cebola e alho"; para o relato de espirro, o protocolo de
   **obstrução urinária** apareceu em primeiro com 0,8183 — o maior score de
   toda a rodada. A similaridade não está separando assunto. Material direto
   para o trilho A.
3. **A instabilidade tem tamanho medido: 1 erro em 4 execuções** do mesmo
   relato, no caso da gata (ver a seção de estabilidade). Desligando a etapa
   de consulta, as três execuções ficam idênticas e corretas. É a pendência
   mais urgente entre trilhos hoje: sem seed fixa na consulta, nenhuma
   rodada de avaliação com RAG é reproduzível.
4. **O HyDE gerou uma doença inexistente.** Num dos testes, o documento
   hipotético começava com *"Síndrome de Sífilo da Cadeia de Reações Imunes
   (SCR)"*, que não existe. Como esse texto vai direto à busca como consulta,
   uma alucinação assim ajuda a explicar a ordenação ruim da observação 2.
   Não é erro de implementação: é o comportamento esperado de um modelo de 3
   bilhões de parâmetros escrevendo um trecho técnico sem âncora. Vale medir
   o HyDE ligado e desligado na régua de recuperação antes de mantê-lo.
   Trilho B1.
5. **A reescrita de consulta adiciona interpretação.** O relato *"meu gato
   está espirrando"* virou *"gato apresentando espirro, sintoma que requer
   avaliação veterinária imediata"* — um juízo de urgência que não estava no
   relato, apesar da instrução explícita "nunca adicione informações que não
   estavam no relato original". É o motivo da decisão 4. Trilho B1.
6. **As três chamadas da etapa de consulta não fixam temperatura nem seed**,
   usando o padrão do Ollama (0.8, aleatório). São três linhas para
   corrigir, com o que já existe em `core/ollama.py`. Trilho B1.
7. **A etapa de consulta custa 63% do tempo de resposta.** Três chamadas
   sequenciais ao modelo antes de qualquer busca. Elas são independentes e
   poderiam rodar em paralelo, ou ser fundidas numa só chamada que devolve
   tudo. Relevante para o requisito de latência do artigo. Trilho B1.
8. **O modelo alucina detalhes na justificativa.** Na resposta do caso 2, o
   texto afirma que *"a presença de sangue na urina é um sinal de dor e
   inflamação"* — o tutor nunca mencionou sangue. O campo de sinais de alerta
   ficou correto (só o que estava no relato), mas a justificativa livre
   escapou. Vale acrescentar ao runner uma métrica de "sinal citado que não
   está no relato", e é um bom argumento a favor do Self-Refine previsto para
   a etapa E5.
9. **`RERANK_TOP_K` e `CONTEXT_TOP_K` se sobrepõem.** A primeira é do trilho
   A e hoje não é usada; quando o re-ranking real entrar e cortar em 3, pedir
   5 trechos de contexto devolverá 3 em silêncio. Combinar quem manda antes
   que vire um número inexplicável em alguma rodada.

## Próximo passo

O **runner de avaliação**: é ele que transforma estes casos isolados em
número sobre os 98 relatos e permite a comparação com os 70,41% do baseline.
A seção de estabilidade mostra por que isso é necessário — com uma execução
só, o mesmo relato pode dar acerto ou erro grave.

Antes disso, levar ao Ryu a correção de temperatura e seed na etapa de
consulta: enquanto ela não entrar, nenhuma rodada com RAG é reproduzível, e
o estudo de ablação não se sustenta.
