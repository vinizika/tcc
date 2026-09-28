# Lote 1 — resumo

40 relatos (q001–q040), 8 quadros, gravados em `relatos.json`, na ordem dos pedidos. Cadernos de linguagem em `cadernos/L1Q01.md` a `cadernos/L1Q08.md`.

## Conferência automática (Python do ambiente tccv, PYTHONUTF8=1)
- O JSON abre; há 40 relatos com os mesmos ids e na mesma ordem dos pedidos.
- "mas" (palavra inteira, sem distinguir maiúsculas): presente em todos os 18 com `usar_mas=true` e ausente nos 22 com `usar_mas=false`.
- Nenhum relato repete 6 ou mais palavras seguidas de um trecho entre aspas dos cadernos. A primeira rodada achou 4 casos (q001, q003 e q031 ecoavam sínteses minhas do caderno); reescrevi e a segunda rodada passou.
- Checagens extras: todo relato tem de 1 a 6 frases; toda URL de `inspiracao` está no caderno do quadro; nos pedidos com `palpite_permitido=false` não aparece nome de doença; nenhum relato diz "emergência".

## Fontes por quadro (páginas lidas de fato)
| Quadro | Tema | Lidas | Em PT | Com fala de tutor em 1ª pessoa |
|---|---|---|---|---|
| L1Q01 | patas de trás paradas/arrastando | 6 | 3 | 1 (pergunta de tutor no Dial A Vet) |
| L1Q02 | recém-nascido que não mama | 3 | 1 | 1 (Dial A Vet) |
| L1Q03 | convulsão | 5 | 1 | 2 (Dial A Vet) |
| L1Q04 | cinomose nervosa | 4 | 2 | 1 (comentários de leitores no Líder da Matilha) |
| L1Q05 | leptospirose | 3 | 1 | 0 |
| L1Q06 | cistite | 3 | 2 | 0 |
| L1Q07 | tremor sem convulsão | 3 | 2 | 1 (comentários resumidos no blog Cobasi) |
| L1Q08 | tártaro e mau hálito | 3 | 2 | 0 |

Total: 30 páginas lidas, 14 em português. Todos os quadros têm pelo menos 3 fontes e pelo menos 1 em PT.

## Dificuldades
- **Cota de busca esgotada no meio do trabalho.** A ferramenta de pesquisa parou após a busca de leptospirose, com a mensagem de que a sessão usou as 200 buscas permitidas. A cota parece compartilhada com outros trabalhos da sessão, já que este lote fez pouco mais de 20 buscas. Não contornei o limite. Para cistite, tremor e tártaro (e para completar leptospirose), abri diretamente endereços de sites de clínicas e pet shops que eu já conhecia ou cujo padrão de endereço era previsível. Muitos deram 404 (VCA, PDSA, PetMD, AKC, algumas páginas da icatcare, tudosobrecachorros). O resultado são fontes mais "institucionais" nesses três quadros.
- **Pouca fala de tutor em primeira pessoa.** Os sites de pergunta e resposta que costumam ter a voz do tutor recusaram o acesso (JustAnswer e comentários da Petlove: 403). O quizsilo.com, com uma pergunta de tutor sobre "mascar chiclete", virou domínio à venda. O PDF de um relato de caso de leptospirose (periodicorease) não pôde ser lido. Redes sociais e fóruns não foram tentados. Por isso, em leptospirose, cistite e tártaro a linguagem do tutor saiu mais do meu conhecimento do jeito brasileiro de falar ("jururu", "xixi cor de coca", "bafo", "pedra no dente") que de fontes.
- As páginas em inglês foram lidas por um resumo automático. As expressões dos cadernos são sínteses e traduções minhas, não citações.

## Rótulos que merecem nota (não alterei nada)
- **L1Q03 (convulsão), todos EMERGENCIA:** uma crise única e curta, num cão já epiléptico e em tratamento, que volta ao normal logo, costuma ser tratada como consulta urgente, não como atendimento imediato. Para o rótulo valer, pus em cada relato pelo menos um critério de atendimento imediato: primeira crise da vida, duas ou mais no dia, sem recuperação entre elas, ou crise de 4–5 minutos. Um relato de "crise isolada em epiléptico conhecido" teria rótulo discutível.
- **L1Q01 com `tom=gemea` (q005, parecido com artrose):** para não confundir com a artrose, a fase grave foi marcada com início súbito, sem sustentar a traseira, sem reação ao beliscão e sem urinar. Só "anda pior no frio" seria artrose.
- **L1Q06, cistite (q026–q030):** a fronteira com obstrução é o xixi sair ou não. Em todos os relatos há evidência de que sai (pinguinhos, bolinhas de areia, manchas, poça). Escolhi fêmeas nos casos de gato (q027, q029), em que a obstrução é rara. O pedido diz só "gato"; se o avaliador imaginar um gato macho, a leitura muda.
- **q039 (tártaro, gata idosa) e q040 (dente mole):** no dente mole e no sangramento leve, alguns veterinários antecipariam a consulta. Ainda assim nada ali é emergência, e o rótulo "rotina" é defensável.
- Nenhum pedido me pareceu errado para o quadro.
