# Pente fino de responsividade no frontend React

**Data:** 09/11/2026 · **Trilho:** B2 (em arquivos do trilho A, a pedido do João) ·
**Rodada:** 33 · **Commits:** este

> Rodada de **interface**, sem tocar o caminho medido (fichas, busca, prompt e
> modelo iguais). Um colega relatou problemas de responsividade na versão
> online. A conferência virou uma varredura automática de 37 telas em 26
> tamanhos e três navegadores, e as correções estão todas em `frontend-react/`.
> Os arquivos são do Vinicius: este commit é só disso, para ele revisar.

## O que foi feito

1. **Conferência manual** no celular (360 × 740), tablet e notebook, pelo
   navegador, com o sistema rodando localmente.
2. **Varredura automática** com o Playwright (Chromium em 26 tamanhos, de
   320 × 568 a 1920 × 1080, incluindo celular deitado e altura reduzida de
   teclado; WebKit em 8; Firefox em 3), sobre 37 estados: entrada, conta
   própria, conversa (boas-vindas, emergência, incerto com pergunta, relato
   longo, analisando, falhou, texto digitado, campo em foco, teclado aberto,
   menu), animais, clínicas com o mapa real e com o mapa bloqueado, revisão do
   envio, encaminhamentos, caso, conta vazia, painel da clínica e abas,
   cadastro de unidade. Cada estado é medido: rolagem horizontal, elemento fora
   da tela, texto cortado, letra abaixo de 11 px, campo abaixo de 16 px em tela
   de toque, alvo de toque abaixo de 36 px, controle sobreposto ou encoberto,
   fração da tela tomada por faixas presas, começo da resposta visível, campo
   em foco visível.
3. **Correções**, todas em `frontend-react/src`.

## O que estava errado

| Problema | Onde aparecia | Correção |
|---|---|---|
| O aviso do mapa ("Carregando mapa…", "Não foi possível carregar o mapa") cobria a **página inteira** e bloqueava a lista de clínicas | até 1100 px de largura; defeito anterior a esta rodada | `.map-wrap` volta a ser o contêiner do aviso; mapa que falhou vira uma faixa baixa |
| A caixa de envio presa embaixo levava junto o seletor de IA e o aviso: **59% da tela** no celular, 98% com o celular deitado | celular | só o campo e os botões ficam presos; o seletor e o aviso rolam com a página |
| Ao chegar a resposta, a tela parava no fim da página: o tutor via o seletor de IA, e não **"Procure atendimento agora"** | celulares pequenos e deitados | a tela para no começo da resposta nova |
| O campo de mensagem mostrava só 2 linhas e o **Enter enviava** no teclado virtual | celular | o campo cresce com o texto (até 6 linhas); em tela de toque o Enter quebra a linha e o envio é pelo botão |
| Campos com letra abaixo de 16 px (o Safari do iPhone dá zoom ao tocar) | celular e tablet | 16 px em tela de toque (`pointer: coarse`) |
| Rolagem horizontal no cadastro com animal e na revisão do envio | **Safari e Firefox**, 320 e 768 px | itens de grade com `min-width: 0` |
| Telas abriam já roladas (a revisão do envio abria no fim do formulário) | todas | cada tela nova começa do topo |
| O menu lateral não fechava com toque fora nem com Esc | celular | fundo escurecido, Esc, botão vira "fechar" |
| Toque num pino do mapa selecionava um cartão 3.000 px abaixo | celular | a página desce até o cartão; atalho para as unidades participantes |
| No painel da clínica, o detalhe do caso abria abaixo da fila inteira | celular | a tela desce até o detalhe |
| Na tela inicial, o seletor de IA e o aviso abriam atrás da caixa de envio | notebooks e celulares pequenos | o que é enfeite ou atalho sai conforme a altura |
| Letras de 9 e 10 px; áreas de toque pequenas; "Sair" inalcançável com o celular deitado | vários | mínimo de 11 px; alvos de 36 px ou mais; menu com rolagem |
| A revisão do envio mostrava "EMERGENCIA" cru | revisão | mesmo rótulo do painel da clínica |

## Resultado esperado

Não houve expectativa escrita antes: a rodada começou como inspeção. O
critério da varredura foi definido antes da última execução: nenhum
apontamento nas medições acima, em nenhum estado, tamanho ou navegador.

## Resultado obtido

| Medida | Antes | Depois |
|---|---|---|
| Altura tomada pela caixa de envio, celular 360 × 740 | 59% | 26% |
| Área para ler a resposta, mesmo celular | ~230 px | 475 px |
| Campos que fazem o iPhone dar zoom | 3 a 9 por tela | 0 |
| Medições da varredura final | — | 1.330, sem falha de execução nem erro de página |
| Apontamentos restantes | — | 1, por escolha (abaixo) |
| Testes de ponta a ponta do repositório | — | 12 de 12 |

O apontamento que fica: com um texto longo digitado, nos dois menores
celulares (320 × 568 e 360 × 640), o cabeçalho e a caixa de envio somam de 52%
a 57% da altura, para mostrar 4 ou 5 linhas do que o tutor escreveu.

## Observações

- A varredura achou o que a conferência manual não tinha achado: o aviso do
  mapa, a rolagem no Safari e no Firefox e a resposta fora de vista.
- O **teclado virtual de um aparelho real** não é emulável. Foi simulada a
  tela encolhendo 300 px com o campo em uso: o campo e o botão de enviar
  seguem visíveis.
- As respostas saem **sem acento** ("veterinario", "coracao"): o modelo
  espelha a ficha de leitura, que vem sem acento do mapa
  ([B-82](../backlog.md#b-82)). Não é defeito de layout.
- A varredura (script, dados de teste e folhas de contato) ficou fora do
  repositório, nas notas do João.

## Deixado para depois

- Conferir o teclado virtual num iPhone e num Android, na versão online
  ([B-83](../backlog.md#b-83)).
- Trazer a varredura para `frontend-react/tests`, se o Vinicius quiser
  mantê-la ([B-83](../backlog.md#b-83)).
- Acentuação das respostas ([B-82](../backlog.md#b-82)).

## Próximo passo

Anexo de documento e histórico do animal entre conversas (rodada seguinte).
