# Intoxicação por medicamento humano — fontes

**Linha do mapa:** `human_medication_poisoning` · cão e gato · emergência · imediato

**Caso da régua:** `b19`, escrito antes da pesquisa

**Pesquisado em:** 14/09/2026

**Estado:** `fonte_aprovada` — aprovada pela ASAVET em 14/09/2026; ainda experimental

## Fonte capturada

### ABMVZ — Sensibilidade a anti-inflamatórios (PT, acadêmico)

Riboldi E, Lima DA, Dallegrave E · 2012 · DOI
`10.1590/S0102-09352012000100006` · CC BY-NC 4.0.

| Critério | Resultado | Evidência literal |
|---|---|---|
| Espécie | cão e gato | “animais de companhia” — *RESUMO* |
| Medicamentos | sim | “cetoprofeno, o ibuprofeno e o diclofenaco” — *RESUMO* |
| Risco | sim | “leva, na maioria das vezes, cães e gatos ao óbito” — *RESUMO* |
| Sinais do caso b19 | não | o resumo não descreve vômito ou edema facial |
| Urgência explícita | parcial | recomenda assistência e prevenção, sem janela temporal |

O HTML repetiu o resumo e produziu 13 chunks; essa variante foi descartada.
O PDF original produziu 7 chunks, todos da seção `RESUMO`, entre 61 e 88
tokens. Tratamento e doses não entram. A captura foi aprovada pela ASAVET e
permanece `experimental_only` até uma nova rodada passar pela régua.

## Fontes abertas, mas não armazenadas

- VCA, *Acetaminophen Toxicity in Cats*: clinicamente específica, mas os
  termos proíbem cópia e redistribuição sem autorização escrita.
- University of Illinois, *Keep Your Medications Away from Pets*: fonte
  institucional, mas sem licença de redistribuição identificada.
- Cornell, *Small Animal Toxins*: fonte universitária, sem licença clara para
  guardar o texto integral.
- Centro Paula Souza, revisão sobre paracetamol (2024): o repositório informa
  “all rights reserved”.

## Limitação preservada após a aprovação

A fonte capturada sustenta o risco de AINEs, mas não cobre paracetamol nem os
sinais específicos do `b19`. A ASAVET aprovou a fonte em 14/09/2026, conforme
informado pelo responsável do projeto; a limitação continua registrada e a
fonte não passou a ser tratada como cobertura completa.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador B) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

Agente B, rodada N6, acesso em 25/09/2026. Uma frase do tutor. Casos de
régua: fora do escopo desta tarefa.

#### Candidatas capturadas

##### 1. Pet Poison Helpline — *Preventing Accidental Medication Exposures*
`human_medication_poisoning__pph_prevent_exposures.txt` ·
https://www.petpoisonhelpline.com/uncategorized/preventing-accidental-medication-exposures/

| Critério | Resultado |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | média (centro de controle de intoxicação animal, serviço privado; autora Pamela Huyck, técnica veterinária certificada) |
| Espécie | cão e gato; a frase que sustenta o item é sobre cães |
| Cobre os sinais | sim, o jeito como acontece: "grabbing pills that drop on the floor or chewing medication bottles" |
| Diz quando ir | não. É um texto de prevenção; o mais perto é "can cause life-threatening problems, even if only one pill is ingested" |
| Estrutura | 863 palavras; sem headings (só o byline) e uma lista de 11 dicas de prevenção. Indexação tudo ou nada, quase toda de prevenção |
| Data | publicada em 22/05/2014, modificada em 27/05/2026 |
| Direitos | ©2026 Pet Poison Helpline® |
| Acesso | abriu, 25/09/2026 |

##### 2. FDA — *Properly Store Medications to Keep Your Pet Safe*
`human_medication_poisoning__fda_store_meds.txt` ·
https://www.fda.gov/animal-veterinary/animal-health-literacy/properly-store-medications-keep-your-pet-safe

| Critério | Resultado |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (agência reguladora dos EUA, Center for Veterinary Medicine) |
| Espécie | cão e gato |
| Cobre os sinais | sim, a cartela: "chew through a variety of medication containers, including … blister packages" |
| Diz quando ir | sim: "call your veterinarian or an animal poison control center" (What To Do if Your Pet Gets Into a Medication) |
| Estrutura | 1217 palavras; quase tudo é como guardar e descartar remédio (Take It Back, Flush It, Trash It). Só uma parte curta é sobre a ingestão |
| Data | "Content current as of 06/14/2024" |
| Direitos | a página não declara; obra do governo federal dos EUA, em geral domínio público |
| Acesso | abriu, 25/09/2026 |

#### Frase por frase

| Frase | Status | Trecho (literal) |
|---|---|---|
| tutor#7 Comeu comprimido que caiu no chão ou mastigou a cartela | sustentada (as duas fontes juntas) | PPH: "Dogs are especially prone to grabbing pills that drop on the floor or chewing medication bottles and eating some or all of the pills in them." FDA: "Pets are known to chew through a variety of medication containers, including plastic pill vials, boxes, and blister packages." |

Nenhuma das duas fontes sozinha cobre a frase inteira. A Pet Poison Helpline
tem o comprimido caído no chão, mas fala de frasco e não de cartela. A FDA
tem a cartela; no chão, ela só tem "knock a tube of medication off a counter
… onto the floor".

#### Recomendação

- **FDA: primária** pela autoridade e por dizer quando ir.
- **Pet Poison Helpline: alternativa.** É a única com o comprimido que caiu
  no chão, mas é autoridade média e não diz quando ir.
- **Descartadas** (abertas, não capturadas): CRMV-AL (2016, "os medicamentos
  ficam expostos ou em locais de fácil acesso e o animal come
  acidentalmente", sem chão nem cartela); CRMV-PB (2023, só "ingestão
  acidental"); Merck Vet Manual para tutores, *Poisonings from Human
  Prescription Drugs* ("countertops, pill minders, mail-order packages", sem
  chão nem cartela); Illinois Vet Med (conselho de catar o comprimido do
  chão, não o evento); VCA *Acetaminophen* e *Safe Handling* (só prevenção).
- **Não abertas:** dvm360 (403 no WebFetch; não contornei). A frase em
  português com chão e cartela só apareceu em blog de empresa (recusado).

#### Não encontrado

- **Fonte em português com autoridade que fale de comprimido caído no chão ou
  de cartela mastigada**: os CRMVs dizem só "ingestão acidental" ou "locais de
  fácil acesso".
