até agora eu estou testando como rodar LLM localmente
optei por streamlit pois sabemos usar melhor, e o Prof. Rafael já havia dito que como POC tudo bem usar.

o docker-compose.yml por enquanto esta vazio pq nao implementei o docker ainda
a importancia das bibliotecas sao:

fastapi
--> a gente cria as nossas APIs com essa bib
uvicorn[standard]
--> roda as APIs aqui
requests
--> a gente pede algo por POST para o modelo com essa bib
python-dotenv
--> para ter acesso ao ambiente env (que é tipo definir algumas regras pra esse projeto somente, sem precisar alterar outros projetos)
pydantic
--> a gente define padroes de entrada para as APIs aqui (tipo se campos sao obrigatorios, string...)
streamlit
--> pra criar o front end

## DIA 27/04
Pontos de melhoria que vejo hoje (obvio alem do rag):
1. Padronizar saída JSON
2. Evitar campos com nomes diferentes
3. Evitar erros de escrita
4. Criar validação da resposta
5. Fazer a LLM perguntar mais antes de classificar
6. Conectar a resposta a uma base técnica via RAG

outro ponto, o dataset 1 (emergencia ou nao) precisa de data augmentation.
faremos isso via LLM da seguinte forma:

1. Objetivo do Data Augmentation: gerar essas colunas
    Dangerous = No
    Source = synthetic_llm
    Validation = pending / approved / rejected

2. Limpar e padronizar o dataset
    tem uns Dogs, Dog, dog...

3. Usar o dataset 2 como fonte de vocabulário padrão de sintomas (pois ele é muito melhor organizado), assim a LLM poderá gerar apenas sintomas dentro desse vocabulário pré definido

4. Separar esse vocabulário em sintomas de baixo risco, apenas eles entraram no data augmentation
    Se a combinação tiver sintoma de alto risco não pode virar "NO" automaticamente

5. Gerar linhas com LLM com um prompt controlado tipo:
    Gere 100 linhas sintéticas para um dataset de triagem veterinária.
    Regras:
    - AnimalName deve ser apenas: Dog, Cat
    - Use apenas sintomas da lista permitida.
    - Não use sintomas da lista proibida.
    - Cada linha deve ter exatamente 5 sintomas.
    - Dangerous deve ser sempre "No".
    - Não crie diagnóstico.
    - Não invente sintomas novos.
    - A saída deve ser CSV.
    - Adicione Source = synthetic_llm.

6. Filtros depois da geração: https://arxiv.org/abs/1711.10160 (tecnica similar a weak supervision)
    Remova qualquer linha que:
    contenha sintoma proibido
    tenha sintoma fora do vocabulário
    tenha animal fora da lista permitida
    seja duplicata
    seja igual ou muito parecida com uma linha Dangerous = Yes original
    tenha menos de 5 sintomas válidos
    tenha sintomas contraditórios

7. Label dados sintéticos e originais

8. Validar 20% (pareto) dos dados manualmente

9. Comparar cenários
    Cenário 1:
    Dataset 1 original

    Cenário 2:
    Dataset 1 limpo e normalizado

    Cenário 3:
    Dataset 1 limpo + No sintético validado

    medir:
    balanceamento das classes
    taxa de falsos não urgentes
    recall para urgência
    precisão para não urgência
    F1-score
    consistência da resposta da LLM

## Argumento para data augmentation
Dataset 1 depois da limpeza:
Yes: 819
No: 20
Total: 839

Ou seja:

Yes ≈ 97,6%
No ≈ 2,4%

o Dataset 1 está extremamente desbalanceado para casos perigosos.

Após a etapa de limpeza, o Dataset 1 passou de 871 para 839 registros válidos, com remoção de 2 registros sem rótulo e 30 duplicatas. Mesmo após a limpeza, a base manteve forte desbalanceamento, com 819 registros classificados como perigosos e apenas 20 como não perigosos.

=== Sintomas encontrados no Dataset 2 ===
animais_filtrados: ['Dog', 'Cat']
quantidade_sintomas: 16

- Appetite Loss
- Coughing
- Dehydration
- Diarrhea
- Eye Discharge
- Fever
- Labored Breathing
- Lameness
- Lethargy
- Nasal Discharge
- No (invalido)
- Skin Lesions
- Sneezing
- Swelling
- Vomiting
- Weight Loss

Desses, apenas esses foram escolhidos para o data augmentation de NAO URGENTE, pois sao os sintomas mais leves:
Eye Discharge
Nasal Discharge
Skin Lesions
Sneezing
Lameness

linhas_sinteticas_avaliadas: 32
linhas_sinteticas_aprovadas: 27
linhas_sinteticas_rejeitadas: 5

