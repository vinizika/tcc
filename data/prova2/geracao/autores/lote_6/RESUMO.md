# Lote 6: resumo

35 relatos (q201 a q235), um por pedido e na ordem dos pedidos, em `relatos.json`. Há 7 cadernos de linguagem em `cadernos/`.

## Conferência (Python, `PYTHONUTF8=1`)
- O JSON abre. São 35 relatos com os mesmos ids dos pedidos, na mesma ordem.
- `usar_mas`: os 14 pedidos com `true` contêm "mas" como palavra inteira, e nenhum dos 21 com `false` contém.
- Nenhum relato repete 6 ou mais palavras seguidas de qualquer trecho entre aspas dos cadernos. A conferência pegou 226 trechos: as citações das fontes e também as minhas sínteses. Na primeira rodada, o q221 repetia uma síntese minha; reescrevi e conferi de novo.
- Conferências extras: nenhum relato diz "é emergência" nem "não é emergência". Nos pedidos com `palpite_permitido=false` não aparece nome de doença ou diagnóstico (envenenamento, intoxicação, artrose, otite, queimadura, choque, infecção, abscesso, derrame etc.). Todas as URLs de `inspiracao` estão no caderno do quadro. A persona da estudante não usa letra maiúscula.

## Fontes por quadro
| Quadro | Fontes | Em português | Com fala de tutor |
|---|---|---|---|
| L6Q01 chumbinho/veneno/inseticida | 7 | 5 | comentários no PeritoAnimal e no blog Reino do Bicho; relato de tutora em notícia (Franca); pergunta de tutor no Dial A Vet |
| L6Q02 antipulgas de cão em gato | 7 | 4 (1 de Portugal) | relato de tutor (Se Meu Pet Falasse); comentários no PeritoAnimal; perguntas no Pet Poison Helpline |
| L6Q03 queimadura/choque elétrico | 5 | 3 | comentários no PeritoAnimal (filhote de gato que mordeu fio desencapado; panela de água quente) |
| L6Q04 uva/uva-passa/xilitol | 7 | 1 | um comentário de tutor (Cobasi); o resto são páginas de orientação |
| L6Q05 perda de equilíbrio súbita | 6 | 3 | quase nada; só páginas de orientação |
| L6Q06 artrose no idoso | 6 | 3 | um comentário de tutor (PeritoAnimal) |
| L6Q07 ferida pequena superficial | 4 | 3 | vários comentários no PeritoAnimal (feridas em gato e cão, abscesso) |

## Dificuldades
- **A cota de buscas acabou no começo.** Depois de umas 10 pesquisas, a ferramenta avisou que a sessão tinha chegado ao limite de 200 buscas (limite compartilhado). Não contornei o limite nem usei outro buscador. Segui abrindo páginas diretamente, com endereços que eu conhecia, e navegando pelas categorias dos sites (PeritoAnimal, manual Merck para tutores, PDSA). Por isso as fontes se concentram em poucos sites e falta variedade de fala de tutor em alguns quadros.
- **Sites que recusaram (403):** justanswer.com (perguntas de tutores a veterinários, a melhor fonte de fala de tutor em inglês), cpt.com.br, petz.com.br, petlove.com.br, petco.com e wagwalking.com. O vcahospitals.com respondeu 429 (excesso de requisições) numa das páginas. Muitos endereços que tentei deduzir não existiam (404). Não tentei redes sociais nem fóruns com login.
- **Pouca fala de tutor na internet acessível:**
  - perda de equilíbrio em **gato**: não achei nenhuma página específica sobre gato que abrisse. Usei as páginas sobre o cão e as de otite felina, que descrevem a cabeça torta e os círculos quando a otite chega ao ouvido interno;
  - choque elétrico: só um comentário de tutor;
  - uva/xilitol: só um comentário em português;
  - artrose: os tutores quase não descrevem, tratam como "velhice".

  Nesses quadros, a linguagem dos relatos vem mais do meu conhecimento do jeito brasileiro de falar do que de citações.

## Rótulos que me pareceram discutíveis (não alterei nada)
- **q230** (artrose, gêmea, NAO_EMERGENCIA, parecido com "arrastar as patas de trás"): o detalhe que assusta é perigoso em gato. Gato que arrasta as patas traseiras, mesmo por pouco tempo, faz pensar em trombo na aorta, e muitos veterinários iam querer ver logo. Para manter o rótulo de rotina, escrevi um episódio de rigidez que passa em minutos, com meses de histórico. Mesmo assim, o caso fica perto da fronteira.
- **q216** (uva, calmo, "come normal", EMERGENCIA): o rótulo está certo, porque ter comido uva já pede atendimento imediato, mas o cão ainda não tem sinais graves. A emergência depende de saber que uva é tóxica, não do que o tutor vê. O relato traz o contexto que pesa: cão de 3 kg, quase um cacho, há 40 minutos.
- **q233** (ferida em gato, neutro, 24 h): incluí um leve inchaço quente em volta dos furinhos de mordida, que é o começo típico do caso que pede consulta em 24 h. Não há febre, prostração nem sangramento.
