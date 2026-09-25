# Carrapatos no animal, sem sinais — fontes

**Linha do mapa:** `ticks_found_no_signs`

**Caso da régua:** `b63`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R96 · Clinical Study and Serological Diagnosis of Vector-Borne Pathogens in Sardinian Dogs · Veterinary Sciences · 2024. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`be7edb3b425fe78f78d8d42e711c11d4a605ba164bb4ad288d3edb54780263af`.

A inspeção individual do recorte produziu **182 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Estudo italiano; assintomáticos podem ter exposição, portanto a fonte não autoriza tratar o achado como inofensivo.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador D) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `ticks_found_no_signs` · cão e gato · rotina (linha leve)
**Pesquisado em:** 25/09/2026 (agente D, rodada N6)
**Frases procuradas:** `como_o_tutor_conta#4` (orelha, pescoço e entre os dedos) e `como_o_tutor_conta#5` (bolinha cinza, carrapato cheio)

#### Candidata 1: TroCCAP, diretrizes de ectoparasitos de cães e gatos nos trópicos (PT)

`ticks_found_no_signs__troccap_2022_ectoparasitos.pdf`

| Critério | Avaliação |
|---|---|
| Idioma | pt (tradução oficial) |
| Registro | clínico |
| Autoridade | alta (TroCCAP). Cita espécies do Brasil (*R. sanguineus* s.l., *Amblyomma sculptum*, *A. aureolatum*) |
| Espécie | cão e gato |
| Cobre os sinais | parcial: "orelhas, axilas, região inguinal, áreas perioculares e interdigitais" (seção "Carrapatos (Ixodida)", Diagnóstico, página 7 do PDF). Pescoço não aparece |
| Diz quando pode esperar (linha leve) | indireto: "A infestação por um único ou poucos carrapatos (especialmente por pequenas larvas) pode passar despercebida"; "Todos os carrapatos visíveis devem ser imediatamente removidos do animal infestado". Não diz quando procurar o veterinário |
| Estrutura | **PDF de 47 páginas, cerca de 12 mil palavras**, sobre todos os ectoparasitos (pulgas, piolhos, ácaros, flebótomos…). Só as páginas 6 a 8 (carrapatos) interessam, e a ingestão precisa de `exclude_pages` |
| Data | 1ª edição, agosto de 2022 |
| Acesso | abriu em 25/09/2026 |
| Direitos | o PDF não declara licença; o site diz "Copyright © 2026 Troccap - All rights reserved" |

**Recomendação:** primária em PT para `#4`, com a ressalva do pescoço.

#### Candidata 2: PDSA, "Ticks on dogs"

`ticks_found_no_signs__pdsa_ticks_on_dogs.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (PDSA) |
| Espécie | cão. A página de gato ("Ticks on cats") tem o mesmo texto, e não a capturei |
| Cobre os sinais | sim: "grow to the size of a small pea as it feeds"; "Brown, pink, purple or a bluish grey"; locais: "head, ears, armpits, groin and tummy" |
| Diz quando pode esperar (linha leve) | **sim, é o critério da linha leve**: "There is no need to contact your vet if you have successfully removed a tick" e, no mesmo trecho, "contact your vet for advice if your dog seems unwell after having a tick" |
| Estrutura | 716 palavras. Headings: Overview · Tick prevention for dogs · When to contact your vet · Lyme disease · Can humans get ticks?. O heading "What does a tick look like on a dog?" não saiu na captura, e a lista da aparência ficou sob Overview. Rodapé de avaliação no fim do arquivo |
| Data | "Published: July 2022" |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© The People's Dispensary for Sick Animals" |

**Recomendação:** primária em inglês para `#5`. A página é do Reino Unido ("This advice is for UK pets only") e fala da doença de Lyme, não da erliquiose e da babesiose. **O especialista precisa saber disto**: a parte de doenças não vale para o Brasil, mas a descrição do carrapato vale.

#### Descartadas ou não capturadas

- **MSD, "Ticks of Dogs"** (tutor): cita "head, neck, shoulders, and pubic area" e diz que o carrapato cheio fica "much more rounded", sem a cor. É alternativa que cobriria o pescoço; não a capturei por causa do limite de duas fontes.
- **CAPC petsandparasites.org, "Ticks"** (tutor): não achei os locais onde o carrapato gruda.

#### Não encontrado

- Uma fonte que cite **orelha, pescoço e dedos juntos**. O TroCCAP e a PDSA não citam pescoço; o MSD cita, mas não cita os dedos.
- Uma fonte PT **para tutor** com autoridade.
