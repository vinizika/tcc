# Ferida superficial pequena — fontes

**Linha do mapa:** `minor_wound`

**Caso da régua:** `b58`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R91 · Integrative Therapies in Wound Healing in Small Animals · Veterinary Sciences · 2026. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`2ca34aed1338400c47dceff0e6482042823b2d6a37c1e9c3716e20aafb1e03f0`.

A inspeção individual do recorte produziu **76 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

O recorte cobre classificação e manejo inicial; não define o prazo do mapa e exclui terapias integrativas.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador A) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `minor_wound` · cão e gato · `ate_24h`
**Pesquisado em:** 25/09/2026 (agente A, rodada N6)
**Escopo:** curadoria das frases `geral` da ficha de busca. Não é a pesquisa completa da linha.

Esta é uma linha leve. Seguindo o roteiro, o critério "diz quando ir" foi lido ao contrário: interessa a fonte dizer **quando pode esperar**.

#### Régua de aptidão

##### 1. PDSA, *Wounds and skin injuries*: `minor_wound__pdsa_wounds.txt`

| Critério | Resultado |
|---|---|
| URL | https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/wounds-and-skin-injuries |
| Idioma / registro | en · tutor |
| Autoridade | alta (entidade beneficente veterinária do Reino Unido, "Written by vets and vet nurses") |
| Espécie | cão e gato (genérico, "pet") |
| Cobre os sinais | parcial: "stop your pet licking, biting or scratching their wounds" |
| Diz quando pode esperar | sim: "Most small cuts are grazes heal in a few days if they are kept clean and dry." (o erro de digitação "are grazes" é do original) |
| Diz quando ir | sim, a lista "When is a wound an emergency?" traz "Bleeding wounds (heavy or haven’t stopped after 10 minutes)" e "Deep wounds" |
| Estrutura | 969 palavras. Seções: Overview, When is a wound an emergency?, Cuts and grazes, Bite wounds, Bruising or crushing, Abscesses, Treatment, Cost |
| Data | publicado em agosto de 2020 |
| Direitos | © The People's Dispensary for Sick Animals; licença de reuso não declarada |
| Acesso | abriu em 25/09/2026 |

##### 2. PDSA, *First aid for wounds, cuts and grazes*: `minor_wound__pdsa_first_aid_cuts.txt`

| Critério | Resultado |
|---|---|
| URL | https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/medications/first-aid-for-cuts-and-grazes |
| Idioma / registro | en · tutor |
| Autoridade | alta |
| Espécie | cão e gato (o texto alterna "pet" e "dog") |
| Cobre os sinais | parcial: "Does your pet seem alright in themselves?" |
| Diz quando pode esperar | sim: "If your dog’s wound is minor, you may be able to treat it at home" |
| Estrutura | 578 palavras. Seções: Overview, What to do if your pet has a wound (passos 1 a 4), Home care for a minor wound. O cuidado caseiro fica em seção própria e pode ser excluído |
| Data | publicado em abril de 2020 |
| Direitos | © PDSA; licença de reuso não declarada |
| Acesso | abriu em 25/09/2026 |

#### Frases

| Frase | Status | Fonte | Trecho |
|---|---|---|---|
| tutor#7: Ele fica lambendo o machucado | parcial | PDSA wounds | "It’s very important to stop your pet licking, biting or scratching their wounds - their tongues are rough…" A fonte trata lamber como algo a impedir, não como relato típico |
| tutor#8: Fora isso, tá andando e brincando normal | parcial | PDSA first aid | "Does your pet seem alright in themselves? Do they have any other injuries? Are they in pain or shock?" Checar o estado geral é o primeiro passo, mas a fonte não diz que animal normal pode esperar |

#### Recomendação

- **Primária:** PDSA *First aid for wounds, cuts and grazes*. Diz quando pode esperar ("Minor wounds can often be treated at home.") e no mesmo passo diz o que muda isso (sangra muito, falta pele, objeto na ferida).
- **Alternativa:** PDSA *Wounds and skin injuries*. Melhor no lado grave e cobre também o alarme de `cat_bite_abscess`.
- **Descartadas:** MSD *Wound Management* (tutor), que descreve tratamento e não diz quando pode esperar. VCA Urgent Care *Lacerations and Abrasions*, com ~250 palavras e "An open wound of any size needs to be seen by a veterinarian": o oposto do que a linha leve precisa. AAHA, primeiros socorros: HTTP 403.

#### Não encontrado

- Nenhuma fonte de autoridade alta que diga, com todas as letras, que a ferida pequena **num animal que anda e brinca normalmente** pode esperar. A frase "acting normally" só aparece em clínicas comerciais e blogs, de autoridade baixa, que não foram capturados.
- Em português, só pet shop e indústria (Cobasi, Ourofino, Petz).
