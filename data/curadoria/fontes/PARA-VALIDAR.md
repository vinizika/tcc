# Para validar — a mesa dos especialistas

Uma linha por fonte capturada. A pergunta é sempre a mesma:

> **Esta fonte serve como referência para este quadro, para um tutor
> brasileiro?**

Três respostas possíveis: **sim** · **não** · **com ressalva** (e a ressalva
escrita). Quem responde põe o nome e a data — e é isso que vai para
`validation_status` e `specialist` na ficha, e para a coluna `validacao` do
mapa.

O que você recebe é um **arquivo**, não um link: o texto foi capturado na
data indicada e tem hash. A página pode mudar amanhã; o que aprovarmos é o
que será indexado.

| Quadro | Fonte | Idioma / registro | Seções que entrariam | Trechos | Veredito | Quem · quando |
|---|---|---|---|---|---|---|
| Torção gástrica | [PDSA — GDV in dogs](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/conditions/gdv-gastric-dilatation-volvulus-in-dogs) · `gastric_dilatation_volvulus__pdsa` | en · tutor | Overview · What is GDV? · Which dogs are most at risk · GDV Symptoms | 9 | | |
| Torção gástrica | [Ciência Rural 2012 — Síndrome da dilatação volvo gástrica](https://www.scielo.br/j/cr/a/CPzTSK3tQkWxFSz7Q3L3zLv/?lang=pt) · `gastric_dilatation_volvulus__scielo_2012` | pt · acadêmico | só "Síndrome da dilatação volvo gástrica" (definição e fatores de risco) | 29 | | |
| Vômito isolado | [PDSA — Vomiting in dogs](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/symptoms/vomiting-in-dogs) · `single_vomiting_or_mild_diarrhea__pdsa_vomito` | en · tutor | Overview · When to contact your vet | 9 | | |
| Vômito isolado (gato) | [Cornell — The Danger of Hairballs](https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information/feline-health-topics/danger-hairballs) · `single_vomiting_or_mild_diarrhea__cornell_bola_pelo` | en · tutor | Hazardous Potential | 6 | | |
| Vômito isolado | [CRMV-SP — Vômitos frequentes](https://crmvsp.gov.br/vomitos-frequentes-indicam-serios-problemas-de-saude-em-caes-e-gatos/) · `single_vomiting_or_mild_diarrhea__crmvsp` | **pt** · tutor | a página inteira — não tem heading para curar | 17 | | |

## Perguntas da leva do vômito isolado (12/09)

1. **O limiar do CRMV-SP confunde?** A única fonte em português que achamos
   diz que "vômitos ocasionais, uma vez por mês, são aceitáveis, mas se essa
   frequência for de uma vez por semana, o animal deve passar por avaliação".
   Isso responde *com que frequência é demais*. O caso que o sistema recebe é
   outro: *vomitou uma vez hoje e está comendo e brincando*. Vale indexar, ou
   um trecho desses atrapalha quem está com um episódio agudo?

2. **Uma bola de pelo a cada uma ou duas semanas é normal** (Cornell), e mais
   de uma por mês merece consulta. Esse número vale para o gato brasileiro?

3. **A fonte do CRMV-SP é release de agência.** O domínio é do conselho, mas o
   rodapé diz "Fonte: Sigma Six Comunicação" e a veterinária citada é de
   hospital privado. Serve assim mesmo, com a procedência registrada na ficha?

4. **Ela entra inteira ou não entra.** A página não tem estrutura de seção,
   então não dá para deixar de fora o parágrafo sobre medicação. São 17
   trechos, mais do que as duas fontes em inglês somadas. Vale?

## Perguntas abertas desta leva

1. **A fonte em inglês.** A melhor fonte para tutor sobre torção gástrica que
   encontramos está em inglês (PDSA). O sistema recebe relatos em português;
   o modelo de busca é multilíngue. Indexar conteúdo em inglês é aceitável
   para você, ou prefere só português mesmo com fonte mais fraca?
2. **A fonte em português.** É uma revisão acadêmica de 2012, e indexaríamos
   só a seção de definição e fatores de risco — o resto é fisiopatologia e
   cirurgia, que ficam de fora de propósito. Serve? Ou é melhor não ter fonte
   em português do que ter essa?
3. **O que ficou de fora.** Em toda fonte, deixamos fora as seções de
   tratamento, cirurgia e dose. A intenção é que o sistema oriente a procurar
   atendimento, nunca a tratar em casa. Concorda com esse corte?

O detalhe de cada fonte — com as citações que sustentam cada julgamento —
está no dossiê do quadro, em [`gastric_dilatation_volvulus.md`](gastric_dilatation_volvulus.md).
