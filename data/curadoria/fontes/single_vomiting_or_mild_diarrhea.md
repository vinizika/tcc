# single_vomiting_or_mild_diarrhea — vômito isolado ou fezes moles em animal ativo

**Linha do mapa:** `pode_esperar` · `rotina` · `ambos` · prioridade **A** · etapa 1
**Par de confusão:** `vomiting_and_diarrhea` · `gastric_dilatation_volvulus` ·
`parvovirus_panleukopenia` · `gastrointestinal_foreign_body`
**Discriminador:** *Continua comendo e ativo? Sai conteúdo quando vomita? Tem
sangue? Passou de 24 horas?*

**Estado:** as duas primárias e a alternativa foram validadas clinicamente
pela ASAVET em 20/09/2026, mas permanecem fora da ingestão por licença
indefinida. Uma fonte substituta CC BY foi capturada e inspecionada para o
perfil experimental; o arquivo novo ainda aguarda validação da ASAVET.

> **Segunda linha levada de ponta a ponta, e a primeira do lado leve.** O que
> ela testa não é o pesquisador em geral — é a seção "Linha leve" do roteiro,
> escrita em 12/09 a partir de uma busca, sem piloto. Onze das 31 linhas da
> etapa 1 dependem dela.

## Casos de régua propostos

Escritos **antes de abrir qualquer fonte**, a partir da coluna `sinais` do
mapa. A linha não tinha caso: os cinco casos leves da régua são espirro,
coceira, claudicação, olho e coriza — **nenhum de vômito**, que é a queixa
mais frequente do pronto-socorro em cães.

| id | Relato | O que ele exercita |
|---|---|---|
| b19 | meu cachorro vomitou uma vez hoje de manhã, saiu ração, mas depois comeu normal e está brincando igual sempre | Sai conteúdo · come · ativo — o oposto de b12 (GDV) em três dos quatro discriminadores |
| b20 | minha gata vomitou uma bola de pelo ontem e hoje está comendo e brincando normalmente | O lado gato, que a coluna `sinais` menciona e nenhum caso cobre |
| b21 | meu cão fez fezes mais moles hoje, uma vez só, mas está comendo e correndo normal, sem sangue | O lado diarreia, sem sangue, dentro de 24 h — o oposto de b07 |

Eles entram em `data/retrieval/cases.csv` **quando o lote for indexado**, não
agora: acrescentar caso muda o sha256 do arquivo e torna as rodadas anteriores
não comparáveis.

## As candidatas

### 1. PDSA — *Vomiting in dogs* · **primária (cão)**

`https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/vomiting-in-dogs`
Capturado 12/09 · 933 palavras · `6a2dc5a5…`

| Critério | Veredito | Citação |
|---|---|---|
| Idioma | `en` | — |
| Registro | `tutor` | — |
| Autoridade | `alta` | Maior instituição de caridade veterinária do Reino Unido; página datada (*Published: October 2024*) |
| Espécie | cão — **metade da linha** | — |
| Cobre os sinais | **sim** | "has only vomited once and seems otherwise fine in themselves" |
| **Responde o discriminador** | **sim** | "it may not be necessary to contact your vet immediately. However, you'll need to monitor them closely" |
| Diz quando ir | **sim** | "Continuous retching and/or a bloated tummy – these can be symptoms of a GDV" |
| Estrutura | Overview · When to contact your vet · Home remedies for vomiting in dogs · Dog vomit colour chart | |

**Por que é a melhor para esta linha:** a seção *When to contact your vet*
traz, em um só lugar, a frase que autoriza esperar **e** a lista do que muda
isso — sangue, letargia, mais de 24 horas, abdome dolorido, e o retching
contínuo com barriga estufada. É literalmente o discriminador do mapa, escrito
do jeito que o tutor fala.