839 linhas originais
+ 27 linhas sintéticas aprovadas
= 866 linhas totais

escrever detalhes do data augmentation, baseado em estudos, precisa estar bem detalhado os 5 sintomas (a escolha com base na Bia - conhecimento de especialista) e tambem pelo fato de estarmos inserindo dados sinteticos em um dataset

para o dev, usar pydantic para fazer validação de entrada (tenho uma saida, e nessa saida so posso ter essas palavras especificas) - boa integracao com o langchain

next step: criar fluxos mais completos, passando contexto e etc... (usar o banco nao relacional ja para armazenar o historico e etc...)

## Dia 04/05/2026
## Métricas de avaliação

Estou iniciando com acurácia, interpretando o que o modelo consegue identificar como Emergencia ou Nao Emergencia. Além disso, quero identificar também a sua capacidade de me devolver JSONs válidos antes de usar pydantic e o campo format na chamada da ollama.

Para o primeiro teste obtivemos esse resultado:
Avaliação concluída.
total_avaliado: 98
total_acertos: 1
total_erros: 97
json_invalidos: 97
acuracia: 0.0102
acuracia_percentual: 1.02%

percebe-se que a LLM está retornando MUITOS JSONs invalidos. com isso vou implementar a técnica de pydantic + campo format na propria requisicao do ollama e espero ver uma diminuicao no campo json_invalidos:
criei a classe TriagemLLMResponse no pydantic para definir o contrato e mudei o prompt para dizer claramente que quero um JSON. se precisar posteriormente, no proximo teste, posso passar o proprio schema TriagemLLMResponse como format na requisicao do ollama.

essa classe do pydantic que eu criei estava retornando um erro pois o JSON que a LLM devolve esta recorrentemente errado (provavelmente acentuando o recomendação). removi por enquanto e deixei apenas o format: json na requisicao da ollama.
Avaliação concluída.
total_avaliado: 98
total_acertos: 69
total_erros: 29
json_invalidos: 0
acuracia: 0.7041
acuracia_percentual: 70.41%

isso nao necessiariamente é bom pois, no teste filtrado para dog/cat temos 71 YES e 27 NO. ou seja, um modelo que sempre chutasse YES teria 72% de acuracia. isso quer dizer que, por enquanto, o modelo esta abaixo de um baseline ingenuo que sempre chuta YES.

pra nao deixar essa acuracia sozinha, vamos impementar a matriz de confusao:
Quantos Yes ele acertou?
Quantos No ele acertou?
Ele está classificando muitos No como emergência?
Ele está classificando algum caso urgente como não urgente?

segue abaixo a amtriz de confusao:
Matriz de confusão

previsto        EMERGENCIA  NAO_EMERGENCIA  INCERTO  INVALID_JSON
real                                                             
EMERGENCIA              65               4        2             0
NAO_EMERGENCIA          19               4        4             0

Resumo
total_avaliado: 98
emergencia_real: 71
nao_emergencia_real: 27
acertos_emergencia: 65
acertos_nao_emergencia: 4
falsos_nao_urgentes: 4
falsos_urgentes: 19
casos_incertos: 6
json_invalidos: 0

Métricas da classe EMERGENCIA
true_positive: 65
false_positive: 19
false_negative: 6
precision: 0.7738 (Quando o modelo disse EMERGENCIA, quantas vezes ele estava certo?)
precision_percentual: 77.38%
recall: 0.9155 (De todos os casos que eram emergência, quantos o modelo encontrou?)
recall_percentual: 91.55%
f1_score: 0.8387 (F1-score combina precision e recall.)
f1_score_percentual: 83.87%

Métricas da classe NAO_EMERGENCIA
true_positive: 4
false_positive: 4
false_negative: 23
precision: 0.5000
precision_percentual: 50.00%
recall: 0.1481
recall_percentual: 14.81%
f1_score: 0.2286
f1_score_percentual: 22.86%

ela significa que:
71 casos reais de emergência
65 foram classificados corretamente como EMERGENCIA
4 foram classificados como NAO_EMERGENCIA (ESSE é O MAIS CRITICO)
2 foram classificados como INCERTO
0 retornaram JSON inválido

65 acertos em 71 casos
recall_emergencia = 65 / 71 = 91,55%

********************************************

27 casos reais de não emergência
19 foram classificados como EMERGENCIA
4 foram classificados corretamente como NAO_EMERGENCIA
4 foram classificados como INCERTO
0 retornaram JSON inválido

4 acertos em 27 casos
recall_nao_emergencia = 4 / 27 = 14,81%

