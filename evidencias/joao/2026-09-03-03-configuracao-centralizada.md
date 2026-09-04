# Configuração centralizada do modelo de linguagem

**Data:** 03/09/2026 · **Trilho:** B2 (Decisão) · **Rodada:** 2

## O que foi feito

Todo parâmetro do modelo de linguagem passou a viver em um lugar só,
`backend/app/core/config.py`, com um cliente compartilhado do Ollama em
`backend/app/core/ollama.py`. Junto vieram as configurações que a próxima
rodada precisa: temperatura, seed, tamanho de contexto, modo de saída
estruturada e as flags de liga/desliga das etapas de decisão.

## Por quê

**O projeto só funcionava em um cenário por vez.** O endereço do Ollama estava
escrito à mão em quatro lugares, e em dois formatos incompatíveis:

| Arquivo | Endereço | Funcionava em |
|---|---|---|
| `clients/query_client.py` | `http://ollama:11434` | só dentro do Docker |
| `clients/llm_client.py` | `http://ollama:11434` | só dentro do Docker |
| `llm.py` | `localhost:11434` (via env) | só fora do Docker |
| `scripts/validate_synthetic_no_with_llm.py` | `localhost:11434` | só fora do Docker |

O nome do modelo, `llama3.2:3b`, aparecia escrito em quatro pontos. Trocar de
modelo — que é justamente um dos experimentos previstos no TCC, comparar
modelos pequenos — exigiria caçar todas as ocorrências.

**Determinismo.** A rodada de 04/05 usou a temperatura padrão do Ollama (0.8).
Com temperatura alta, a mesma entrada pode gerar classificações diferentes a
cada execução, e duas rodadas de avaliação deixam de ser comparáveis: não dá
para saber se a diferença veio da mudança que fizemos ou do acaso. Com
`temperature=0` e `seed` fixa, a mesma entrada devolve a mesma saída.

**Tamanho de contexto explícito.** O Ollama trunca o prompt em silêncio quando
ele ultrapassa `num_ctx`, e o que se perde é o começo — justamente as
instruções de como classificar. Como a próxima rodada vai injetar documentos
recuperados no prompt, esse limite deixa de ser teórico. Melhor definir o valor
do que descobrir o corte por um resultado estranho.

## Resultado esperado

- O mesmo código funcionando dentro e fora do Docker, sem editar arquivo.
- As configurações visíveis e documentadas em um `.env.example`.
- Confirmar que a saída estruturada por schema produz os nomes de campo
  exatos — o que resolveria, na origem, o problema de JSON inválido.

## Resultado obtido

Atingido. Dentro do container, `settings.OLLAMA_HOST` resolve para
`http://ollama:11434` (injetado pelo compose) e o padrão do código continua
sendo `localhost` para quem roda fora.

**Teste da saída estruturada.** Chamada real ao modelo, com um schema Pydantic
passado no parâmetro `format`:

| Verificação | Resultado |
|---|---|
| Chaves devolvidas | `classificacao`, `justificativa`, `sinais_de_alerta`, `recomendacao` |
| Validação Pydantic | passou de primeira |
| Tempo da chamada | **8,0s** (GPU) |
| Tokens (prompt/saída) | 73 / 140 |

Os nomes saíram exatos, sem o `recomendação` acentuado que quebrava o parsing
antes. Vale lembrar o histórico: na primeira avaliação de 04/05, **97 das 98
respostas foram JSON inválido**. O `format: "json"` derrubou isso para zero,
mas garantia apenas que a saída era um JSON — não que os campos fossem os
certos. A restrição por schema resolve os dois problemas de uma vez, porque o
formato passa a ser imposto durante a decodificação.

**Observação clínica que merece registro.** No teste, o relato foi "meu
cachorro comeu uma barra de chocolate ao leite inteira há uma hora e está
tremendo e vomitando". O modelo respondeu **`NAO_EMERGENCIA`**, justificando
que "não há informações suficientes". Isso é um falso não urgente — o tipo de
erro mais grave neste projeto, e o que as métricas do time acompanham de perto.

É apenas um caso, sem documentos recuperados e com prompt mínimo, então não é
medição. Mas é exatamente a falha que o RAG existe para corrigir: a base já tem
um protocolo de intoxicação por chocolate e teobromina. Serve como caso de
teste concreto para a próxima rodada — se a geração ancorada mudar essa
resposta, é evidência direta do valor do RAG.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/core/config.py` | endereço e modelo do Ollama; temperatura, seed, contexto e timeout; modo de saída estruturada; flags de decisão (`RETRIEVAL_ENABLED`, `CONTEXT_TOP_K`, `COT_ENABLED`, `SELF_REFINE_ENABLED`); `.env` da raiz atendendo Docker e local |
| `backend/app/core/ollama.py` | **novo** — cliente compartilhado e opções padrão de geração |
| `backend/requirements.txt` | `ollama>=0.4.4`, versão a partir da qual `format` aceita um schema JSON |
| `backend/requirements-dev.txt` | **novo** — pytest e httpx, para os testes da próxima rodada |
| `backend/Dockerfile` | instala as dependências de teste em camada separada, para não invalidar o cache da instalação do torch |
| `scripts/validate_synthetic_no_with_llm.py` | lê endereço e modelo do ambiente |
| `.env.example` | todas as configurações novas, documentadas |

As flags declaradas pelo colega do trilho B1 (`QUERY_REWRITING_ENABLED`,
`MULTI_QUERY_ENABLED`, `HYDE_ENABLED`) foram mantidas com os nomes dele.

## Próximo passo

Substituir a geração simulada pela classificação real ancorada nos documentos
recuperados, usando a saída estruturada validada aqui. O caso do chocolate fica
como teste de aceitação da próxima rodada.
