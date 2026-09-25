# Ofegação após exercício — fontes

**Linha do mapa:** `exertional_panting_mild`

**Caso da régua:** `b61`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R94 · Working Dogs Drinking a Nutrient-Enriched Water Maintain Cooler Body Temperature and Improved Pulse Rate Recovery After Exercise · Frontiers in Veterinary Science · 2018. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`3a7083eed08fa55ec967a2c6432ae1a78623e83474b5a935164f571e2bf80027`.

A inspeção individual do recorte produziu **87 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Estudo com cães de trabalho condicionados; não define sozinho a fronteira com intermação.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador C) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `exertional_panting_mild` (cão; rotina)
**Pesquisado em:** 25/09/2026 · **Frases do grupo C:** tutor#5, diferenciar#1

#### Régua de aptidão

##### Tufts HeartSmart — *Difficulty Breathing (Dyspnea)*
`exertional_panting_mild__tufts_dispneia.txt` (a mesma página de `congestive_heart_failure` e `respiratory_distress`)

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (Tufts University, cardiologia) |
| Espécie | cão e gato |
| Cobre os sinais | sim — "normal panting (quick, shallow, open-mouth breathing after exercise or when they are hot)" |
| Responde o discriminador | **sim, quase palavra por palavra** — "differentiate a dog’s normal panting … from an increased breathing rate due to heart failure" |
| Diz quando ir | sim, e com o critério da linha leve — "difficulty breathing that does not resolve with rest is almost always a veterinary emergency" |
| Estrutura | 689 palavras, quase sem headings |
| Data | não declarada |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© Tufts University 2026"; sem licença declarada |

##### PDSA — *Vet Q&A: Is my dog is panting too much?*
`exertional_panting_mild__pdsa_ofegacao.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (entidade veterinária beneficente; blog assinado pelos veterinários da PDSA, sem nome) |
| Espécie | cão |
| Cobre os sinais | sim — "more likely to see your dog pant after exercise or on a warm day" |
| Responde o discriminador | em parte — doença cardíaca faz ofegar e "Often, your dog will also show other symptoms of their illness, for example coughing" |
| Diz quando ir | sim, nos dois sentidos — pode esperar: "Stop exercise" / água / tempo para esfriar; vai já: "give first aid and contact your vet immediately" |
| Estrutura | 856 palavras; 6 headings (When might I see my dog pant?, Stress and anxiety, Illness or pain, What should I do if my dog is panting?, How can I tell if my dog is panting too much?, Heatstroke). Boa para a linha leve |
| Data | 23/06/2021 |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© The People's Dispensary for Sick Animals. Registered charity nos. 208217 & SC037585"; sem licença declarada |

#### Frases

| Frase | Status | Fonte | Trecho (literal) |
|---|---|---|---|
| tutor#5 "Tá ofegante, mas esperto, anda normal e atende quando chamo" | **parcial** | PDSA | "Panting is usually a response to something, so you are more likely to see your dog pant after exercise or on a warm day." |
| diferenciar#1 | sustentada (com ressalva) | Tufts | "differentiate a dog’s normal panting (quick, shallow, open-mouth breathing after exercise or when they are hot) from an increased breathing rate due to heart failure (noted as fast breathing or extra breathing effort present even at rest)." |

**tutor#5:** a fonte não diz em positivo "esperto, anda normal, atende". Diz o contrário, como alarme: "Not wanting to move/low energy" (contatar imediatamente); na intermação, "Weakness and collapse" e "Confusion". A frase do tutor é a negação desses alarmes: é leitura por exclusão, não afirmação da fonte.

**diferenciar#1, por partes:**
- Acelerada em repouso × ofegação normal após exercício/calor: sustentado (trecho).
- "ou dormindo": implícito. A Tufts manda contar "at rest or sleeping" e dá o normal abaixo de 35/min "at rest or during sleep".
- "pode vir com tosse": sustentado — legenda da Tufts "Dogs with heart failure often have difficulty breathing combined with cough" e a PDSA (acima).
- "**só** aparece depois de exercício ou calor": mais restrito que as fontes. A PDSA dá outras causas não patológicas (estresse e ansiedade; raças de focinho curto; excesso de peso).

#### Recomendação

- **Primária:** Tufts, para o discriminador (autoridade alta, cobre a frase).
- **Primária para o lado leve:** PDSA — é a que diz quando pode esperar e o que muda isso, que é o critério da linha leve.

#### Não encontrado

- Fonte de autoridade que descreva em positivo o cão ofegante "alerta, andando normal, respondendo" como sinal de que pode esperar.
- Fora a PDSA, a busca pela queixa só trouxe clínicas e lojas.
