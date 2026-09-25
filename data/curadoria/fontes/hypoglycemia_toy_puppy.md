# Hipoglicemia em filhote de raça pequena — fontes

**Linha do mapa:** `hypoglycemia_toy_puppy`

**Caso da régua:** `b47`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R80 · Neonatal hypoglycemia in dogs—pathophysiology, risk factors, diagnosis and treatment · Frontiers in Veterinary Science · 2024. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`3ce285a546e871c580e1f2e7094ba5c725b7b043dfff6c8da220a3162abae5c9`.

A inspeção individual do recorte produziu **129 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Cobre neonatos, não especificamente filhotes toy de até três meses; páginas de tratamento foram excluídas.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador C) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `hypoglycemia_toy_puppy` (cão; imediato)
**Pesquisado em:** 25/09/2026 · **Frases do grupo C:** tutor#1, tutor#8

#### Régua de aptidão

##### American Kennel Club — *Hypoglycemia in Dogs: Signs, Symptoms, and Treatments*
`hypoglycemia_toy_puppy__akc_hipoglicemia.txt`

| Critério | Avaliação |
|---|---|
| Idioma | en |
| Registro | tutor |
| Autoridade | **média** (entidade de criação/registro de raças; autora Caroline Coile, PhD, não veterinária; as falas clínicas são do Dr. Jerry Klein, DVM, veterinário-chefe do AKC) |
| Espécie | cão |
| Cobre os sinais | sim — "extreme lethargy, incoordination, unconsciousness or seizures"; "lack of balance" |
| Responde o discriminador | em parte — "very young or very small puppies, especially young toy puppies"; "under 12 weeks". Não nomeia raças |
| Diz quando ir | sim — "But they should then be taken to veterinarian immediately for further care." |
| Estrutura | 1.343 palavras; headings: How Glucose Levels Work, Causes…, Physiological causes, Pathological causes, Signs…, Diagnosing…, Treating…, Preventing…. Entrariam Physiological causes e Signs; o resto é conduta ou é adulto. **Defeito de extração:** a lista de sinais neurológicos logo após "such as:" (sonolência, desmaio, convulsão, colapso, tremor, inquietação — vista no navegador) **não entrou no .txt**. Vale olhar o script |
| Data | 19/11/2024 |
| Acesso | abriu em 25/09/2026 |
| Direitos | "© The American Kennel Club, Inc. 2026. All rights reserved." + aviso de que não é conselho profissional |

#### Frases

| Frase | Status | Trecho (literal) |
|---|---|---|
| tutor#1 "É filhote de yorkshire, chihuahua, pinscher ou spitz, bem pequenininho." | **parcial** | "Puppy or toy dog hypoglycemia: This condition can occur in very young or very small puppies, especially young toy puppies." |
| tutor#8 "Tá cambaleando, andando como se estivesse bêbado." | sustentada | "These puppies present for extreme lethargy, incoordination, unconsciousness or seizures." |

- **tutor#1:** sustenta "filhote bem pequenininho / raça toy", mas **não nomeia** yorkshire, chihuahua, pinscher nem spitz. O MSD (Pet Owner, *Congenital and Inherited Disorders of the Nervous System in Dogs*, forebrain disorders) diz só "seen in toy breeds in the first 6 months of life"; o Merck profissional diz o mesmo. Nenhuma das três nomeia raças.
- **tutor#8:** a fonte diz *incoordination* e *lack of balance*; a imagem do "bêbado" é do tutor.

#### Recomendação

- **Alternativa (não primária):** AKC — cobre os sinais e diz quando ir, mas a autoridade é média e não nomeia raças.
- **Descartada:** MSD Pet Owner (uma frase só, dentro de uma página longa sobre outras doenças neurológicas; sem sinais). Dissertação UNESP 2023 (*Correção da hipoglicemia neonatal…*): é de neonato de cesariana, não de filhote toy.
- **Bloqueadas / não verificadas:** VIN Veterinary Partner, *Hypoglycemia (Low Blood Sugar) in Toy Breed Dogs* (R38 em `referencias.md`) — CAPTCHA, não contornei. Os resultados de busca trazem uma lista de raças (Chihuahua, Yorkshire, Maltês, Poodle Toy, Lulu da Pomerânia) que pode vir dela, mas **não verifiquei a origem**. **Uma pessoa precisa abrir no navegador.** Vets Now *Hypoglycaemia in dogs* — 403.

#### Não encontrado

- Fonte de autoridade alta ou média, aberta, que **nomeie as raças**. Pinscher não aparece em nenhuma fonte de autoridade vista. "Spitz" só aparece como Pomeranian/Lulu em material comercial.
- Fonte em português: só pet shops, blogs e páginas de clínica (Patas da Casa, Chef Bob, PeritoAnimal, Pet Care, seu.dog, Royal Canin Portal Vet) — recusadas.
- O orçamento de buscas da sessão acabou durante esta linha. Não pude tentar PDSA, Blue Cross nem UC Davis por busca.
