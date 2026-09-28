# Abscesso após briga de gato — fontes

**Linha do mapa:** `cat_bite_abscess` · gato · atendimento em até 24 horas

**Caso da régua:** `b31`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 19/09/2026; ressalvas mantidas

## Fonte experimental

Tamura et al. · Frontiers in Veterinary Science · 2025 · DOI
`10.3389/fvets.2025.1654990` · CC BY 4.0. SHA-256
`996c364f63c5f28ab8e5cd7edb5ea30c3768a26583be4604e26f3fe2f8b4a4af`.

A inspeção produziu 44 chunks de 40–95 tokens. O PDF aborda abscesso felino,
mas o caso é intra-abdominal e não confirma a origem por mordida.

## Limitações

Este é o candidato mais fraco do lote. Não deve ser confundido com evidência
específica para ferida de briga nem usado para validar o prazo de seis horas.
Requer substituição ou aceite explícito com ressalva pelos especialistas.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador A) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `cat_bite_abscess` · gato · `ate_24h`
**Pesquisado em:** 25/09/2026 (agente A, rodada N6)
**Escopo:** curadoria das frases `geral` da ficha de busca. Não é a pesquisa completa da linha: não houve casos de régua nem `--inspect`.

#### Régua de aptidão

##### 1. iCatCare, *Cat bites and abscesses*: `cat_bite_abscess__icatcare.txt`

| Critério | Resultado |
|---|---|
| URL | https://icatcare.org/articles/cat-bites-and-abscesses |
| Idioma | en (corpo) |
| Registro | tutor |
| Autoridade | alta (entidade felina, International Cat Care) |
| Espécie | gato. Sim |
| Cobre os sinais | sim: "Commonly affected areas are the tail, face, head, neck and legs."; "If it bursts, you will see pus and may notice a bad smell" |
| Diz quando ir | parcial: "If you see what you think is a bite wound on your cat, … contact your veterinary team." Não dá prazo |
| Estrutura | 465 palavras. Os títulos de seção se perderam na extração e o texto ficou corrido, o que conta contra: vai tudo ou nada |
| Data | publicado em 21/03/2025, atualizado em 26/09/2025 |
| Direitos | © 2026 International Cat Care; licença de reuso não declarada |
| Acesso | abriu em 25/09/2026 |

##### 2. VCA, *Fight Wound Infections in Cats*: `cat_bite_abscess__vca_fight_wound.txt`

| Critério | Resultado |
|---|---|
| URL | https://vcahospitals.com/know-your-pet/wounds-fight-wound-infections-in-cats |
| Idioma | en |
| Registro | tutor |
| Autoridade | média (rede de hospitais; texto LifeLearn assinado por veterinários) |
| Espécie | gato. Sim |
| Cobre os sinais | sim: "Puncture wounds can close over quickly and can easily be missed"; "your cat may limp" |
| Diz quando ir | sim: "If you know your cat has been in a fight, notify your veterinarian immediately." |
| Estrutura | 1184 palavras, com seções em forma de pergunta (What should I do if my cat is bitten?, How are fight wounds treated?…). Tem medicamentos com nome comercial em "How are fight wounds treated?", uma seção a excluir |
| Data | atualizado em 15/05/2026 |
| Direitos | © 2026 LifeLearn Inc.; proíbe cópia e redistribuição sem consentimento, e proíbe o uso de IA para reescrever ou republicar o conteúdo. **O especialista precisa saber disso antes de indexar** |
| Acesso | abriu em 25/09/2026 |

#### Frases

| Frase | Status | Fonte | Trecho |
|---|---|---|---|
| tutor#2: Achei um furinho na pele, escondido no pelo, parece mordida | sustentada | VCA | "particularly if the wounds are in areas with a lot of fur. Puncture wounds can close over quickly and can easily be missed…" |
| tutor#3: Uns dias depois da briga apareceu um caroço mole, inchado | parcial | iCatCare | "An abscess (a swelling filled with pus) can take 2-3 days to develop." Nenhuma fonte diz "mole" |
| tutor#4: Inchou perto do rabo, numa pata ou na cara | sustentada | iCatCare | "Commonly affected areas are the tail, face, head, neck and legs." |
| tutor#5: O caroço estourou e saiu pus com cheiro ruim | sustentada | iCatCare | "If it bursts, you will see pus and may notice a bad smell" |
| tutor#6: Tá mancando da pata que foi mordida | sustentada | iCatCare | "Limping, if bitten on one of the legs" |
| tutor#7: Não deixa encostar no lugar, reclama de dor | sustentada | iCatCare | "Abscesses are usually very painful, so your cat may be reluctant to be touched." |
| alarme#1: Sangra muito ou a ferida é funda | não encontrada | — | Ver abaixo |

#### Recomendação

- **Primária:** iCatCare. Autoridade alta, escrita para tutor, cobre cinco das sete frases. Diz "procure o veterinário", mas não diz em quanto tempo.
- **Alternativa:** VCA. É a única que cobre o furo escondido no pelo e a que diz "imediatamente". O aviso de direitos da LifeLearn é mais restritivo que o das outras fontes.
- **Descartadas:** VCA *Abscesses in Cats*, que não traz o furo escondido, os locais nem o mancar. Veterinary Partner (VIN), que abre verificação anti-robô; não contornei.

#### Não encontrado

- **"Sangra muito ou a ferida é funda"** não aparece como alarme em nenhuma das duas fontes. A VCA chama toda mordida de gato de "small, deep wounds", o que sugere que "funda" não separa os casos graves. A PDSA *Wounds and skin injuries*, capturada para `minor_wound` (`minor_wound__pdsa_wounds.txt`), põe na lista de emergência "Bleeding wounds (heavy or haven’t stopped after 10 minutes)" e "Deep wounds". Para contar aqui, a página precisaria ser capturada também para este tópico.
- Nenhuma fonte em português com autoridade: a busca devolveu só pet shop e blog (Cobasi, zooplus).
- O prazo de 6 horas do mapa ("feridas tratadas em até 6 horas…") não apareceu em nenhuma das fontes lidas.
