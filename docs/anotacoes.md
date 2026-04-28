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