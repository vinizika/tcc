# Queda de altura em gato — fontes

**Linha do mapa:** `high_rise_syndrome_cats`

**Caso da régua:** `b49`, escrito antes da pesquisa

**Pesquisado em:** 19/09/2026

**Estado:** `fonte_aprovada` — validada pela ASAVET em 20/09/2026

## Fonte experimental

R82 · Prognostic Performance of Shock Index in Cats with Trauma-Induced Shock · Animals · 2026. A licença e a procedência estão
registradas no sidecar. O arquivo integral foi preservado com SHA-256
`ad24fe0d6216bbd2841b71afe19693fc7fc2820d1c80bf533a3308e0104dc93d`.

A inspeção individual do recorte produziu **77 chunks** e confirmou que
nenhum registro foi escrito no ChromaDB durante a inspeção.

## Limitações

A maioria dos animais teve queda de altura, mas todos já apresentavam choque; não cobre gatos aparentemente normais.

A captura está `approved_by_specialist`, com validação da ASAVET em 20/09/2026.
O `ingestion_scope` permanece `experimental_only`; a validação clínica, por si
só, não autoriza ativação da coleção.

## Fontes para as frases gerais da ficha de busca (25/09, rodada 27)

> Pesquisa de um agente de IA (pesquisador A) para as frases marcadas como conhecimento geral na ficha de busca do tópico. As fontes aguardam o especialista (`PARA-VALIDAR.md`); a frase da ficha não muda.

**Linha do mapa:** `high_rise_syndrome_cats` · gato · `imediato`
**Pesquisado em:** 25/09/2026 (agente A, rodada N6)
**Escopo:** uma frase `geral` da ficha de busca (tutor#8).

#### Régua de aptidão

##### 1. UnB, TCC *Síndrome do Gato Paraquedista: revisão da literatura* (2018): `high_rise_syndrome_cats__unb_2018_tcc_sgp.pdf`

| Critério | Resultado |
|---|---|
| URL | https://bdm.unb.br/bitstream/10483/22080/1/2018_IsabelaSimasDeDeusVieira_tcc.pdf |
| Idioma / registro | pt · acadêmico |
| Autoridade | alta pelo roteiro (repositório universitário), mas é **TCC de graduação**: revisão aprovada por banca, não revisada por pares. Autora: Isabela Simas de Deus Vieira; orientadora: Ana Carolina Mortari |
| Espécie | gato. Sim |
| Cobre os sinais | sim: "os gatos podem apresentar epistaxe"; "fratura dentária"; "separação de sínfise mandibular" |
| Diz quando ir | sim, dirigido ao clínico: "deve sempre ser tratada como emergência grave" |
| Estrutura | PDF de 40 páginas, ~9800 palavras: revisão, triagem, choque e contusão pulmonar. Quase tudo é conduta clínica, o que exigirá um recorte forte na ingestão |
| Data | 2018 |
| Direitos | cessão de direitos: a UnB pode reproduzir só para fins acadêmicos; "nenhuma parte desta monografia pode ser reproduzida sem a autorização por escrito do autor" |
| Acesso | abriu em 25/09/2026. O servidor manda a cadeia de certificados incompleta, e o Python recusou o TLS. Completei a cadeia com o intermediário oficial (RNP ICPEdu GR46, baixado do AIA da GlobalSign) num bundle na pasta temporária, via `REQUESTS_CA_BUNDLE`. A verificação continuou ativa e o script não foi alterado |
| Tipo na ficha | `peer_reviewed_article`, por falta de tipo "tese/TCC" no script. **Ajustar na aprovação** |

##### 2. UFSC, TCC *Síndrome do Gato Paraquedista – Relato de Caso* (2022): `high_rise_syndrome_cats__ufsc_2022_tcc_sgp.pdf`

| Critério | Resultado |
|---|---|
| URL | https://repositorio.ufsc.br/bitstream/handle/123456789/246889/S%C3%ADndrome%20do%20Gato%20Paraquedista%20-%20Relato%20de%20Caso.pdf?sequence=1&isAllowed=y |
| Idioma / registro | pt · acadêmico |
| Autoridade | alta pelo roteiro (repositório universitário), mas é TCC de graduação com relato de caso. Autora: Taynara Regina Machado; orientadora: Marcy Lancia Pereira |
| Espécie | gato. Sim |
| Cobre os sinais | sim: "quem atinge primeiro o solo é o queixo"; "epistaxe"; "traumas dentários" |
| Diz quando ir | parcial: "A SGP apesar de ser considerada uma emergência" |
| Estrutura | PDF de 40 páginas, ~7600 palavras. O caso clínico aconteceu em Portugal |
| Data | 2022 |
| Direitos | o PDF não declara licença; a página do repositório não foi conferida |
| Acesso | abriu em 25/09/2026 |
| Tipo na ficha | `case_report` |

#### Frases

| Frase | Status | Trecho |
|---|---|---|
| tutor#8: Sangrou pelo nariz ou pela boca, machucou o queixo ou quebrou dente | parcial | UnB: "as lesões faciais incluem fratura de palato, separação de sínfise mandibular, fratura de mandíbula, fratura dentária e luxação da articulação temporomandibular e, nesses casos, os gatos podem apresentar epistaxe". Sustenta nariz, dente e queixo (a UFSC usa a palavra "queixo"). **Nenhuma das duas fala de sangue pela boca** |

#### Recomendação

- **Primária PT:** UnB, a mais completa nas lesões da face. Contra: registro acadêmico, é TCC e a cessão de direitos é restritiva.
- **Alternativa PT:** UFSC, que usa a palavra "queixo" e traz relato de caso com epistaxe.
- **Não capturada, e melhor para a frase:** Candela Andrade et al., *High-rise syndrome in cats (part 2): injury patterns and survival rate*, J Feline Med Surg 2025, PMC12126627, CC BY-NC 4.0. Ao ser aberta pela ferramenta de leitura, registrou epistaxe, "mouth bleeding", fratura de mandíbula e lesão dentária. O script foi recusado: o PMC devolveu verificação anti-robô (18 palavras) e a SAGE, HTTP 403. **Uma pessoa pode baixar o PDF manualmente.**

#### Não encontrado

- Fonte para tutor, com autoridade, que cite sangue pelo nariz ou pela boca após a queda. O Animal Medical Center (NY) cita "fractured teeth and hard palates" e fraturas de mandíbula. O iCatCare *High-rise cats* cita só "facial injuries such as jaw fractures". A Blue Cross devolveu HTTP 403. O PubMed (Bonner et al. 2012, lesões orofaciais) pediu CAPTCHA, que não contornei.