Isso significa que o modelo está muito ruim em detectar não emergências, o que é bom no ponto de vista conservador de não deixar emergências passarem mas ruim pois não ataca a motivação do projeto que é reduzir o gargalo nas clínicas.

Principais números:
Total avaliado: 98

Acertos totais:
65 + 4 = 69

Acurácia:
69 / 98 = 70,41%

Falsos não urgentes:
4

Falsos urgentes:
19

Casos incertos:
2 + 4 = 6

JSON inválidos:
0

A matriz de confusão mostrou que, após a aplicação do parâmetro format=json, o modelo passou a retornar respostas estruturadas de forma consistente, sem ocorrência de JSON inválido. No entanto, a análise por classe revelou que a acurácia global de 70,41% esconde um comportamento assimétrico. Dos 71 casos reais de emergência, o modelo classificou corretamente 65, resultando em bom desempenho na identificação de casos urgentes. Por outro lado, entre os 27 casos reais de não emergência, apenas 4 foram classificados corretamente, enquanto 19 foram classificados como emergência e 4 como incertos. Isso indica que o modelo adota uma postura conservadora, priorizando a detecção de emergências, mas ainda apresenta baixa capacidade de reconhecer casos não urgentes.

Por enquanto temos essas métricas:
1. Acurácia
2. Matriz de confusão
3. Precision (Quando o modelo disse EMERGENCIA, quantas vezes ele estava certo?)
4. Recall (De todos os casos que eram emergência, quantos o modelo encontrou?)
5. F1-score (F1-score combina precision e recall.)
6. Taxa de JSON inválido/válido
7. Taxa de casos INCERTO
8. Taxa de falso não urgente
9. Taxa de falso urgente

Amanhã espero concluir o dia com essas métricas:
Classificação:
- acurácia
- matriz de confusão
- precision
- recall
- F1-score

Segurança:
- taxa de falso não urgente
- taxa de falso urgente
- taxa de casos incertos

Estrutura da resposta:
- taxa de JSON válido
- taxa de JSON inválido

Desempenho:
- tempo médio de predição -- isso é importante para avaliar 

matriz de confusao é a ultima etapa

podemos mudar o tamanho de modelo e o tipo de modelo
mudando o tipo de modelo usar a mesma quantidade de parametros para comparar

para entrega final de TCC2 fazer uma comparação com diferentes modelos pequenos, pois isso rodaria em um celular

- nao fugir acima de modelos de 16GB

## design of experiments: tabela com diferentes modelos e testes

usar o dataset 2 dizendo que cada linha é uma emergencia ou nao e incluir isso no dataset1.
- transfer learning

-----------30 DE AGOSTO----------------
INCLUIR CEBOLA NOS TESTES
## Estado atual do ChromaDB e da recuperação documental

Foi implementado um ingestor automático para arquivos PDF e TXT, responsável por extrair o texto, dividi-lo em chunks, associar metadados e inserir os registros no ChromaDB. Também foi adotado o modelo multilíngue `paraphrase-multilingual-MiniLM-L12-v2`, utilizando similaridade cosseno. Atualmente, a base contém protocolos sintéticos sobre dificuldade respiratória, intoxicação por chocolate, cebola e alho, convulsões, obstrução urinária, traumas, vômito e diarreia.

A inserção e a busca vetorial estão funcionando, mas os primeiros testes mostraram problemas na ordenação. Nos três casos avaliados, o documento correto apareceu entre os cinco primeiros resultados, porém não ocupou a primeira posição. Portanto, o sistema apresentou bom `Recall@5`, mas baixa precisão na primeira posição.

O diagnóstico indica que os chunks estão grandes, começam algumas vezes no meio de palavras ou frases e incluem conteúdos repetitivos dos PDFs, como avisos, rodapés e referências. Além disso, nem todos os chunks carregam o título e o tema do documento, fazendo trechos genéricos de protocolos diferentes parecerem semanticamente semelhantes. Por isso, ainda não deve ser definido um limiar mínimo de score: os resultados incorretos obtiveram scores maiores do que os documentos corretos.

Como continuação, recomenda-se melhorar a preparação dos documentos: remover cabeçalhos, rodapés e referências repetitivas; dividir o texto por sentenças ou seções; reduzir o tamanho dos chunks; impedir cortes no meio das palavras; e acrescentar título, tema e espécie a cada chunk. Depois disso, o banco deverá ser recriado e os mesmos testes repetidos. Caso a ordenação continue inadequada, deverá ser avaliada a troca para um modelo voltado especificamente à recuperação, como `multilingual-e5-small`, além da implementação efetiva do reranking já previsto na arquitetura.
