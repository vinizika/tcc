# Histórico do animal: documentos anexados e conversas anteriores como contexto

**Data:** 09/11/2026 · **Trilho:** B2 (com arquivos do trilho A, a pedido do João) ·
**Rodada:** 34 · **Commits:** este e o anterior (a regra no prompt)

> O tutor passa a poder **anexar um documento do animal** (exame, receita,
> laudo, carteira de vacinação) e o sistema passa a **lembrar das conversas
> anteriores do mesmo animal**. Os dois entram na decisão como contexto. Sem
> documento e sem conversa anterior, o que vai ao modelo é o de sempre, byte a
> byte: o caminho medido não muda, e nenhum lote lacrado foi usado.

## Por quê

Dois pedidos do João em 09/11. E uma constatação: o sistema **não tinha
memória entre conversas**. Cada conversa mandava ao modelo só as próprias
mensagens e o cadastro do animal. Conferido no código e num teste real: um cão
com "não consegue andar com as patas de trás" (EMERGENCIA) e, numa conversa
nova do mesmo animal, "mais quieta e comeu menos" saiu NAO_EMERGENCIA, sem
nada da conversa anterior no prompt.

## O que foi feito

1. **Leitura de documento** (`POST /workspace/documents/read`): PDF ou foto,
   até 10 MB e 10 páginas, tipo conferido pelo conteúdo. Com o Gemini, o próprio
   modelo lê o arquivo e devolve fatos do animal num formato fixo (tipo, data,
   diagnósticos, resultados alterados, medicações, alergias, vacinas,
   procedimentos), instruído a deixar de fora dados de pessoas e a ignorar
   comandos escritos no arquivo. Com o modelo local, só o texto selecionável de
   um PDF é aproveitado, sem modelo. **O arquivo não é guardado.**
2. **Resumo revisado pelo tutor**: a leitura vira uma proposta de resumo (até
   1.200 caracteres) que o tutor confere, corrige e só então guarda.
3. **Onde fica**: no animal (`poc_pets.documents`), valendo para as próximas
   conversas; sem animal associado, só na conversa. Até 10 documentos; remover
   tira do contexto.
4. **Conversas anteriores**: as últimas 5 do mesmo animal que chegaram a uma
   classificação, com data, primeiro relato (até 280 caracteres) e a
   classificação da ocasião. Sem modelo: é cópia do banco.
5. **No prompt**: um bloco "Histórico do animal", delimitado, entre o cadastro
   e o relato, e uma regra a mais no sistema (`REGRA_HISTORICO`), **só quando o
   bloco existe**. A busca continua recebendo só o relato.
6. **Na tela**: clipe na caixa de mensagem e em "Meus animais"; confirmação
   antes de enviar o arquivo; cartão de revisão; linha "Contexto de … na
   análise" com o que será usado e o botão de remover; nas referências de cada
   resposta, o que do histórico entrou.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| O documento é do animal, não da mensagem | O exame de hoje vale para a conversa de amanhã; é o mesmo problema da memória entre conversas |
| Ler uma vez e guardar só o resumo revisado | O tutor vê e corrige o que a IA leu; dado pessoal não fica; o arquivo não precisa de armazenamento |
| Histórico entre conversas sem modelo | Preferir o determinístico: data, relato e classificação já estão no banco |
| Só na decisão, nunca na busca | Na rodada 22 do Ryu, o cadastro na consulta piorou a recuperação |
| Bloco e regra só quando há histórico | Sem histórico o prompt é idêntico (teste com o hash das mensagens de antes), e as medições seguem valendo |
| O histórico só aumenta a cautela | Um exame normal antigo não pode rebaixar um sinal grave de hoje |
| Emergência nos últimos 7 dias, sem atendimento dito, não vira NAO_EMERGENCIA | É o caso que motivou a rodada; num teste avulso, só pôr a conversa anterior no cadastro não mudou a decisão |
| Doença crônica ou medicação contínua, com sinal de hoje que pode ser piora dela, não vira NAO_EMERGENCIA | Entrou depois da segunda leva de pares: sem a frase, 3 de 5 relatos leves seguiam NAO_EMERGENCIA |
| Nas contas acadêmicas compartilhadas, as conversas anteriores não entram | Lá as conversas são de quem quer que tenha usado o acesso rápido |
| A leitura usa o provedor que o tutor escolheu | Quem escolheu o modelo local não pode ter o arquivo enviado ao Google |
| `ANIMAL_RECORDS_ENABLED` desliga tudo | Volta ao comportamento anterior sem mexer em código |

## Resultado esperado

_Escrito antes de rodar._ Vinte pares de desenvolvimento
([`dados/2026-11-09-pares-historico-do-animal.csv`](dados/2026-11-09-pares-historico-do-animal.csv)),
cada relato sem e com o histórico, duas repetições, pelo caminho do app
(`scripts/experimento_historico_do_animal.py`):

