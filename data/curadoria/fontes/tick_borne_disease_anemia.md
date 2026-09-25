# Doença do carrapato com anemia — fontes

**Linha do mapa:** `tick_borne_disease_anemia`

**Caso da régua:** `b46`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R79 · Costa Rican Genotype of Ehrlichia canis: A Current Concern · Veterinary Sciences · 2023. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`8e11958bbfef428d172bfb74222ad2dcc44791dc3feed126ec57088e78046ef9`.

A inspeção individual do recorte produziu **80 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Estudo brasileiro de Ehrlichia canis; não cobre babesiose nem todo quadro de anemia.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador D) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `tick_borne_disease_anemia` · cão · imediato
**Pesquisado em:** 25/09/2026 (agente D, rodada N6)
**Frases procuradas:** `como_o_tutor_conta#8` (xixi escuro, cor de café) e `sinais_de_alarme#3` (manchinhas roxas ou pontinhos vermelhos na barriga)

#### Candidata 1: TroCCAP, diretrizes de endoparasitos caninos nos trópicos (PT)

`tick_borne_disease_anemia__troccap_2019_endoparasitos.pdf`

| Critério | Avaliação |
|---|---|
| Idioma | pt (tradução oficial do TroCCAP) |
| Registro | clínico (diretriz para veterinários) |
| Autoridade | alta (conselho científico internacional sobre parasitos de animais de companhia nos trópicos; o Brasil está no escopo, e o texto cita *B. vogeli* e *R. sanguineus*) |
| Espécie | cão |
| Cobre os sinais | sim, na seção "Babésia (Babesia spp.)", página 52 do PDF: "petéquias e equimoses, urina vermelha, marrom ou amarelo-laranja (hemoglobinúria)" |
| Relação com a erliquiose | o texto registra: "É possível que tais casos tenham erliquiose concomitante" |
| Diz quando ir | não (texto clínico) |
| Estrutura | **PDF de 71 páginas, cerca de 18,8 mil palavras**, sobre todos os endoparasitos caninos. Só as páginas 52 a 54 (Babesia) interessam; a ingestão precisa de `exclude_pages` extenso, e sem isso o PDF inunda a busca |
| Data | 2ª edição, 17/03/2019 (arquivo publicado em fev/2022) |
| Acesso | abriu em 25/09/2026 |
| Direitos | o PDF não declara licença (diz só "disponíveis gratuitamente"); o site diz "Copyright © 2026 Troccap - All rights reserved" |

**Recomendação:** primária em PT para as duas frases, porque é a única fonte com autoridade que tem as duas. Foi capturada como PDF por falta de uma página HTML equivalente.

#### Candidata 2: MSD Veterinary Manual, "Ehrlichiosis and Related Infections in Dogs" (tutor)

`tick_borne_disease_anemia__msd_owner_ehrlichiosis.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta |
| Espécie | cão |
| Cobre os sinais | sim, do lado da erliquiose: "increased tendency to bruise (seen most often on the skin or gums)"; também sangramento pelo nariz e "blood in urine or feces" |
| Diz quando ir | não (só "Use veterinarian-recommended products to prevent ticks.") |
| Estrutura | 709 palavras, com listas de sinais por fase. As subdivisões são frases soltas, não headings, e o ingestor pode não enxergá-las como seção |
| Data | Full review jun/2026, Nick Roman, DVM, MPH |
| Acesso | abriu em 25/09/2026 |
| Direitos | "Copyright © 2026 Merck & Co., Inc. … All rights reserved." |

**Recomendação:** alternativa em inglês para tutor, do lado da erliquiose. Complementa o TroCCAP, que só trata da babesiose.

#### Descartadas ou não capturadas

- **VCA, "Babesiosis in Dogs"**: "Abnormal dark urine". É a melhor alternativa para tutor na frase do xixi. Não capturei para respeitar o limite de duas fontes.
- **CAPC, "Ehrlichia spp. and Anaplasma spp."**: "petechial to ecchymotic hemorrhages". Clínica, alternativa.
- **MSD, "Blood Parasites of Dogs"** (tutor): na babesiose, só "red urine".
- **VCA, "Ehrlichiosis in Dogs"**: "bleeding disorders", sem petéquias nem mancha na pele.
- **CRMV-SP**: as páginas sobre carrapato são reprodução de jornal (Folha, 2009; Rede Bom Dia, 2011) e só dizem "manchas hemorrágicas na pele". Descartadas.
- **Material brasileiro "doença do carrapato" para tutor**: tudo o que a busca trouxe é pet shop, clínica comercial ou blog.
- **Busca do SciELO**: devolveu 403 ao cliente do projeto; não tentei contornar.

#### Não encontrado

- A localização **"na barriga"**: nenhuma fonte diz onde aparecem as petéquias e equimoses. O MSD diz "skin or gums".
- A expressão "cor de café". O TroCCAP diz "marrom".
- Uma fonte PT **para tutor** com autoridade.
