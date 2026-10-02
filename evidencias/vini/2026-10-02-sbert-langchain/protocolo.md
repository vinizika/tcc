# Protocolo anterior à execução

Comparação isolada em CPU, sem alterar dependências ou coleção da aplicação.
Base: 61 fichas atuais, search_text integral, cosseno, mesmos metadados.
Modelos: BAAI/bge-m3 (5617a9f61b028005a4858fdac845db406aefb181) e
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
(e8f8c211226b894fcb81acc59f3b34ba3efd5f42), ambos Sentence Transformers.
Braços: RetrievalClient atual e langchain-chroma + RunnableLambda, mesmos
vetores e coleção por modelo. Sem tracing, Gemini ou chamadas clínicas.

Conjuntos: régua 66; oficiais somente split dev com tópico (47);
calibração com tópico (16); independentes (122). Nenhum split teste/prova2.
Três repetições por consulta/braço, ordem alternada, após aquecimento.
Quatro threads Torch, modelos em processos separados. Registrar ranks,
distâncias, hashes do prompt, tempos por requisição, carga/indexação,
RSS máximo do processo e truncamento por tokenizer. Metadados/versões/hashes
dos insumos acompanham os dados. Sem alterar teto nativo dos modelos.

Métricas: hit@1/3/5 e MRR nos primeiros 50 candidatos; mediana e p95 de
busca + construção do prompt. São métricas de recuperação, não acurácia
clínica ou latência total do atendimento. RSS inclui bibliotecas/índice.
Critério: só recomendar troca do embedding se não perder mais de 2 pontos
percentuais de hit@3 em nenhum conjunto e melhorar custo. LangChain deve
preservar documentos e prompt; sua adoção requer benefício funcional além
de eventual diferença pequena de tempo. Não extrapolar para agentes nem
para outros modelos SBERT. Resultados históricos têm ambientes diferentes.