**Seções que entram** (conferido no `--inspect`): *Overview* e *When to
contact your vet*. **Fora:** *Home remedies for vomiting in dogs* — é
orientação de tratamento em casa, e o sistema orienta a procurar
atendimento, não a tratar —, *Dog vomit colour chart* e o rodapé.
**7 seções detectadas, 2 indexadas, 9 trechos**: 280 das 933 palavras.

### 2. Cornell Feline Health Center — *The Danger of Hairballs* · **primária (gato)**

`https://www.vet.cornell.edu/.../danger-hairballs`
Capturado 12/09 · 698 palavras · `a75db0bb…`

| Critério | Veredito | Citação |
|---|---|---|
| Idioma | `en` | — |
| Registro | `tutor` | — |
| Autoridade | `alta` | Universidade; cita Dr. Richard Goldstein nominalmente |
| Espécie | gato — **a outra metade** | — |
| Cobre os sinais | **sim** | "for a cat to regurgitate a hairball once every week or two. Aside from inconvenience to the owner, this is nothing to worry about" |
| **Responde o discriminador** | **sim** | "lethargic, refuses to eat for more than a day or two or has had repeated episodes of unproductive retching" |
| Diz quando ir | **sim** | mesma frase |
| Estrutura | The Danger of Hairballs · Hazardous Potential · Relieving the Obstruction | |

**Fecha uma lacuna declarada.** A [rodada 11](../../../evidencias/joao/2026-09-12-12-mapa-de-assuntos.md)
registrou como não encontrado o "limiar numérico de frequência de bola de pelo
em gato". Está aqui: **uma a cada uma ou duas semanas é normal**.

**Seções** (conferido no `--inspect`): *Hazardous Potential*, que traz o
limiar e o alarme. **Fora:** *Relieving the Obstruction*, conduta clínica e
cirúrgica. **3 detectadas, 1 indexada, 6 trechos**: 215 das 698 palavras.

Declarar o limite foi necessário: sem *Relieving the Obstruction* em
`exclude_sections`, a seção *Hazardous Potential* engolia **417 palavras**
em vez de 215, levando a cirurgia junto. É a mesma armadilha do piloto da
torção gástrica, reproduzida num site diferente.

### 3. CRMV-SP — *Vômitos frequentes indicam sérios problemas de saúde* · **alternativa**

`https://crmvsp.gov.br/vomitos-frequentes-indicam-serios-problemas-de-saude-em-caes-e-gatos/`
Capturado 12/09 · 509 palavras · `e8ce6f4f…`

| Critério | Veredito | Citação |
|---|---|---|
| Idioma | **`pt`** — corpo em português de verdade | "Vômito constante ou diarréia são dois sintomas comuns em cães e gatos" |
| Registro | `tutor` | — |
| Autoridade | **`media`** — ver ressalva | — |
| Espécie | ambos | — |
| Cobre os sinais | **parcial** | Fala de vômito, mas o foco é o **constante** |
| **Responde o discriminador** | **não** — ver abaixo | — |
| Diz quando ir | parcial | "se essa frequência for de uma vez por semana, o animal deve passar por avaliação" |

**Duas ressalvas, e a segunda é a que importa.**

**Autoridade.** O domínio é de conselho regional, mas o conteúdo é release de
agência — o rodapé diz "Fonte: Sigma Six Comunicação", e a veterinária citada
é de um hospital privado. O CRMV publicou; não redigiu. O texto ainda traz
erros de revisão no original ("parate", "explicas", "consequencia"). Classifico
como **média**, não alta, e o especialista precisa saber disso.

**Ela responde outra pergunta.** "Vômitos ocasionais, uma vez por mês, são
aceitáveis, mas se essa frequência for de uma vez por semana, o animal deve
passar por avaliação" é sobre **frequência ao longo de semanas**. A linha do
mapa pergunta sobre **o episódio de hoje**: vomitou uma vez, está comendo e
brincando. São perguntas diferentes, e um trecho desses recuperado para um
relato agudo pode confundir mais do que ajuda.