- **N, nunca rebaixar** (4 pares: sinal grave hoje + registro tranquilizador):
  **4 de 4 EMERGENCIA** com o histórico, nas duas repetições. É o critério
  duro: se falhar, a regra não entra.
- **H, emergência recente** (5 pares: emergência nos últimos 3 dias + relato
  leve de hoje, sem dizer que foi atendido): sem histórico espero
  NAO_EMERGENCIA ou INCERTO; com histórico, **nenhuma NAO_EMERGENCIA**.
- **D, documento de doença crônica** (5 pares): com o documento, a decisão
  **nunca menor** que sem ele e **nenhuma NAO_EMERGENCIA**.
- **C, contexto sem relação** (6 pares: relato leve + histórico que não tem a
  ver, ou emergência antiga, ou atendimento já dito): **no máximo 1 de 6 sobe**
  em relação a sem histórico.

**Segunda leva** (dez pares, escrita depois de ver a primeira e antes de rodar a
segunda): na primeira, 9 dos 10 relatos de H e D já saíam INCERTO ou EMERGENCIA
sem histórico, então a leva dizia pouco sobre o efeito. Na segunda, o relato de
hoje é completo e leve, do tipo que sozinho tende a NAO_EMERGENCIA:

- **H2** (5 pares: emergência nos últimos 2 dias + relato leve de hoje, sem
  dizer que foi atendido): com histórico, **nenhuma NAO_EMERGENCIA**.
- **D2** (5 pares: doença crônica documentada + sinal leve de hoje que pode ser
  descompensação): com o documento, **nunca menor**; espero **pelo menos 3 de 5
  subindo** de NAO_EMERGENCIA para INCERTO. Se subirem menos de 3, o documento
  muda a justificativa, mas não a classificação, nesses casos, e isso fica dito.

**Ajuste da regra** (escrito depois da segunda leva, antes de rodar de novo): em
D2 subiram 2 de 5, abaixo do esperado. A regra ganha uma frase para doença
crônica ou medicação de uso contínuo, no molde da frase da emergência recente.
Com ela, os 30 pares rodam de novo, e espero: **D2 com pelo menos 3 de 5
subindo**; **C ainda com no máximo 1 de 6 subindo** (em especial o C6, doença
renal + espirro, segue NAO_EMERGENCIA); N, H e H2 como antes.

Os pares foram escritos por quem escreveu a regra e não passaram por
veterinário: mostram o comportamento, não entram no número final.

## Resultado obtido

Gemini `gemini-3.5-flash-lite`, coleção das fichas, prompt `v1_grounded`, pelo
`poc_pipeline()` do app. 30 pares × 2 braços × 2 repetições = 120 decisões por
versão da regra; dados por decisão em
[`dados/…-resultados-regra-1.jsonl`](dados/2026-11-09-historico-do-animal-resultados-regra-1.jsonl)
e [`dados/…-resultados-regra-2.jsonl`](dados/2026-11-09-historico-do-animal-resultados-regra-2.jsonl).
As duas repetições deram a mesma decisão em 60 de 60 casos, nas duas versões, e
o braço sem histórico saiu igual nas duas rodadas (60 de 60).

**Regra 1** (histórico só aumenta a cautela + emergência recente):

| Grupo | Pares | Sobe com histórico | Desce | NAO_EMERGENCIA com histórico | Critério |
|---|---|---|---|---|---|
| N, nunca rebaixar | 4 | 0 | 0 | 0 (4 EMERGENCIA) | passou |
| H, emergência recente | 5 | 1 | 0 | 0 | passou; 4 já saíam INCERTO sem histórico |
| D, documento de doença crônica | 5 | 0 | 0 | 0 | passou; nenhuma decisão mudou |
| C, contexto sem relação | 6 | 0 | 0 | 6 | passou |
| H2, emergência recente + relato leve | 5 | **5** | 0 | 0 | passou |
| D2, doença crônica + relato leve | 5 | 2 | 0 | 3 | **não passou** (esperado 3 ou mais) |

**Regra 2** (a que ficou: acrescenta a frase da doença crônica):

| Grupo | Pares | Sobe com histórico | Desce | NAO_EMERGENCIA com histórico | Critério |
|---|---|---|---|---|---|
| N, nunca rebaixar | 4 | 0 | 0 | 0 (4 EMERGENCIA) | passou |
| H, emergência recente | 5 | 1 | 0 | 0 | passou |
| D, documento de doença crônica | 5 | 1 | 0 | 0 | passou |
| C, contexto sem relação | 6 | 0 | 0 | 6 | passou |
| H2, emergência recente + relato leve | 5 | **5** | 0 | 0 | passou |
| D2, doença crônica + relato leve | 5 | **5** | 0 | 0 | passou |

