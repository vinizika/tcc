# Geração de triagem ancorada nos documentos (matar o mock)

**Data:** 04/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 3
**Commits:** [`a2b9f3c`](https://github.com/vinizika/tcc/commit/a2b9f3c) (estrutura) · [`906bd72`](https://github.com/vinizika/tcc/commit/906bd72) (evidência) · geração real e limpeza a seguir.

> As seções "Resultado esperado" e "Decisões" foram escritas **antes** de
> medir. Falta apenas a limpeza (parte 3).

## O que foi feito

A entrega substitui a resposta simulada pela **classificação real de
urgência ancorada nos trechos recuperados**. Ela vai à `main` em três
passos, para o repositório nunca ficar quebrado para quem puxar:

1. **Estrutura** (feito): o pipeline passa a ser configurável por
   requisição — cada etapa pode ser ligada ou desligada, e a resposta diz o
   que rodou, quanto tempo cada etapa levou e o que a busca encontrou. A
   geração continua simulada de propósito, para este passo ser só estrutura.
2. **Geração real** (feito): o LLM classifica usando os documentos, com
   saída estruturada e fontes citadas por número; o mock morreu.
3. **Limpeza** (a seguir): remoção do classificador antigo desligado e da
   rota morta.

## Por quê

O coração do produto ainda não existe. `LLMClient.generate` devolve um
texto fixo, e a única classificação real do projeto (`llm.py`) está
desligada e nunca viu um documento recuperado. Sem esta entrega não há o
que medir no Marco 1, e o runner de avaliação não tem alvo.

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
| 5 | Um trecho **relevante** pode elevar a classificação e deve ser citado; um trecho sobre **outro** problema é ignorado. Além disso, um único sinal grave basta, e a ausência de outros sintomas não torna o caso leve | Escrita em duas etapas: a primeira versão só deixava os documentos "qualificarem" a gravidade, para que um documento irrelevante não empurrasse tudo para emergência (os 7 protocolos da base são todos de emergência). Isso produziu um falso não urgente num caso grave — ver "regressão que os controles pegaram". A distinção correta é relevância, não impedir que o documento eleve |
| 6 | Modo legado fiel ao `llm.py`: prompt literal, sem documentos, saída apenas em JSON, sem teto de tokens e leitura tolerante dos campos | É a única forma de a comparação com os 70,41% medir a mesma coisa. Verificado: 7 das 98 respostas antigas tinham campos faltando ou com o nome errado |
| 7 | Toda etapa ainda não implementada é **recusada** com erro 400, e nome de opção desconhecido também falha | Uma chave aceita e ignorada produziria uma linha de ablação idêntica à do braço sem ela, sugerindo que a técnica não teve efeito |
| 8 | Sem busca, as etapas de consulta são desligadas automaticamente | Sem recuperação não há consulta a otimizar; gastaria chamadas ao modelo e a configuração ecoada mentiria sobre o que rodou |
| 9 | `sources` passa a listar só os trechos que o classificador viu; a lista completa da busca fica no bloco de depuração | O campo dizia "fontes" mas trazia documentos que não embasaram nada |
| 10 | Estatísticas da busca (quantos vieram, quantos passaram do limiar, score máximo) ficam **fora** do bloco de depuração | O runner precisa delas em toda linha para separar "a geração errou" de "a busca não trouxe nada útil" |

## Resultado esperado

*(escrito antes de rodar a geração real)*

- **Caso de aceitação:** o relato *"meu cachorro comeu uma barra de chocolate
  inteira há uma hora e está tremendo e vomitando"*, hoje classificado como
  **não emergência** sem contexto, deve virar **emergência** citando o
  protocolo de intoxicação por chocolate.
- **Controle 1** (mesmo relato, busca desligada): deve continuar errando ou
  ficar incerto. Este braço é o que separa o efeito do **prompt novo** do
  efeito do **RAG** — sem ele, um acerto poderia ser creditado ao RAG sem
  ter vindo dele.
- **Controle 2** (modo legado): deve reproduzir o comportamento antigo.
- Dois relatos adicionais para checar o outro lado: gata sem urinar há 24h
  (espera-se emergência) e gato espirrando sem outros sinais (espera-se não
  emergência) — este segundo é o tipo de caso em que o sistema atual falha,
  com recall de não emergência em 14,81%.

Se o resultado for contrário, ele é registrado do mesmo jeito: o valor está
na diferença entre o previsto e o medido.

## Resultado obtido

### Parte 1 — estrutura

| Verificação | Resultado |
|---|---|
| Testes automatizados (os primeiros do projeto) | **28 passaram em 1,06s** |
| Braço "LLM puro" (busca desligada) | 0 documentos, nenhuma chamada ao modelo, **0,0s** |
| Caminho completo com RAG | 3 trechos usados; consulta 6,55s, busca 0,19s |
| Rota `/search` (trilho A) | intacta |
| Frontend | responde normalmente |
| Relato vazio · etapa inexistente · opção desconhecida | 422 · 400 · 422 |
| Ollama | um modelo carregado, 4096 de contexto, sem recarga entre etapas |

### Parte 2 — geração real

Testes automatizados: **43 passam**. Cada caso foi rodado em três braços,
para separar o efeito do prompt novo do efeito do RAG.

| Caso | Esperado | Com RAG | Sem RAG (só prompt) | Modo legado |
|---|---|---|---|---|
| Cão comeu chocolate, tremendo e vomitando | EMERGENCIA | **EMERGENCIA** | EMERGENCIA | EMERGENCIA |
| Gata sem urinar há 24h | EMERGENCIA | **EMERGENCIA** | NAO_EMERGENCIA | EMERGENCIA |
| Gato espirrando, comendo e brincando | NAO_EMERGENCIA | **NAO_EMERGENCIA** | NAO_EMERGENCIA | NAO_EMERGENCIA |

**O caso de aceitação passou**, mas não pelo motivo previsto. O relato do
chocolate era classificado como não emergência num teste anterior, feito com
um prompt mínimo; com o prompt completo desta entrega ele acerta **mesmo sem
busca**, e o modo legado também acerta. Ou seja: o mérito é do prompt, não do
RAG. Sem os braços de controle, esse acerto teria sido creditado ao RAG por
engano — foi exatamente para isso que eles existiram.

**O valor do RAG apareceu em outro caso.** Na gata sem urinar, o mesmo prompt
com e sem busca dá respostas diferentes: com o protocolo de obstrução urinária
recuperado, o sistema classifica como emergência e cita a fonte; sem ele,
classifica como não emergência. É a primeira evidência concreta, no projeto,
de que a recuperação muda a decisão clínica — e num caso em que errar é grave,
já que obstrução urinária em gato mata em poucas horas.

Um caso não é medição. O número que vale virá do runner sobre os 98 relatos.
Mas é o primeiro sinal de que o mecanismo funciona.

**Desempenho:** 10,4s por requisição completa (7,4s nas três chamadas da etapa
de consulta, 0,2s na busca, 2,8s na classificação), a 85,7 tokens/s na GPU.
Formato válido na primeira tentativa em todos os casos.

### Uma regressão que os controles pegaram

A primeira versão do prompt classificou a gata sem urinar como **não
emergência**, com esta justificativa: *"o relato não menciona sinais de dor,
vômito, fraqueza ou prostração, que são indicadores de urgência"*. O modo
legado, mais simples, acertava o mesmo caso.

Investigando: a busca tinha funcionado, e trouxe o protocolo certo com score
0,72 — o modelo recebeu o documento correto e mesmo assim rebaixou o caso, sem
citar fonte nenhuma. Falha de prompt, não de recuperação.

A causa foi uma regra que escrevi para evitar o problema oposto (decisão 5):
como a busca devolve o documento mais próximo mesmo sem relevância, e os 7
protocolos da base são todos de emergência, eu queria impedir que um documento
errado empurrasse tudo para emergência. A regra dizia que os trechos servem
apenas para "julgar a gravidade dos sinais relatados". O modelo entendeu que
precisava de sinais adicionais, procurou dor e vômito, não achou, e rebaixou —
ignorando que não urinar já é a emergência.

Correção aplicada, mantendo a proteção original:

- um único sinal grave basta para emergência, e a ausência de outros sintomas
  não torna o caso leve;
- se um trecho **descrever a situação do relato** e indicar risco, classifique
  como emergência e cite esse trecho;
- se um trecho tratar de **outro** problema, ignore-o.

A distinção passou a ser relevância, e não "documento nunca eleva a
gravidade". Depois da correção, os três casos ficaram corretos nos braços com
RAG, e o falso não urgente desapareceu.

## O que mudou no repositório

**Parte 1 — estrutura.** Arquivos novos: os modelos de configuração e
instrumentação (`schemas/triage.py`), o resolvedor que decide o que roda
(`pipeline/config_resolver.py`), a estrutura de resultado
(`pipeline/result.py`) e a dependência da rota (`api/deps.py`). Reescritos:
`pipeline/chat_pipeline.py` (clientes injetáveis, todas as etapas
respeitando as chaves, tempos por etapa) e `services/chat_service.py`, que
deixou de ser repasse e virou o tradutor para o formato da API. Aditivos:
`schemas/chat.py` e `core/config.py`. Novos testes em `backend/tests/`.

Duas correções aproveitadas no caminho: o tratador de exceções devolvia
sempre 400, ignorando o código definido pela exceção; e passou a existir uma
exceção específica para "etapa ainda não implementada".

**Mudanças de comportamento declaradas:** as chaves
`QUERY_REWRITING_ENABLED` e `MULTI_QUERY_ENABLED` passam a ter efeito real
(estavam declaradas, mas o pipeline nunca as consultava — só o HyDE era
verificado); e `sources` passa a refletir apenas o que o classificador viu.

## Observações

Coisas notadas de passagem, para não se perderem. As três primeiras afetam
outros trilhos.

1. **A base vetorial estava vazia nesta máquina** (0 registros), porque o
   banco não é versionado e a ingestão precisa rodar uma vez por máquina.
   Depois de rodar: 18 trechos dos 7 protocolos. **Isso muda a leitura do
   commit de ontem do Ryu**, que concluiu, ao ver nenhum documento acima de
   0,7 de similaridade, que faltava curadoria na base. Com a base populada,
   **três documentos passam de 0,7** (máximo 0,741) para o caso do
   chocolate. A conclusão anterior provavelmente veio de uma base vazia, e
   não de ausência de protocolo. Vale conferir no ambiente dele. Sugestão
   para o trilho A: colocar o passo de ingestão no README.
2. **O problema de ordenação está confirmado com números.** Para o relato do
   chocolate, a busca devolveu, nesta ordem: intoxicação por **cebola e
   alho** (0,7411), vômito e diarreia (0,7256) e só então intoxicação por
   **chocolate** (0,7021). O documento certo em terceiro, atrás de um
   veneno diferente. É exatamente o diagnóstico do handover de 30/08, agora
   reproduzível — material direto para o trilho A.
3. **O HyDE gerou uma doença inexistente.** Para o mesmo relato, o documento
   hipotético começava com *"Síndrome de Sífilo da Cadeia de Reações Imunes
   (SCR)"*, que não existe. Como esse texto vai direto à busca vetorial como
   consulta, uma alucinação assim ajuda a explicar a ordenação ruim do item
   anterior. Não é erro de implementação — é o comportamento esperado de um
   modelo de 3 bilhões de parâmetros escrevendo um trecho técnico sem
   nenhuma âncora. Vale medir o HyDE ligado e desligado na régua de
   recuperação antes de mantê-lo. Trilho B1.
4. **A reescrita de consulta também adiciona interpretação.** O relato
   *"meu gato está espirrando"* virou *"gato apresentando espirro, sintoma
   que requer avaliação veterinária imediata"* — o modelo acrescentou um
   juízo de urgência que não estava no relato, apesar da instrução explícita
   "nunca adicione informações que não estavam no relato original". É o
   motivo da decisão 4 acima. Trilho B1.
5. **As três chamadas da etapa de consulta não fixam temperatura nem seed**,
   então usam o padrão do Ollama (0.8, aleatório). Consequência: mesmo com o
   classificador determinístico, o contexto muda a cada execução e duas
   rodadas de avaliação com RAG não são estritamente comparáveis. São três
   linhas para corrigir, usando o que já existe em `core/ollama.py`. Trilho
   B1.
6. **`RERANK_TOP_K` e `CONTEXT_TOP_K` se sobrepõem.** A primeira é do trilho
   A e hoje não é usada; quando o re-ranking real entrar e cortar em 3, pedir
   5 trechos de contexto devolverá 3 em silêncio. Combinar quem manda antes
   que vire um número inexplicável em alguma rodada.

## Próximo passo

Parte 3: apagar o classificador antigo, que virou código morto, e registrar
os contratos entre os trilhos. Depois disso, o runner de avaliação — é ele
que transforma estes três casos em número sobre os 98 relatos, e permite
comparar com os 70,41% do baseline.
