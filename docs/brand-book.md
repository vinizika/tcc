# VetAI — sistema de marca e interface da POC

Versão 1 · 24/09/2026 · proposta aplicada, ainda não validada com participantes.

## Intenção

Clareza quando o tutor está preocupado. Acolhimento sem infantilizar; competência
sem parecer um diagnóstico. VetAI mantém o nome já usado pelo projeto. Esta
proposta não declara registro de marca nem aprovação clínica.

**Promessa de interface:** “O próximo passo, com mais clareza.”

**Personalidade:** calma, próxima, objetiva, transparente sobre limites.
Nunca usar “seu animal está seguro”, “diagnóstico confirmado” ou “vaga garantida”.
Preferir “orientação inicial”, “o tutor confirmou que está a caminho” e
“ligue para confirmar disponibilidade”.

## Referências e decisões

| Referência | O que observamos | Como foi aplicado |
| --- | --- | --- |
| [Bond Vet](https://bondvet.com/) | Atendimento primário/urgente e acesso a registros com chamadas claras | Uma ação principal por etapa; área de cuidado acolhedora, sem copiar marca ou composição |
| [NHS 111 online](https://111.nhs.uk/) | Orientação sobre próximos passos, limites do serviço e localização | Pré-triagem não apresentada como diagnóstico; localização solicitada no momento de buscar atendimento |
| [Google Maps](https://developers.google.com/maps/documentation/javascript/overview) | Relação entre mapa, local e informação verificável | Lista numerada vinculada a marcadores, origem explícita e rota externa |
| [IHC do grupo](https://github.com/Ryu2525/INTERFACE-HUMANO-COMPUTADOR) | Personas, jornada, concorrência e rastreabilidade | Texto simples, entrada progressiva, revisão de voz, consentimento e recuperação de erro |

O estudo de IHC foi consultado somente para leitura. Seu README ainda marca
protótipos/pesquisa pendentes; não afirmamos que esta interface tenha sido
validada. H03, H05 e H08–H11 continuam hipóteses, não resultados de usabilidade.

## Marca

Logotipo tipográfico “vetai.” acompanhado de uma pata em um quadrado arredondado.
A pata indica o contexto animal; não usar cruz médica, selo ou escudo como
certificação. O ponto ocre dá calor, sem competir com alertas.

- Componente de referência: `frontend-react/src/components/ui.tsx → Brand`.
- Área livre mínima: metade da altura do símbolo em todos os lados.
- Tamanho mínimo recomendado: símbolo 24 px; conjunto 100 px de largura.
- Usar verde sobre fundo claro ou branco sobre verde. Não distorcer, colocar
  sobre fotografias ruidosas nem usar vermelho como cor institucional.
- Ilustração de entrada: formas orgânicas, órbitas e ícones SVG próprios em
  código; sem fotografias de animais em sofrimento, mascotes ou imagens geradas.

## Cores

| Token / uso | Cor | Intenção |
| --- | --- | --- |
| `--green` / ação primária | #255F4C | Confiança e cuidado |
| `--green-dark` / interação | #194A39 | Hover de ações |
| `--ink` / texto principal | #233D38 | Leitura confortável |
| `--muted` / apoio | #667570 | Hierarquia sem apagar informação |
| Fundo | #FAFBF8 | Respiro |
| Superfície | #FFFFFF | Agrupamento de conteúdo |
| `--sage` / contexto suave | #EDF3EC | Acolhimento |
| `--line` / contorno | #DFE6DF | Separação discreta |
| Emergência | #A0452F sobre #FFF2EB | Prioridade, sempre com texto |
| Incerteza | #8B691D sobre #FAF5E8 | Informação incompleta |
| Foco | #B58028 | Navegação por teclado visível |

Cor nunca é o único indicador: estados possuem rótulo e alerta possui próxima
ação. Texto principal/auxiliar deve alcançar contraste WCAG AA sobre o fundo
efetivo; não aplicar opacidade nos textos para criar uma nova hierarquia.

## Tipografia

**Manrope Variable:** títulos e marca; formas abertas, presença contemporânea.
**DM Sans Variable:** corpo, formulários, mensagens e navegação; leitura neutra.

Fontes hospedadas no próprio bundle, sem chamada a Google Fonts em runtime.
Ambas usam SIL Open Font License 1.1:
[Manrope](https://github.com/google/fonts/blob/main/ofl/manrope/OFL.txt),
[DM Sans](https://github.com/google/fonts/blob/main/ofl/dmsans/OFL.txt).
Licenças distribuídas em `frontend-react/public/licenses/`.

Escala: título de entrada 36–60 px; páginas 28–43 px; seções 18–23 px;
corpo 14–16 px; apoio 12–13 px. Textos muito pequenos ficam restritos a
metadados, nunca à orientação clínica principal.

## Espaçamento, componentes e movimento

- Base de 4 px; respiros principais 16/24/32/40 px.
- Conteúdo do chat centralizado com largura limitada; nenhuma coluna densa
  de informações concorrentes ao relato.
- Superfícies com bordas de 1 px e raios de 12–20 px; sombras discretas.
- Botões com alvo mínimo de 44 px nas ações principais.
- Hover/foco de 180 ms, entrada de página de 250 ms e deslocamento de até 5 px.
- `prefers-reduced-motion` desliga transições e animações. Nenhuma animação
  pode atrasar uma ação de emergência.
- Sem carrossel, autoplay ou splash screen obrigatório.

## Fluxos e rastreabilidade de UX

| Necessidade do estudo | Solução implementada | Verificação necessária |
| --- | --- | --- |
| Tutor sob estresse | Login curto; acesso tutor abre diretamente o chat | Teste de tarefa e tempo até o relato |
| Dados incompletos | Animal opcional; só nome/espécie obrigatórios; idade/peso/histórico opcionais | Entendimento do cadastro |
| Baixa familiaridade com termos | Linguagem simples e exemplos de relato | Entrevistas com P01/P02 |
| Erros na entrada por voz | Transcrição entra como rascunho editável, nunca é enviada automaticamente | Áudio real e acessibilidade |
| Falha/lentidão do sistema | Relato persistido, estado de análise consultável, nova tentativa | Falha de rede e reinício |
| Orientação acionável | Emergência com CTA de atendimento; mapa também disponível durante análise | Compreensão sem diagnóstico |
| Localização negada | CEP, endereço e ponto de referência | Permissão negada no celular |
| Confiança e privacidade | Revisão do envio; consentimentos separados para resumo, conversa e localização | Leitura/entendimento do consentimento |
| Continuidade com profissional | Fila, resumo, cópia autorizada, estados e chat humano separados | Simulação tutor–clínica |
| Não inventar disponibilidade | Encontrada no Google ≠ participante; envio ≠ aceitação ≠ chegada | Teste de compreensão dos estados |

O fluxo profissional P03 continua uma hipótese de projeto. “Atualização a cada
8 segundos” significa polling, não comunicação em tempo real por WebSocket.

## Responsividade e acessibilidade

Desktop: navegação lateral fixa, chat central, mapa/lista lado a lado.
Celular: navegação recolhida por botão, mapa antes da lista, painéis empilhados.
Formulários possuem labels; erros usam `role=alert`; processamento usa
`role=status`; ícones decorativos são ocultos de leitores de tela.

Pendências de validação: auditoria completa WCAG, leitor de tela, zoom 200%,
dispositivos móveis físicos, testes com tutores e profissionais. Esses itens
não são substituídos por screenshots ou testes automatizados.