**E ela não pode ser curada por seção.** O `--inspect` mostra uma única
seção (`Document`, pelo fallback), porque a página não tem estrutura de
heading. É tudo ou nada — e o "tudo" inclui o parágrafo sobre medicação
("já existem medicações veterinárias super específicas") e o rodapé da
agência. Resultado: **17 trechos**, mais do que as duas primárias somadas
(9 + 6 = 15). A fonte mais fraca é a que mais competiria na busca.

**O que ela tem de bom** e nenhuma outra tem em português: a distinção entre
vômito e regurgitação, e o vocabulário de alarme que o tutor brasileiro usa —
"cor de borra de café" para sangue digerido, odor fétido para obstrução.

## O que este piloto ensinou sobre a linha leve

**1. A hipótese do roteiro estava meio certa, e precisa de ajuste.** O roteiro
diz: *"a fonte quase sempre é a mesma do par grave; capture-a duas vezes, com
seções diferentes"*. Não foi o que aconteceu. A PDSA tem **duas páginas**: a de
sintoma (`symptoms/vomiting-in-dogs`) e a de condição
(`conditions/gdv-...`), e cada linha ficou com a sua. A captura dupla é o caso
em que o site **só** tem a página de sintoma — não a regra.

**2. Buscar pela queixa funcionou.** "dog vomited once eating normally when to
worry" achou a página certa de primeira; buscar por nome de quadro não teria
achado, porque "vômito isolado em animal ativo" não é um quadro com nome.

**3. O critério invertido é o que mais separa.** As três candidatas falam de
vômito. A que serve é a que diz **quando pode esperar** — e foi por esse
critério que a fonte em português caiu para alternativa.

**4. O dilema idioma × registro ficou pior do que a rodada 12 descreveu.** Lá
o problema era: em português só há fonte clínica ou comercial. Aqui apareceu
outra camada: **a fonte em português disponível responde uma pergunta
diferente**. Não é só registro — é escopo. Se isso se repetir nas outras dez
linhas leves, o
[redator de lacuna](../../../agentes/README.md) deixa de ser plano B e vira o
caminho principal para o lado leve em português.

**5. Confirmação nº 2 da armadilha do MSD.** A página
`msdvetmanual.com/pt/cat-owners/…/vômito-em-gatos` tem **títulos de seção em
português e corpo em inglês** — "Manejo de bolas de pelo em gatos", "Vômito de
curta duração ou ocasional", e o texto abaixo em inglês. Não foi capturada.
Vale como evidência: a tradução parcial do MSD não é exceção de uma página.

## Não encontrado

**Fonte em português, de autoridade alta, que responda o discriminador desta
linha.** Procurei em SciELO, no MSD em português, nos Cadernos Técnicos e em
CRMVs. O que existe trata de vômito **crônico ou frequente**, não do episódio
isolado em animal ativo. É a lacuna que o [B-54](../../../evidencias/backlog.md#b-54)
pode ou não fechar, e o argumento mais concreto até agora para o redator de
lacuna.

## Validação

A ASAVET aprovou as três capturas em 20/09/2026. As ressalvas de procedência,
escopo e possível confusão temporal continuam registradas. Como os direitos
continuam `pending_review`, os arquivos não foram copiados para
`backend/data/documents/`.

## Substituição com redistribuição permitida

R105 · Holzmann et al. · *Utility of diagnostic tests in vomiting dogs
presented to an internal medicine emergency service* · Frontiers in Veterinary
Science 10:1063080 · 2023 · DOI `10.3389/fvets.2023.1063080` · CC BY 4.0.

A captura usa somente a primeira página do PDF, que contém o resumo e a
separação entre vômito simples e complicado. O recorte foi inspecionado e
preserva o texto original. SHA-256:
`482a69011e47d209b75bd3d38dc5e0ef7332faf73690edaed0a3c7e2e0a15008`.

O arquivo entrou somente no perfil `experimental` e permanece
`pending_specialist`, pois foi produzido depois da validação das fontes
anteriores.
