# Queimadura e choque elétrico — fontes

**Linha do mapa:** `burns_and_electrical_injury`

**Caso da régua:** `b50`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R83 · Successful management of pulmonary edema secondary to accidental electrocution in a young dog · BMC Veterinary Research · 2024. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`5adc0b96a6cb6b90f4672a6ba5219dbf2b7789ff34416c87ef7567757dc979c1`.

A inspeção individual do recorte produziu **47 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Relato canino de eletrocussão; não cobre queimaduras térmicas ou químicas.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador A) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `burns_and_electrical_injury` · cão e gato · `imediato`
**Pesquisado em:** 25/09/2026 (agente A, rodada N6)
**Escopo:** uma frase `geral` da ficha de busca (tutor#10).

#### Régua de aptidão

##### 1. Texas A&M, *Pet Burns* (Pet Talk): `burns_and_electrical_injury__tamu_pet_burns.txt`

| Critério | Resultado |
|---|---|
| URL | https://vetmed.tamu.edu/news/pet-talk/pet-burns |
| Idioma / registro | en · tutor (coluna de divulgação da faculdade, com entrevista da Dr. Alison Diesel, dermatologia) |
| Autoridade | alta (faculdade de veterinária) |
| Espécie | cão e gato ("dogs and cats", "puppies or cats chewing on plugged in electrical cords") |
| Cobre os sinais | sim: "more severe burns can cause burning or singeing of the coat"; "may turn black, crusty" |
| Diz quando ir | sim: "burns are considered to be emergencies in just about all situations" |
| Estrutura | 1107 palavras, texto corrido **sem títulos de seção**: vai tudo ou nada. Inclui dica sobre secador e inalação de fumaça, e uma frase de conduta caseira ("removing the hot material would be good") |
| Data | 22/09/2011 (antiga) |
| Direitos | © 2026 Texas A&M University; licença de reuso não declarada |
| Acesso | abriu em 25/09/2026 |

##### 2. Cruz Vermelha Americana, *Burns in Dogs*: **captura falhou**

| Critério | Resultado |
|---|---|
| URL | https://www.redcross.org/take-a-class/resources/learn-pet-first-aid/dog/burns |
| Conteúdo (lido fora do script) | "Signs of first degree burn include: Loss of fur Reddening of the skin"; "The area will look charred (black and leathery)" |
| Autoridade | média (entidade de primeiros socorros, não veterinária) |
| Captura | o script extraiu só o banner de promoções da loja (85 palavras) e deu aviso, mas não recusou. **O arquivo `burns_and_electrical_injury__redcross_dog_burns.txt` + `.json` ficou na pasta de capturas e deve ser descartado**: não contém a página |

#### Frases

| Frase | Status | Trecho |
|---|---|---|
| tutor#10: O pelo ficou chamuscado ou caiu, e a pele embaixo ficou vermelha ou escura | sustentada | "Initially, it may start as the skin itself just looks a little red or inflamed, while more severe burns can cause burning or singeing of the coat." O resto está na mesma fonte: "the pet’s hair may become dry, brittle, curled, or even lost completely" e "The skin may look red initially, but then may turn black, crusty" |

#### Recomendação

- **Primária:** Texas A&M. Cobre as quatro partes da frase (chamuscado, caiu, vermelha, escura) e diz que é emergência. Contra: é de 2011 e não tem estrutura de seções.
- **Descartada:** Cruz Vermelha, porque a captura saiu vazia.
- **Não capturadas:** VCA *Burns in Dogs* e *Burns in Cats* ("Affected tissue can be white, red, or black"), que não falam do pelo; Clinician's Brief *Burns* ("hair epilates easily"), em registro clínico.

#### Não encontrado

- Fonte em português com autoridade que descreva a aparência da queimadura: a busca devolveu só pet shop e indústria. O artigo da revista *Veterinária e Zootecnia* (rvz.emnuvens.com.br) não abriu, porque o DNS não resolve.
- PDSA *First aid for burns* e MSD *What to Do in a Dog or Cat Emergency* não descrevem a aparência. O MSD diz só "fur hides damage".
