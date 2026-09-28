# Tosse dos canis leve — fontes

**Linha do mapa:** `kennel_cough_mild`

**Caso da régua:** `b55`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R88 · Canine infectious respiratory disease: New insights into the etiology and epidemiology · PLOS ONE · 2019. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`3ba544d14dbf2616933fe711b6716f49afec77c5edc7590aa2de03837ba75c91`.

A inspeção individual do recorte produziu **56 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Descreve o complexo respiratório e gravidade, mas não define sozinho o prazo seguro de espera.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador C) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `kennel_cough_mild` (cão; até 24 h)
**Pesquisado em:** 25/09/2026 · **Frases do grupo C:** tutor#3, tutor#4, diferenciar#1

#### Régua de aptidão

##### MSD Veterinary Manual (Pet Owner) — *Tracheobronchitis (Bronchitis) in Dogs*
`kennel_cough_mild__msd_traqueobronquite.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (manual veterinário; autor Ned F. Kuehn, DVM, DACVIM) |
| Espécie | cão |
| Cobre os sinais | sim — "spasms of harsh, dry coughing, which may be followed by retching and gagging" |
| Responde o discriminador | em parte — contato: "history of exposure to other susceptible or affected dogs"; estado geral: "few if any additional signs except for some loss of appetite" |
| Diz quando ir | diz quando **pode esperar**: "It is a mild disease that normally improves on its own." E o que muda isso: "Development of more severe signs, including fever, pus-containing nasal discharge, depression" |
| Estrutura | 869 palavras; headings "Tracheobronchitis" e "Infectious Tracheobronchitis of Dogs (Kennel Cough)". O parágrafo de abertura vem antes do primeiro heading. Entraria só a seção de tosse dos canis; a seção "Tracheobronchitis" (bronquite crônica, corticoide, codeína) deveria ser declarada para exclusão |
| Data | revisão completa jun/2018; modificada set/2024 |
| Acesso | abriu em 25/09/2026 |
| Direitos | "Copyright © 2026 Merck & Co., Inc. … All rights reserved." |

##### Cornell Riney Canine Health Center — *Bordetellosis*
`kennel_cough_mild__cornell_bordetelose.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | alta (Cornell University; Brian Collins, DVM) |
| Espécie | cão (cita gato só em zoonose) |
| Cobre os sinais | sim — "loud, high-pitched, persistent “honking” cough"; "trying to clear something from their throat" |
| Responde o discriminador | em parte — "history of exposure to other dogs"; lista de hotel, banho e tosa, creche, parque. Mas também lista "Lethargy" e "Decreased appetite" como sinais comuns |
| Diz quando ir | em parte — "diagnostic testing is not required, especially if the dog is otherwise healthy"; "pneumonia can develop which may also be associated with labored breathing" |
| Estrutura | 861 palavras; 9 headings (Overview, How are dogs infected…, What are the signs?, How is it diagnosed?, How is Bordetella treated?, Vaccination…, How long is a dog contagious?, Zoonotic potential, Outcome). Entrariam Overview, signs, diagnosed, Outcome; excluir tratamento e vacina |
| Data | atualizada em 20/11/2025 |
| Acesso | abriu em 25/09/2026 |
| Direitos | "©2026" Cornell University; sem licença declarada |

#### Frases

| Frase | Status | Fonte | Trecho (literal) |
|---|---|---|---|
| tutor#3 "Tosse forte, como se tivesse algo engasgado na garganta" | sustentada | Cornell | "The most common feature is a loud, high-pitched, persistent “honking” cough. Dog owners may initially feel that their dog is trying to clear something from their throat." |
| tutor#4 "No fim da tosse faz ânsia, parece que vai vomitar" | sustentada | MSD | "The most common sign is spasms of harsh, dry coughing, which may be followed by retching and gagging." |
| diferenciar#1 | **parcial** | MSD | "Tracheobronchitis is usually suspected whenever a dog demonstrates the distinctive harsh cough and has a history of exposure to other susceptible or affected dogs." |

**diferenciar#1, por partes:**
- *Contato com outros cães* — sustentado (MSD e Cornell).
- *Segue ativo e comendo* — parcial, com divergência sobre o apetite: o MSD diz "few if any additional signs except for some loss of appetite"; a Cornell lista letargia e apetite reduzido entre os sinais comuns. As fontes dizem que o cão costuma ficar bem, mas pode comer menos. **O especialista decide.**
- *Lado do coração* (cão mais velho, sopro conhecido, cansa fácil, respira rápido dormindo) — não encontrado nas duas fontes. A VCA *Congestive Heart Failure in Dogs*, capturada em `congestive_heart_failure__vca_icc.txt`, cobre sopro ("in a pet with a heart murmur"), cansaço ("tire out more easily") e frequência em repouso/dormindo. **"Mais velho" não aparece em nenhuma fonte aberta de autoridade.** Não capturei a VCA neste tópico por causa do limite de 2 fontes.

#### Recomendação

- **Primária:** MSD — autoridade alta, diz quando pode esperar e o que muda isso, sustenta a ânsia e o contato.
- **Alternativa:** Cornell — melhor descrição leiga do som ("clear something from their throat"), mas o critério "diz quando ir" é mais fraco.
- **Descartadas:** PDSA *Coughing in Dogs* (só nomeia as causas); Texas A&M Pet Talk 2016 (mais raso); AVMA (página veio vazia para leitura automatizada); VCA *Kennel Cough…* (404); dvm360 *When to take this cough to heart* (403, e é para clínicos); webvet, drfossums, vetmedguide e maven (blogs/comerciais).

#### Não encontrado

- Uma fonte de autoridade que ponha lado a lado a tosse cardíaca e a tosse dos canis, **para tutor**. O que existe com esse formato é de clínica comercial ou blog.
- "Cão mais velho" como marcador da tosse cardíaca.
