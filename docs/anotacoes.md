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