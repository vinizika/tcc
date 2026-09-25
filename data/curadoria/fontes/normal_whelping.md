# Parto normal — fontes

**Linha do mapa:** `normal_whelping`

**Caso da régua:** `b53`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R86 · Uterine dynamics, blood profiles, and electronic fetal monitoring of bitches · Frontiers in Veterinary Science · 2023. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`44e411b0062c4bb185f970d722152d6c0156e3d03efdadac387bead5752e8745`.

A inspeção individual do recorte produziu **235 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Cobre apenas cadelas e um contexto de monitoramento clínico; não cobre gatas.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador D) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `normal_whelping` · cão e gato · rotina (linha leve)
**Pesquisado em:** 25/09/2026 (agente D, rodada N6)
**Frase procurada:** `como_o_tutor_conta#2` (cavando e arrumando um cantinho, fazendo ninho)

#### Candidata 1: Cornell Riney Canine Health Center, "The normal whelping process"

`normal_whelping__cornell_normal_whelping.txt` (já constava de `referencias.md`, em R11)

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (Cornell University College of Veterinary Medicine) |
| Espécie | cão |
| Cobre os sinais | sim: "extreme nesting behavior (fervently shredding bedding material, frantic nesting, etc.)". "Cavando" não aparece |
| Responde o discriminador (normal × distocia) | sim: "Up to two hours between puppies is considered normal." |
| Diz quando ir | sim: "Contact your veterinarian if more than two hours have passed between the delivery of puppies." |
| Estrutura | 864 palavras, com headings em forma de pergunta (How long is pregnancy in dogs? · What are the expected stages of labor? · How will I know when my dog is going into labor? · How long should it take between birthing puppies? · …); boa para curar |
| Data | não informada ("Cornell University ©2026") |
| Acesso | abriu em 25/09/2026 |
| Direitos | "Cornell University ©2026" (sem licença de reuso declarada) |

**Recomendação:** primária.

#### Candidata 2: MSD Veterinary Manual, "Management of Reproduction of Cats" (tutor)

`normal_whelping__msd_owner_cat_reproduction.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta |
| Espécie | gato |
| Cobre os sinais | sim: "hiding, becoming restless, and building a nest for the kittens" |
| Diz quando ir | parcial: define distocia como "more than 1 to 4 hours between delivery of kittens during stage II" |
| Estrutura | 1487 palavras e só dois headings (Pregnancy and Delivery · Problems Associated with Delivery). O começo (cruza, controle de natalidade) fica sem heading e não interessa à linha |
| Data | Full review ago/2018, Autumn P. Davidson, DVM, MS, DACVIM |
| Acesso | abriu em 25/09/2026 |
| Direitos | "Copyright © 2026 Merck & Co., Inc. … All rights reserved." |

**Recomendação:** alternativa para gata, e ela completa a espécie da linha.

**Divergência para o especialista:** para gatas, o MSD põe o limite da distocia entre **1 e 4 horas** entre filhotes. A regra do mapa (2 horas) vem de cadela. Não escolhi lado.

#### Descartadas ou não capturadas

- **MSD, "Management of Reproduction in Dogs"** (tutor): "becoming restless, nesting, hiding", sem cavar. Alternativa.
- **iCatCare, "Pregnancy and kittening"**: a página abriu, mas não achei "nest" no texto extraído.
- **PDSA, gestação de cão e de gata**: as URLs tentadas deram 404.

#### Não encontrado

- A palavra **"cavando"**. As fontes descrevem ninho e mexer na cama ("shredding bedding"), não cavar.
- Fonte em português. O orçamento de buscas na web acabou antes de uma busca PT para este tópico.
