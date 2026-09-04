# TCC Vet RAG

Protótipo inicial de uma aplicação de triagem veterinária usando:

- Python
- FastAPI
- Ollama
- Streamlit
- LLM local

A ideia inicial é permitir que o usuário digite o relato de um tutor e receba uma resposta gerada por um modelo local.

---

## Rodando com Docker Compose (forma recomendada)

É o padrão do time: sobe backend, frontend e Ollama juntos, com a mesma
configuração em todas as máquinas.

**1. Crie seu arquivo de configuração local** (uma vez por máquina):

```bash
cp .env.example .env
```

O `.env` não vai para o Git. Ele é opcional — o projeto sobe sem ele, com os
padrões do código —, mas é onde você sobrescreve o que for específico da sua
máquina.

**2. Suba os serviços:**

```bash
docker compose up -d
```

Se a sua máquina tem **GPU NVIDIA**, use o override e ganhe respostas em
segundos em vez de minutos (o modelo passa a rodar na GPU):

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

**3. Baixe o modelo dentro do container** (uma vez; fica guardado no volume):

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

**4. Acesse:**

- Interface: <http://localhost:8501>
- API: <http://localhost:8000>
- Saúde da API: <http://localhost:8000/health/>

Para acompanhar os logs: `docker compose logs -f backend`.
Para derrubar tudo: `docker compose down`.

> Se você tem o Ollama instalado nativamente na máquina, ele ocupa a porta
> 11434 e conflita com o container. O override de GPU já resolve isso (não
> publica a porta); sem ele, encerre o Ollama nativo antes de subir o compose.

### Scripts de dados e avaliação

Os scripts em `scripts/` rodam **fora** do Docker, direto na sua máquina, e
falam com a API pela porta 8000. Crie um ambiente virtual na raiz do projeto:

```bash
python -m venv .venv
```

Ative (`.venv\Scripts\Activate.ps1` no Windows, `source .venv/bin/activate` no
Mac/Linux) e instale as dependências:

```bash
pip install -r scripts/requirements.txt
```

---

## Estrutura atual

```txt
tcc-vet-rag/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── llm.py
│   ├── requirements.txt
│   └── .venv/
│
├── frontend/
│   └── streamlit_app.py
│
├── README.md
└── .gitignore
```

---

## 1. Rodar o Ollama

Primeiro, garanta que o Ollama está instalado e funcionando.

Baixe o modelo usado no projeto:

```bash
ollama pull llama3.2:3b
```

Teste o modelo:

```bash
ollama run llama3.2:3b
```

---

## 2. Criar e ativar o ambiente virtual

Entre na pasta do backend:

```bash
cd backend
```

Crie o ambiente virtual:

```bash
python3 -m venv .venv
```

Ative o ambiente virtual:

### Mac/Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3. Instalar dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

---

## 4. Rodar o backend FastAPI

Ainda dentro da pasta `backend`, execute:

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

```txt
http://localhost:8000
```

Teste no navegador:

```txt
http://localhost:8000/health
```

Se aparecer:

```json
{"status":"ok"}
```

o backend está funcionando.

---

## 5. Rodar a interface Streamlit

Abra outro terminal.

Na raiz do projeto, execute:

```bash
streamlit run frontend/streamlit_app.py
```

Ou, se estiver dentro da pasta `backend`, execute:

```bash
streamlit run ../frontend/streamlit_app.py
```

A interface abrirá no navegador em:

```txt
http://localhost:8501
```

---

## Fluxo atual do sistema

```txt
Usuário digita o relato no Streamlit
        ↓
Streamlit envia o texto para a API FastAPI
        ↓
FastAPI chama o Ollama
        ↓
Ollama executa o modelo local
        ↓
A resposta aparece na tela
```

---

## Observação

O projeto ainda está em fase inicial.

Atualmente ele apenas conecta:

```txt
Streamlit → FastAPI → Ollama → LLM local
```

As próximas etapas serão:

- melhorar o formato da resposta;
- adicionar RAG;
- adicionar banco vetorial;
- futuramente usar Docker para padronizar o ambiente.