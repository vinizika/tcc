# O cadastro do pet ajuda a decidir?

**Data:** 06/10/2026 · **Trilho:** B1 (Consulta, frente prova) · **Rodada:** 20 · **Commit:** este

## O que foi feito

O app do Vinicius (workspace) manda à IA que decide, junto com o relato, os
dados que o tutor cadastrou do animal: nome, espécie, idade, peso, raça e
histórico ([`workspace_service.py`](../../backend/app/services/workspace_service.py),
bloco "Dados cadastrais do animal" do prompt). **Nenhuma medição do projeto
testou isso**: todas as provas mandam só o texto. Esta rodada mede, num
experimento pequeno e de desenvolvimento, se o cadastro muda a decisão quando
deveria e não muda quando não deveria.

**O desenho: pares gêmeos.** Oito pares em que o **relato é idêntico** e só o
cadastro difere, de um jeito que, pelo mapa de assuntos, muda a urgência:

| Par | O mesmo relato | Cadastro A → rótulo | Cadastro B → rótulo |
|---|---|---|---|
| p1 | vai toda hora na caixinha, faz força, sai pouco | gato **macho** → EMERGENCIA (obstrução uretral) | gata **fêmea** → NAO_EMERGENCIA (cistite) |
| p2 | passei o antipulgas de cachorro grande | **gato** → EMERGENCIA (permetrina) | **cão** de 30 kg → NAO_EMERGENCIA (uso correto) |
| p3 | mordiscou folhas e flor de lírio | **gata** → EMERGENCIA (lírio) | **cadela** → NAO_EMERGENCIA (comeu fora da dieta) |
| p4 | não comeu hoje, quietinho, dormindo | **filhote** yorkshire de 0,8 kg → EMERGENCIA (hipoglicemia) | adulto de 12 kg → NAO_EMERGENCIA (comendo menos) |
| p5 | vomitou uma vez, não comeu, mais parada | gata **diabética com insulina** → EMERGENCIA (cetoacidose) | gata jovem saudável → NAO_EMERGENCIA (vômito isolado) |
| p6 | tosse seca, respirando um pouco mais rápido dormindo | idoso **cardiopata** → EMERGENCIA (insuficiência cardíaca) | jovem que **voltou do hotelzinho** → NAO_EMERGENCIA (tosse dos canis) |
| p7 | tremendo, agitada, ofegante | **amamentando 5 filhotes** → EMERGENCIA (eclâmpsia) | castrada → NAO_EMERGENCIA (tremor sem convulsão) |
| p8 | bebendo muita água, quietinha, comendo menos | **não castrada, cio há 5 semanas** → EMERGENCIA (piometra) | **castrada** → NAO_EMERGENCIA (investigar sede) |

Mais **4 controles**, em que o cadastro não deveria mudar nada (atropelado
sangrando, convulsão, espirro leve, comeu miolo de pão). Casos em
[`dados/2026-10-06-casos-cadastro-pet.csv`](dados/2026-10-06-casos-cadastro-pet.csv).

**Como roda.** Cada relato vai à IA **sem cadastro** e **com cadastro**, pelo
mesmo caminho do primeiro turno do app: o `poc_pipeline()` do workspace, com
as opções que o `WorkspaceService.process` usa, o contexto montado no mesmo
formato, Gemini como atendente, busca nas fichas só com o texto do tutor. Duas
repetições por condição, por causa da variação do Gemini (B-77).

## Por quê

Ponto 1 da lista combinada com o Ryu em 06/10. O cenário do projeto é: o tutor
cadastra o pet antes, e o sistema decide "com base no que eu falei e nas
informações do pet". A segunda metade dessa frase nunca foi medida.

## Decisões desta rodada

| # | Decisão | Motivo |
|---|---|---|
| 1 | Pares gêmeos, com o relato idêntico | Sem cadastro, a IA recebe exatamente o mesmo texto nos dois casos do par e, no máximo, acerta um. Só o cadastro pode resolver o par: o efeito fica isolado |
| 2 | Rótulo pela urgência do mapa de assuntos (`imediato` → EMERGENCIA; `ate_24h`/`rotina` → NAO_EMERGENCIA) | É a referência do projeto. **Não foram validados por veterinário**: o experimento é de desenvolvimento, não dá número para o TCC |
| 3 | Sexo, castração, gestação e doenças vão no campo **histórico** | O cadastro do app **não tem** campos de sexo, castração nem gestação, e eles decidem 3 dos 8 pares |
| 4 | Fora da prova 2 | É uma pergunta diferente, e a prova 2 não tem cadastro |

**Muralha, por honestidade:** os casos foram escritos por mim, a partir do mapa
de assuntos. Nesta sessão eu li uma ficha (a do cio), que não entra em nenhum
par.

## Resultado esperado

_Escrito antes de rodar._

- **Sem cadastro:** como o texto do par é o mesmo, espero a IA acertar um caso
  de cada par, ou nenhum se responder INCERTO: **no máximo 8 de 16**, e **0 pares
  resolvidos**.
- **Com cadastro:** espero **pelo menos 6 dos 8 pares resolvidos** (os dois
  casos certos), nas duas repetições.
- **Controles:** a mesma resposta certa com e sem cadastro, 4 de 4.

**Critério de "o cadastro ajuda":** com cadastro, ≥ 6 de 8 pares resolvidos e os
4 controles sem mudança. Se ficar abaixo disso, o cadastro existe no app mas não
pesa na decisão como o cenário supõe.

