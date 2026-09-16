# Protótipo demonstrativo de encaminhamento

Este diretório contém o protótipo oficial de **demonstração** do fluxo entre
tutor e clínica. Ele não é o frontend real iniciado pelo Docker Compose. O
entrypoint continua sendo `mock/streamlit_app_mock.py` e funciona sem backend,
Ollama, Supabase, MongoDB ou ChromaDB.

## O que a demonstração cobre

O tutor envia um relato fictício, responde a uma pergunta complementar e vê
uma pré-triagem simulada. No cenário de emergência, pode abrir o mapa, filtrar
e ordenar três clínicas fictícias, examinar detalhes, escolher uma delas,
revisar todos os dados e consentir antes de concluir o envio simulado.

O dashboard da clínica possui métricas derivadas da sessão, fila com filtros,
detalhe em abas, estados do caso, eventos e conversa manual. Cada clínica vê
somente os casos destinados ao próprio identificador. Depois do encaminhamento,
as mensagens são apenas entre tutor e clínica; a IA não responde.

Telas principais:

- Área do tutor: perfil, chat, classificação, busca, mapa, detalhes e revisão;
- Área da clínica: seleção da unidade, métricas, fila e detalhe do caso;
- conversa humana simulada e histórico de eventos do caso.

## Como executar

Execute os comandos a partir da raiz do repositório.

macOS/Linux:

```bash
python3 -m venv .venv-mock
source .venv-mock/bin/activate
python -m pip install -r frontend/requirements.txt
python -m streamlit run mock/streamlit_app_mock.py --server.port 8502
```

Windows PowerShell:

```powershell
python -m venv .venv-mock
.venv-mock\Scripts\Activate.ps1
python -m pip install -r frontend/requirements.txt
python -m streamlit run mock/streamlit_app_mock.py --server.port 8502
```

Abra <http://localhost:8502>.

## Testes

Os testes da lógica não importam Streamlit e podem rodar isoladamente:

```bash
python -m pytest mock/tests -q
```

Para executar todas as suítes no ambiente de desenvolvimento do projeto:

```bash
python -m pytest mock/tests scripts/tests -q
cd backend
DEBUG=True python -m pytest -q
```

O `DEBUG=True` evita que uma variável `DEBUG` incompatível definida pelo
sistema operacional sobreponha a configuração Pydantic do backend.

## Estrutura

- `demo_data.py`: localização, tutor, animal e clínicas fictícias;
- `domain.py`: `Clinic`, `Tutor`, `Pet`, `Triage`, `Case`, `Message` e
  `CaseEvent`;
- `demo_service.py`: regras puras, isolamento por clínica e adaptadores locais;
- `streamlit_app_mock.py`: apresentação e navegação;
- `tests/`: testes da lógica independente da renderização.

## Limitações e segurança de comunicação

Todos os nomes, endereços, telefones, distâncias, tempos, avaliações,
quantidades de avaliações, horários, serviços e disponibilidades são
fictícios. A localização é fixa e simulada. O mapa não consulta Google Maps,
não traça rota e não confirma a existência de nenhuma clínica.

A classificação é uma pré-triagem simulada, nunca diagnóstico, prescrição,
reserva ou decisão médica. Nada sai do processo local do Streamlit; atualizar
o navegador pode preservar a sessão, mas reiniciar o processo ou usar
“Reiniciar demonstração” apaga o estado.

## Contrato futuro sugerido

As funções em `demo_service.py` delimitam as operações que futuramente podem
ser trocadas por uma integração autenticada:

| Adaptador atual | Integração futura necessária |
|---|---|
| `get_location` | localização consentida do dispositivo |
| `list_clinics` / `get_clinic` | catálogo verificado de clínicas |
| `create_referral` | criação idempotente de encaminhamento após consentimento |
| `list_clinic_cases` | fila autenticada e paginada por clínica |
| `update_status` | atualização autorizada, com trilha de auditoria |
| `send_message` | canal humano autenticado e notificações |
| `get_history` | histórico persistente e auditável |

Esse contrato é apenas uma proposta do mock. Ele não corresponde a endpoints
existentes e não deve ser confundido com `/chat/`, `/search/`, `/voice/`,
`/health/`, tutores, pets ou conversas documentados em `docs/CONTRATOS.md`.

Antes de uma integração real ainda serão necessários autenticação, autorização
por clínica e tutor, consentimento e retenção compatíveis com LGPD, fonte
verificável para os dados das clínicas, disponibilidade confirmada, serviço de
mapas/rotas e persistência transacional. Nenhuma dessas integrações é
apresentada como funcional nesta versão.
