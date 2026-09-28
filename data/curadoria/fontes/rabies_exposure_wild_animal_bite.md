# Mordida por morcego ou animal silvestre — fontes

**Linha do mapa:** `rabies_exposure_wild_animal_bite`

**Caso da régua:** `b62`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R95 · Rabies in Cats—An Emerging Public Health Issue · Viruses · 2024. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`e515445a1d0443303d48ab600bb91feb4af1d92a98cece540dafd12424c9966d`.

A inspeção individual do recorte produziu **43 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Fonte felina e internacional, embora inclua autores do Ministério da Saúde; não cobre integralmente cães nem substitui protocolo local.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador A) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `rabies_exposure_wild_animal_bite` · cão e gato · `ate_24h`
**Pesquisado em:** 25/09/2026 (agente A, rodada N6)
**Escopo:** uma frase `geral` da ficha de busca (alarme#2).

#### Régua de aptidão

##### 1. MSD Veterinary Manual (versão para tutor), *Rabies in Dogs*: `rabies_exposure_wild_animal_bite__msd_rabies_dogs.txt`

| Critério | Resultado |
|---|---|
| URL | https://www.msdvetmanual.com/dog-owners/brain-spinal-cord-and-nerve-disorders-of-dogs/rabies-in-dogs |
| Idioma / registro | en · tutor |
| Autoridade | alta (manual veterinário). Autor: Charles E. Rupprecht |
| Espécie | cão. A página *Rabies in Cats* do mesmo manual tem o mesmo trecho sobre baba e deglutição, mas não foi capturada (limite de 2 fontes) |
| Cobre os sinais | sim: "often with excess salivation and inability to swallow" |
| Responde a exposição | sim: "an animal bitten or otherwise exposed by a wild, carnivorous mammal or a bat" |
| Diz quando ir | parcial: "it should be revaccinated immediately and closely observed for 45 days". O texto é voltado à conduta sanitária (EUA) |
| Estrutura | 1043 palavras. Seções: Signs and Diagnosis, Control of Rabies, Management of Suspected Rabies Cases, Risk of Passing Rabies to People. Tem condutas dos EUA (NASPHV, eutanásia de cão não vacinado exposto) que talvez não se apliquem ao Brasil |
| Data | revisão completa em 2018, atualizado em setembro de 2024 |
| Direitos | Copyright © 2026 Merck & Co., Inc. All rights reserved. |
| Acesso | abriu em 25/09/2026 |

##### 2. CRMV-SP, *Dia Mundial contra a Raiva: morcegos são os principais transmissores no Brasil*: `rabies_exposure_wild_animal_bite__crmvsp_2025_morcegos.txt`

| Critério | Resultado |
|---|---|
| URL | https://crmvsp.gov.br/dia-mundial-contra-a-raiva-morcegos-sao-os-principais-transmissores-no-brasil/ |
| Idioma / registro | pt · clínico. A notícia mistura público geral e veterinário; o trecho dos sinais está na seção "Médicos-veterinários em ação". Capturada primeiro como `tutor` e recapturada com `--forcar` para `clinico` (mesmo texto) |
| Autoridade | alta (conselho profissional) |
| Espécie | cão e gato |
| Cobre os sinais | parcial: "sinais neurológicos, como paralisia, incoordenação motora, apatia, sialorreia ou comportamento agressivo". Fala em baba, não em dificuldade de engolir |
| Diz quando ir | não para o animal. Para pessoas: "é sempre necessário buscar atendimento médico" |
| Estrutura | 1199 palavras. Seções: Profilaxia pré-exposição e pós-exposição, Médicos-veterinários em ação, Auxilie no monitoramento da doença!, Proteção dos profissionais… Muito conteúdo de vigilância e de profilaxia humana |
| Data | 26/09/2025 |
| Direitos | "Todos os direitos reservados ao Conselho Regional de Medicina Veterinária do Estado de São Paulo" |
| Acesso | abriu em 25/09/2026 |

#### Frases

| Frase | Status | Trecho |
|---|---|---|
| alarme#2: Babando muito ou com dificuldade de engolir | sustentada | MSD: "The paralytic form of rabies (or "dumb rabies") usually involves paralysis of the throat and jaw muscles, often with excess salivation and inability to swallow." |

#### Recomendação

- **Primária EN:** MSD *Rabies in Dogs*, que cobre as duas partes da frase. Ressalva: as condutas são dos EUA.
- **Alternativa PT:** CRMV-SP, que dá o contexto brasileiro (morcegos) e a baba. Ressalva: registro clínico e sem orientação ao tutor sobre o animal.

#### Não encontrado

- O Ministério da Saúde, *Raiva animal* (gov.br, CC BY-ND 3.0), não descreve os sinais clínicos em cães e gatos.
- Fonte em português para tutor que descreva a dificuldade de engolir.