## Resultado obtido

`python /tmp/experimento_cadastro_pet.py` no container, 80 decisões (20 casos ×
2 braços × 2 repetições), Gemini `gemini-3.5-flash-lite`, coleção das fichas;
dados por decisão em
[`dados/2026-10-06-cadastro-pet-resultados.jsonl`](dados/2026-10-06-cadastro-pet-resultados.jsonl).

| Braço (repetição) | Casos dos pares certos (de 16) | Pares resolvidos (de 8) | Emergências perdidas (de 8) | Falsos alarmes (de 8) | INCERTO | Controles (de 4) |
|---|---|---|---|---|---|---|
| Sem cadastro (1ª) | 5 | 0 | 3 | 4 | 7 | 4 |
| Sem cadastro (2ª) | 4 | 0 | 4 | 4 | 8 | 4 |
| **Com cadastro (1ª)** | 9 | **2** | **1** | 3 | 4 | 4 |
| **Com cadastro (2ª)** | 10 | **3** | **1** | 3 | 3 | 4 |

**O critério não passa:** 2 e 3 pares resolvidos, contra os ≥ 6 esperados. Os
controles ficaram iguais, 4 de 4, como esperado.

**Mas o cadastro pesa, e numa direção só: a da segurança.** Com ele, as
emergências perdidas caem de 3–4 para 1, e os INCERTO de 7–8 para 3–4. Os casos
em que o cadastro virou a decisão para o lado certo:

| Caso | Sem cadastro | Com cadastro |
|---|---|---|
| p2b — antipulgas de cão num **cão** de 30 kg | EMERGENCIA | **NAO_EMERGENCIA** |
| p4a — **filhote** de 0,8 kg sem comer | INCERTO | **EMERGENCIA** |
| p7a — **amamentando** 5 filhotes, tremendo | INCERTO | **EMERGENCIA** |
| p7b — castrada, tremendo | INCERTO | **NAO_EMERGENCIA** |
| p8a — **não castrada**, cio há 5 semanas, bebendo muita água | EMERGENCIA / INCERTO | **EMERGENCIA** (2 de 2) |

**Onde não funcionou**, caso a caso:

- **Para tranquilizar, quase nunca.** p1b (gata fêmea fazendo força na
  caixinha), p3b (cão que mordiscou lírio) e p6b (cão jovem com tosse,
  voltando do hotelzinho) continuaram EMERGENCIA com o cadastro. No p3b a
  justificativa diz que lírios são "altamente tóxicos para gatos e cães": a
  ficha que a busca trouxe é a do lírio **em gatos**, e o Gemini estendeu para
  cães. Errar para o lado da emergência é o erro seguro, e os três rótulos
  "leves" são discutíveis sem um veterinário; ficam como pergunta para a ASAVET.
- **A gata diabética (p5a) ficou INCERTO nas duas repetições**, mesmo com
  "diabética, toma insulina duas vezes por dia" no cadastro. É a falha mais
  séria da rodada.

**Por que a gata diabética falhou: a busca não vê o cadastro.** O app manda à
busca só o texto do tutor (`retrieval_question` = o relato); o cadastro só entra
no prompt da decisão. Para "vomitou uma vez e não quis comer", a busca trouxe
torção gástrica, vômito isolado e vômito persistente — a ficha da cetoacidose
nunca chega, porque "diabética" só existe no cadastro. O mesmo vale para a
hipoglicemia do filhote (p4a; ali o Gemini acertou sem a ficha) e para a
piometra (p8a, idem). Nos 8 casos "A" dos pares, a ficha do quadro grave ficou
fora das 3 em p4a, p5a e p8a: nos três, o texto sozinho aponta para um quadro
comum (falta de apetite, vômito, sede), e o que leva ao quadro grave está só no
cadastro. Nos outros 5, o próprio texto já levava à ficha certa. Em p4a e p8a o
Gemini acertou sem a ficha, com o próprio conhecimento; em p5a, não.

## Leitura

O cenário "o sistema decide com base no relato **e** nas informações do pet"
funciona pela metade:

1. **O cadastro chega à decisão e muda o resultado para o lado seguro** —
   menos emergências perdidas, menos "não sei". Isso o app já entrega.
2. **O cadastro não chega à busca.** A ficha que a IA lê é escolhida só pelo
   texto do tutor; quando o fato decisivo está no cadastro (diabetes,
   gestação, idade de filhote), a ficha certa não vem. **Isso é etapa de
   consulta — trilho B1.**
3. **Faltam campos no cadastro.** Sexo, castração e gestação decidem 3 dos 8
   pares e não existem como campo: aqui foram escritos no histórico livre, o que
   um tutor real pode não fazer.

## Deixado para depois

- **A consulta enriquecida com o cadastro** (proposta, não testada): mandar à
  busca o relato **mais** os fatos clínicos do cadastro (espécie, idade,
  histórico). É barato de medir só na busca, com estes 16 casos. Cuidado
  registrado pelo Vinicius na rodada 20 dele: quando regras e texto de
  orquestração foram para a busca, duas classificações regrediram. A proposta
  é mandar só dados clínicos, não instruções.
- **Campos de sexo, castração e gestação no cadastro** — sugestão ao Vinicius
  (dono do app).
- **Validação dos 16 rótulos pela ASAVET**, em especial p1b, p3b e p6b.

## Próximo passo

Levar ao time os três achados. No trilho B1, se o Ryu aprovar, medir a consulta
enriquecida com o cadastro.
