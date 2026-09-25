# Otite externa leve — fontes

**Linha do mapa:** `otitis_externa_mild`

**Caso da régua:** `b57`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R90 · Pseudomonas spp. in Canine Otitis Externa · Microorganisms · 2023. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`505fa677581af534b69dfa550ba1922414fff06d0d52cf34f9617c3567f7949f`.

A inspeção individual do recorte produziu **107 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Cobre cães e casos inclusive crônicos; não prova que um caso específico seja leve nem cobre gatos.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador D) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `otitis_externa_mild` · cão e gato · rotina (linha leve)
**Pesquisado em:** 25/09/2026 (agente D, rodada N6)
**Frase procurada:** `sinais_de_alarme#1` (cabeça torta ou olhos mexendo sozinhos)

Linha leve: segui o roteiro e busquei a **página de sintoma** ("ear problems"), não a de uma doença. A página de sintoma diz o que é o problema comum do ouvido externo e, na mesma página, o que muda quando o problema atinge o ouvido médio ou interno.

#### Candidata 1: PDSA, "Ear problems in dogs"

`otitis_externa_mild__pdsa_ear_problems_dogs.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (entidade veterinária beneficente do Reino Unido; "Written by vets and vet nurses") |
| Espécie | cão |
| Cobre os sinais (leves) | sim: "Ear problems tend to cause swelling, redness, pain, a bad smell, itchiness, and head shaking." |
| Responde o discriminador (externo × ouvido médio ou interno) | sim: "cause symptoms such as loss of balance, a head tilt, and flickering eye movements" |
| Diz quando ir | sim, de forma genérica: "Always contact your vet if you think your dog might have an ear problem." Não diz quando dá para esperar |
| Estrutura | 531 palavras. Headings: Overview · Common ear problems in dogs · Symptoms of an ear problem · Dog breeds prone to ear disease (a lista de raças não saiu na captura). O rodapé ("Did you find this page useful?…") saiu no arquivo e deve ficar de fora |
| Data | "Published: Oct 2021" |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© The People's Dispensary for Sick Animals" (sem licença de reuso declarada) |

**Recomendação:** primária.

#### Candidata 2: PDSA, "Ear problems in cats"

`otitis_externa_mild__pdsa_ear_problems_cats.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (PDSA) |
| Espécie | gato |
| Cobre os sinais | sim: "If your cat has a more serious problem affecting their middle or inner ear", seguido da lista "A head tilt", "Loss of balance", "Flickering eye movements" |
| Diz quando ir | só na reação alérgica grave: "If you think this is the case, call your vet immediately." |
| Estrutura | 346 palavras. Headings: Symptoms of ear problems in cats · Common ear problems in cats. Mesmo rodapé da de cão |
| Data | "Published: January 2023" |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© The People's Dispensary for Sick Animals" |

**Recomendação:** alternativa para gato, e ela completa a espécie da linha.

#### Descartadas ou não capturadas

- **MSD, "Otitis Externa in Cats"** (tutor): não fala de cabeça torta nem de olhos.
- **VCA, "Ear Infections in Dogs" e "Ear infections in cats"**: não achei cabeça torta nem movimento dos olhos no corpo do texto.
- **MSD, "Otitis Media and Interna"** (tutor): cobre os sinais, mas é página da doença vestibular, não da linha leve.

#### Não encontrado

- Fonte em português.
- As duas páginas da PDSA dizem que os sinais vêm do ouvido médio ou interno, sem usar a palavra "otite". A ligação com a otite externa que se espalha é leitura minha.
