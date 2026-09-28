# Tártaro e mau hálito — fontes

**Linha do mapa:** `periodontal_disease_mild`

**Caso da régua:** `b59`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R92 · Revisiting Periodontal Disease in Dogs: How to Manage This New Old Problem? · Antibiotics · 2022. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`c78af961e81fd54d2836ea36949b5393376c99db65c5276b5a1a4dfa96363683`.

A inspeção individual do recorte produziu **73 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Cobre cães e doença periodontal em vários estágios; não cobre gatos.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador B) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

Agente B, rodada N6, acesso em 25/09/2026. Duas frases: uma do tutor, que é a
da **linha leve** ("tá normal, só o bafo"), e um alarme. Casos de régua: fora
do escopo desta tarefa.

#### Candidatas capturadas

##### 1. BluePearl — *Periodontal Disease in Dogs & Cats*
`periodontal_disease_mild__bluepearl_periodontal.txt` ·
https://bluepearlvet.com/pet-blog/periodontal-disease-in-pets-know-the-signs/

| Critério | Resultado |
|---|---|
| Idioma | en |
| Registro | tutor (blog institucional com entrevista) |
| Autoridade | média (rede de hospitais de especialidade; falas de Donnell Hansen, DVM, DAVDC, dentista veterinária) |
| Espécie | cão e gato |
| Cobre os sinais | sim: "chews on one side of their mouth, or noticeably drops food while eating" (texto inicial) |
| Diz quando ir | fraco: "speak to your veterinarian if their appetite has drastically decreased"; "call your veterinarian to schedule an appointment" (itens 4 e 5) |
| Diz quando pode esperar (linha leve) | **não**. Diz o contrário: comer e brincar normal não quer dizer boca saudável ("most indicators are hidden") |
| Estrutura | 979 palavras; texto inicial sem heading, 5 dicas numeradas, Preventative Care is Key, Silent Sufferers. Tem link comercial ("how to get rid of dog breath at home") e o chamado do "National Pet Dental Health Month" |
| Data | publicada em 12/02/2020, modificada em 02/10/2023 |
| Direitos | © 2026 BluePearl Holdings LLC. All rights reserved. |
| Acesso | abriu, 25/09/2026 |

##### 2. Merck (MSD) Veterinary Manual, versão para tutores — *Dental Disorders of Dogs*
`periodontal_disease_mild__msd_dental_dogs.txt` ·
https://www.merckvetmanual.com/dog-owners/digestive-disorders-of-dogs/dental-disorders-of-dogs

| Critério | Resultado |
|---|---|
| Idioma | en |
| Registro | tutor (versão do manual para donos) |
| Autoridade | alta (Alexander M. Reiter, Dipl. Tzt., DEVDC, DAVDC) |
| Espécie | só cão (existe a versão para gatos, *Dental Disorders of Cats*, sem inchaço no rosto) |
| Cobre os sinais | sim: "Bad breath is common." (Gingivitis); "a swelling on the face; or a decrease in appetite" (Endodontic Disease) |
| Diz quando ir | não |
| Estrutura | 2117 palavras; seções Dental Terms, Gum Disease, Gingivitis, Periodontitis, Prevention, Endodontic Disease, Developmental Abnormalities, Unerupted Teeth, Improper Bite, Enamel Defects, Trauma to the Face and Jaw, Tooth Decay. Boa para declarar; muito conteúdo fora do quadro (má oclusão, trauma) |
| Data | publicada em 30/05/2018, "Last updated: Oct 2025" |
| Direitos | © 2026 Merck & Co., Inc., Rahway, NJ, USA and its affiliates. All rights reserved. |
| Acesso | abriu, 25/09/2026 |

#### Frase por frase

| Frase | Status | Trecho (literal) |
|---|---|---|
| tutor#10 Tá comendo e brincando normal, só o bafo que incomoda | sustentada | BluePearl: "The truth is most patients won’t show signs of oral pain and will continue to go on playing and eating." Mais: "Does your pet’s breath smell consistently foul (like rotten eggs)? There may be more going on than just bad breath." |
| alarme#2 Parou de comer, mastiga de um lado só ou o rosto inchou | parcial | BluePearl: "…often cause pets to drool, drop food, and/or chew to one side of their mouth." BluePearl: "…especially if they are reluctant to eat their normal food and/or treats." MSD: "a swelling on the face; or a decrease in appetite." |

**Divergência de enquadramento (para o especialista):** a frase tutor#10
existe para a linha "rotina" (pode esperar). A BluePearl confirma o relato:
o animal com doença periodontal segue comendo e brincando, e o hálito é o
que o tutor percebe. Mas ela tira a conclusão oposta à da linha leve: sem
sinal visível, a doença pode estar avançada, e por isso pede exame anual com
raio-x. A MSD vai no mesmo sentido: "most dogs mask their pain, making
diagnosis difficult". Nenhuma das duas diz que comer e brincar normal
significa doença leve.

**No alarme:** os três sinais só aparecem somando as duas fontes. O inchaço
no rosto da MSD está na seção de doença **endodôntica** (dentro do dente,
fratura), não na de doença periodontal. E nenhuma das duas trata esses
sinais como alarme de urgência.

#### Recomendação

- **MSD (cão): primária para o alarme.** Autoridade alta, seções limpas.
  Não serve para a frase leve.
- **BluePearl: alternativa, e a única para a frase leve.** É autoridade
  média, tem cara de conteúdo de campanha e não diz quando pode esperar.
- **Alternativa para gato** (aberta, não capturada pelo limite de 2 fontes):
  Cornell Feline Health Center, *Feline Dental Disease*. Traz "may stop
  eating", "turn their heads to the side when chewing" e "develop bad
  breath", mas não fala de inchaço no rosto nem de comer normal. Na mesma
  Cornell, *Tooth Resorption* diz "appetite appears to be normal but … chew
  on just one side".
- **Não abertas:** AVMA *Pet dental care* (o script não conseguiu extrair o
  texto da página); Veterinary Partner/VIN (pediu CAPTCHA; não contornei).

#### Não encontrado

- **Fonte que diga quando a doença periodontal pode esperar**, isto é, que
  hálito ruim num animal que come e brinca normal é caso de consulta de
  rotina. Todas as fontes abertas tratam o "normal" como disfarce.
- **Fonte em português**: não procurei. A busca na web se esgotou (limite de
  200 buscas da sessão) no meio deste tópico.