Da regra 1 para a 2 mudaram quatro decisões, todas em doença crônica: D2
(diabética fraca e tremendo) de INCERTO para EMERGENCIA; D6 (diabética que
vomitou e não comeu), D8 (cardiopata mais cansado no passeio) e D10 (epiléptica
com tremor dormindo) de NAO_EMERGENCIA para INCERTO. O C6 (doença renal +
espirro) seguiu NAO_EMERGENCIA.

O caso que motivou a rodada: emergência ontem ("não consegue andar com as patas
de trás") e hoje "mais quieta e comeu menos". Sem histórico, NAO_EMERGENCIA;
com histórico, INCERTO: "Como houve uma emergência recente de paralisia nas
patas ontem, a diminuição do apetite hoje exige cautela veterinária."

**Leitura de documento**, num exame fictício de uma página: o Gemini leu a foto
em 2,2 s e o PDF em 1,9 s, devolveu diagnóstico, resultados alterados,
medicação e alergia, e não copiou nome, CPF nem telefone. O texto de um PDF
pelo `pypdf` sai na hora, sem modelo.

**Testes**: backend 343 (25 novos), com o hash das mensagens de antes preso em
`test_prompt_historico.py`; ponta a ponta 15 de 15 (3 novos, sem gastar cota); a
varredura de responsividade da rodada 33, com quatro telas novas, deu 1.478
medições sem falha.

## O que mudou no repositório

| Arquivo | Mudança |
|---|---|
| `backend/app/prompts/triage.py` | `REGRA_HISTORICO`, `com_regra_de_historico` e o bloco opcional em `build_triage_messages` |
| `backend/app/pipeline/chat_pipeline.py` | `animal_records` opcional em `execute` e `_classify` |
| `backend/app/services/animal_records_service.py` | **novo**: leitura do documento, resumo por regra, conversas anteriores, bloco do prompt |
| `backend/app/services/workspace_service.py`, `api/workspace.py`, `schemas/workspace.py` | guardar, listar, remover e levar à análise; `context_used` em cada resposta |
| `backend/app/clients/gemini_llm_client.py` | `read_document`, com as mesmas chaves e esperas do `classify` |
| `backend/app/core/config.py`, `.env.example`, `deploy/env.prod.example` | `ANIMAL_RECORDS_ENABLED`, `MAX_DOCUMENT_UPLOAD_MB` |
| `backend/app/services/fingerprint_service.py` | hash do prompt com a regra do histórico |
| `frontend-react/src` (`AnimalRecords.tsx` novo, `TutorFlow.tsx`, `api.ts`, `types.ts`, `ui.tsx`, `styles.css`) | clipe, confirmação, revisão, contexto na análise, documentos em "Meus animais" |
| `frontend-react/nginx.conf`, `deploy/nginx.prod.conf` | corpo de até 25 MB no Nginx de desenvolvimento; limite por IP na leitura de documento |
| `backend/tests/test_prompt_historico.py`, `test_animal_records.py`, `frontend-react/tests/documents.spec.ts` | **novos** |
| `scripts/experimento_historico_do_animal.py`, `evidencias/joao/dados/` | o experimento e os dados |
| `docs/CONTRATOS.md`, `docs/poc-utilizavel.md`, `README.md` | contratos e operação |

## Observações

- O histórico **não entra nas contas acadêmicas compartilhadas**: lá as
  conversas são de quem quer que tenha usado o acesso rápido. Os documentos
  entram, porque são explícitos e aparecem na tela.
- O efeito aparece no relato **leve e completo**. Quando o relato é vago, o
  sistema já responde INCERTO sem histórico, e o histórico só muda a
  justificativa.
- A regra 2 é cautelosa: um tremor dormindo numa cadela epiléptica vira
  INCERTO. É o lado escolhido do erro.
- A pergunta que o caso pede ("ele foi atendido?") não está no catálogo de
  perguntas do fluxo conversacional. O INCERTO sai com a justificativa certa e
  a pergunta de sempre.
- Os testes antigos da interface, que simulam a API, pegaram um defeito do
  painel novo (resposta fora do formato derrubava a tela). Corrigido.
- O `v2_suficiencia` segue desligado: esta rodada não mexeu nessa decisão.

## Deixado para depois

- Pares validados por veterinário e a regra como braço declarado da medição
  final ([B-84](../backlog.md#b-84)).
- Documentos no encaminhamento à clínica, a pergunta "foi atendido?", o
  arquivo original e a leitura de imagem sem o Gemini
  ([B-85](../backlog.md#b-85)).
- Texto de consentimento ([B-64](../backlog.md#b-64)): documento traz dado de
  pessoas.

## Próximo passo

Medição final no lote teste da prova 2, com o protocolo ainda por escrever
([B-63](../backlog.md#b-63), [B-77](../backlog.md#b-77)). O histórico do animal
não entra nela: os relatos da prova não têm documento nem conversa anterior, e
o prompt, sem eles, é o de sempre.
