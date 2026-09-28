# Lote 5 — resumo

40 relatos (q161–q200) em `relatos.json`, na ordem dos pedidos. Cadernos em `cadernos/L5Q01.md` … `L5Q08.md`.

Conferência (Python, `PYTHONUTF8=1`): o JSON abre; 40 relatos com os mesmos ids e a mesma ordem dos pedidos; os 16 com `usar_mas=true` contêm "mas" e os 24 com `usar_mas=false` não contêm; nenhum relato repete 6 ou mais palavras seguidas das 41 citações anotadas nos cadernos. Checagens extras: nenhum relato diz "é emergência"/"não é emergência", e nos pedidos com `palpite_permitido=false` não aparece nome de doença (insolação, parvo, panleucopenia, cio, piometra, tosse dos canis, doença do carrapato, intoxicação, obstrução, virose etc.).

## Fontes por quadro

| Quadro | Tema | Fontes | Em PT | Observação |
|---|---|---|---|---|
| L5Q01 | insolação (cão) | 10 | 3 | 5 são títulos de perguntas de tutores no JustAnswer: só o título, vindo da busca (a página recusou com 403) |
| L5Q02 | parvovirose / panleucopenia | 5 | 5 | inclui a queixa da tutora num relato de caso de panleucopenia |
| L5Q03 | engasgo | 4 | 3 | |
| L5Q04 | objeto engolido preso | 4 | 3 | |
| L5Q05 | mordeu ou lambeu sapo | 5 | 3 | as fontes em PT falam pouco de sapo (Cobasi cita de passagem; a Wikipédia PT fala do veneno sem descrever sinais) |
| L5Q06 | cio normal (e piometra, a gêmea) | 5 | 3 | |
| L5Q07 | tosse dos canis leve | 4 | 3 | |
| L5Q08 | carrapatos, animal bem | 3 | 3 | |

## Dificuldades

- **O limite de buscas da sessão acabou logo no começo.** A ferramenta de busca parou depois das primeiras consultas (o limite de 200 é por sessão, e os lotes provavelmente dividem essa conta). Só os quadros L5Q01 e L5Q02 tiveram buscas de verdade. Do L5Q03 ao L5Q08 abri direto páginas cujo endereço eu conhecia e usei a busca interna do blog da Cobasi. Por isso a Cobasi aparece muito nos quadros 3 a 8, e a variedade de fontes ficou menor que o ideal. Não usei buscador externo pelo WebFetch para contornar o limite.
- **Quase não há fala de tutor acessível.** As páginas de perguntas e respostas e os fóruns recusaram ou não abriram:
  - JustAnswer: 403, aproveitei só os títulos das perguntas;
  - Vets Now, Wag!, fórum Positively, blog Petz e Petlove: 403;
  - Reddit e Pets StackExchange: a ferramenta não consegue abrir;
  - petforums.co.uk: redireciona para um pedágio de robôs (TollBit). Pulei, sem contornar.
  - Nos artigos do Tudo Sobre Cachorros, os comentários de leitores não aparecem no texto que a ferramenta recebe.

  Vários endereços que tentei deram 404 (páginas da VCA sobre sapo e tosse dos canis, AKC, PetMD, PDSA, Cornell, Kitten Lady). Na prática, o vocabulário de tutor dos cadernos é uma síntese minha: parte do jeito como as páginas de clínicas e hospitais descrevem o que o dono vê, parte dos títulos do JustAnswer e da queixa registrada no relato de caso, e o resto é conhecimento próprio de como tutores brasileiros falam.
- Quadros com menos material em português: sapo (L5Q05) e objeto linear engolido por gato (L5Q04).

## Pedidos em que o rótulo ou a combinação pareceram estranhos (não alterei nada)

- **Persona "muito aflita com tudo" com tom calmo** (q161, q166, q171, q176, q181): as duas coisas brigam. Resolvi mantendo as interjeições religiosas ("Deus abençoe", "Nossa Senhora") num relato contado com calma, sem pânico.
- **q161, insolação com `mas_come_normal`:** um cão em insolação grave raramente come. Usei "bebeu a vasilha toda e aceitou um pedacinho de pão", que é plausível mas fica no limite.
- **q182, sapo com `mas_come_normal`:** comer logo depois de morder sapo só é verossímil nos primeiros minutos. Escrevi nessa janela (30 min).
- **Cio com `palpite_permitido=false`** (q186, q187, q188, q189): quase todo tutor diz simplesmente "entrou no cio". Proibir a palavra obriga a um tutor que não reconhece o cio (q186 e q187: "sempre tive macho") ou que descreve sem dar nome (q188, q189). O caso mais artificial é o q188: uma protetora com vários bichos que não diz "cio".
- **q193, protetora com tosse dos canis e `palpite_permitido=false`:** a mesma artificialidade, em grau menor.
- **q167 e q169, panleucopenia em gato:** a diarreia com sangue é menos constante no gato do que na parvovirose do cão. Mantive o sangue porque o quadro pedido fala dele, e reforcei os sinais típicos do gato: ficar em cima da vasilha de água sem beber, esconder-se e ficar mole.
- **q195, tosse dos canis gêmea com palpite permitido:** o tutor dizer "tosse dos canis" é natural para um programador que pesquisa, mas praticamente entrega o quadro.
