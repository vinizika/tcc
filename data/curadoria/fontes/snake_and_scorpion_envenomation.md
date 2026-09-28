# Acidente com cobra ou escorpião — fontes

**Linha do mapa:** `snake_and_scorpion_envenomation`

**Caso da régua:** `b45`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R78 · Zootoxins and Domestic Animals: A European View · Toxins · 2024. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`4d5aefb6734fdf89db694f139564525cf38baf69a5a616d1a5672b5eb1979ac2`.

A inspeção individual do recorte produziu **105 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

Revisão europeia; espécies, epidemiologia e condutas podem não representar o Brasil.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador A) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `snake_and_scorpion_envenomation` · cão e gato · `imediato`
**Pesquisado em:** 25/09/2026 (agente A, rodada N6)
**Escopo:** três frases `geral` da ficha de busca (tutor#10, alarme#3, alarme#4).

#### Régua de aptidão

##### Cadernos Técnicos de Veterinária e Zootecnia nº 75, *Animais Peçonhentos* (UFMG/CRMV-MG, dez. 2014): `snake_and_scorpion_envenomation__ufmg_ct75_2014_peconhentos.pdf`

| Critério | Resultado |
|---|---|
| URL | https://vet.ufmg.br/wp-content/uploads/2019/06/Caderno-T%C3%A9cnico-75.pdf. A página do número é https://vet.ufmg.br/caderno-tecnico/cadernos-tecnicos-de-veterinaria-e-zootecnia-no-75-animais-peconhentos/ |
| Idioma / registro | pt · clínico (educação continuada para veterinários) |
| Autoridade | alta (Escola de Veterinária da UFMG com o CRMV-MG). Autores: Benito Soto Blanco e Marília Martins Melo (todos os capítulos usados); Guilherme de Caro Martins (Araneísmo) |
| Espécie | **cão** nos capítulos usados (figuras de cães picados); gato quase ausente (3 menções no PDF inteiro). Há muito texto sobre bovinos e equinos |
| Cobre os sinais | sim: escorpião, "dor local intensa… vômitos, sialorreia"; cascavel, "Frequentemente não há alteração no local da picada"; jararaca, "dois pequenos pontos hemorrágicos" |
| Responde o discriminador | ajuda a separar jararaca de cascavel: "Sinais clínicos locais são caracterizados por dor intensa, edema e hemorragia" contra "não há alteração no local da picada" |
| Diz quando ir | não orienta o tutor. Para o clínico: "a gravidade pode ser determinada em uma a duas horas após o acidente" |
| Estrutura | PDF de 46 páginas, ~23.700 palavras, 9 capítulos (Ofidismo, Botrópico, Crotálico, Laquético, Elapídico, Sapos, Escorpionismo, Araneísmo, Apidismo). Tem soroterapia e doses. **Vai exigir recorte forte por página ou capítulo na ingestão**, e o capítulo de sapos é de outra linha do mapa (`toad_bufotoxin_poisoning`) |
| Data | dezembro de 2014 |
| Direitos | "Permite-se a reprodução total ou parcial, sem consulta prévia, desde que seja citada a fonte." |
| Acesso | abriu em 25/09/2026. Mesma cadeia TLS incompleta da UnB, resolvida da mesma forma (bundle com o intermediário oficial, verificação ativa). O PDF capturado é idêntico byte a byte ao baixado com curl |

#### Frases

| Frase | Status | Trecho (capítulo) |
|---|---|---|
| tutor#10: Depois do escorpião, grita de dor, baba e vomita. | sustentada | "Além da dor local intensa, outros sinais clínicos nos casos moderados incluem náuseas, vômitos, sialorreia, agitação ou sonolência, taquicardia, taquipneia e picos hipertensivos." (Escorpionismo). O grito: "pode apresentar vocalizações, inquietação ou até agressividade" |
| alarme#3: Sangra pelos furinhos, pelo nariz ou pela gengiva. | parcial | "Podem ser identificados dois pequenos pontos hemorrágicos" (Botrópico). Para o resto, só o genérico "hemorragias em mucosas ou subcutâneas". "epistaxes, gengivorragia" aparecem só no capítulo Laquético, **e descritos em humanos** ("ainda não está descrita em animais domésticos") |
| alarme#4: Quase não inchou, mas ficou fraco, com as pálpebras caídas ou xixi escuro. | sustentada | "Frequentemente não há alteração no local da picada, o que impossibilita sua localização" (Crotálico). Fraqueza: "ataxia, paralisia flácida da musculatura". Xixi escuro: urina "variando de avermelhada a marrom escura". Pálpebras: no crotálico, "Fácies miastênicas" e "flacidez da musculatura da face"; "ptose palpebral" literal só no capítulo Elapídico |

Nos PDFs, os trechos foram conferidos no texto extraído com `pymupdf`, com espaços e quebras de linha normalizados. As citações da coluna "observação" do JSON desfazem a hifenização do PDF (hífen invisível U+00AD seguido de quebra de linha); o JSON avisa onde isso ocorre.

#### Recomendação

- **Primária PT:** Caderno Técnico nº 75. É brasileiro e trata das espécies de cobra e escorpião do Brasil, com sinais em cães. Cobre em parte a lacuna de `referencias.md` ("Casuística brasileira de escorpionismo e araneísmo… não encontrada"): é revisão brasileira com sinais em cães, não casuística, e não cobre gatos. Contra: registro clínico, tamanho e conteúdo terapêutico.

#### Não encontrado

- Fonte em inglês para tutor: **não foi buscada**, porque a cota de buscas web da sessão acabou (200/200) antes deste tópico. O Caderno foi achado navegando o índice dos Cadernos Técnicos, que o roteiro recomenda.
- Sangramento pelo nariz ou pela gengiva **em cão ou gato** após picada de jararaca, descrito literalmente numa fonte veterinária.
- Gatos: o caderno quase não trata de gatos.
- Cadernos Técnicos nº 87 (Emergência): o endereço presumido do PDF devolveu 404.
