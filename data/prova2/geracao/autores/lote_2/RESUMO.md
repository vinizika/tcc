# Lote 2 — resumo

40 relatos (q041–q080), 8 quadros, 5 personas. Arquivos: `relatos.json`, `cadernos/L2Q01.md` … `cadernos/L2Q08.md`.

Conferência automática (Python do `tccv`, `PYTHONUTF8=1`): o JSON abre, tem 40 relatos com os mesmos ids e na mesma ordem dos pedidos, a regra do "mas" (palavra inteira, sem distinguir maiúsculas) bate nos 40, nenhum relato repete 6 ou mais palavras seguidas de uma citação anotada, nenhum usa a palavra "emergência", as URLs de `inspiracao` estão todas no caderno do quadro e os relatos da persona de Recife estão todos em minúsculas. Um relato (q077) repetia 6 palavras de uma expressão que eu mesmo sintetizei no caderno (não era citação); troquei mesmo assim.

## Fontes por quadro

"Lidas" = página aberta e lida. "Só busca" = conheço só o trecho que apareceu no resultado da busca (a página recusou ou deu 404).

| Quadro | Lidas | em PT | Só busca | Fala de tutor de verdade |
|---|---|---|---|---|
| L2Q01 cebola/alho | 4 | 2 | 3 | comentários de leitores (Walkerville, AU) |
| L2Q02 torção de estômago | 4 | 2 | 2 | comentários de leitores (Perito Animal) |
| L2Q03 trauma grave | 6 | 4 | 1 | comentários de leitores (Perito Animal: atropelamento e queda de janela) |
| L2Q04 parto que não anda | 4 | 4 | 2 | comentários de leitores (Perito Animal) |
| L2Q05 lírio em gato | 5 | 2 | 0 | nenhuma (só páginas de orientação) |
| L2Q06 conjuntivite leve | 4 | 2 | 0 | comentários de leitores (Cobasi, cão e gato) |
| L2Q07 ferida/caroço após briga | 3 | 2 | 0 | comentários de leitores (Cobasi) |
| L2Q08 bebendo e urinando muito | 5 | 3 | 0 | comentários de leitores (Cobasi) |

## Dificuldades

- **O limite de buscas acabou no meio do trabalho.** Durante o quadro L2Q05 a ferramenta avisou que a cota da sessão (200 buscas, ao que parece dividida com os outros lotes) tinha acabado. Não contornei o limite com outros buscadores. Daí em diante (L2Q05 a L2Q08) abri direto endereços que eu já conhecia e usei o mapa do site do blog da Cobasi (`sitemap`) para achar páginas de verdade. Por isso a Cobasi pesa muito nos quadros 5 a 8.
- **Sites que recusaram (HTTP 403):** JustAnswer, as perguntas e respostas da Petco, dvm360, AAHA, Petlove e Petz. Nenhum foi contornado. Várias URLs que tentei adivinhar deram 404. Não acessei fórum nem rede social.
- **Lírio (L2Q05) é o quadro com menos fala de tutor.** Não achei relato de tutor, nem em português nem em inglês. As fontes em PT só dizem que o lírio é tóxico, sem descrever como o tutor percebe o problema. Os relatos desse quadro se apoiam no que as fontes descrevem (pólen no pelo, água do vaso, vômito e baba nas primeiras horas, piora entre 1 e 3 dias) e em como os tutores falam nos outros quadros.
- A fala real de tutor veio quase toda dos comentários de leitores. Esses comentários só dá para ler pelo resumo do WebFetch, então as expressões do caderno são sínteses minhas, não cópia.

## Pedidos com rótulo ou combinação estranha (rótulos não alterados)

- **q046** (torção de estômago, calmo `mas_come_normal`): um cão com torção não "come normal" depois dos sinais, porque não consegue segurar comida. Para a combinação ficar realista, o tutor diz que o cão comeu a ração toda no jantar (antes da crise) e que bebeu água. Quem ler pode achar a frase pouco natural para esse quadro.
- **q080** (bebendo e urinando muito, rótulo NAO_EMERGENCIA 24 h, gêmea de piometra): gata não castrada, um mês depois do cio, bebendo e urinando muito. Vários veterinários iam querer ver essa gata no mesmo dia para descartar infecção no útero. O relato só não fica grave porque não tem secreção, a barriga está normal e ela está ativa. O rótulo é defensável, mas fica na fronteira.
- **L2Q01** (cebola/alho, todos EMERGENCIA): o rótulo só é inequívoco com sinal de anemia (gengiva branca, xixi escuro, cansaço) ou com uma ingestão grande e recente. Um "comeu um pouquinho e está bem" seria discutível. Por isso os cinco relatos trazem sinais do 1º ao 3º dia.
- **q060, q050 e q065** (gêmeas de EMERGENCIA): nelas o tutor acha que é o quadro leve e diz isso em voz alta. Os sinais descritos (força há horas com líquido verde-escuro, ânsia repetida sem sair nada com a barriga dura, gato que comeu folha de lírio) são os do quadro grave.
