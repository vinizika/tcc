# Rodada 23 — comunicação acolhedora e nome VetIA

## Pedido e observação real

Em 02/10, o usuário testou o sistema e pediu menos dureza na linguagem, uma
frase curta de contexto, instruções rápidas e troca do nome para VetIA.
O objetivo é tornar a orientação mais útil sem suavizar a ação urgente.

A conversa foi localizada no Mongo local pelo texto exato, em leitura apenas.
Nenhum dado de conta ou credencial foi copiado. Não havia pet associado.

| Turno | Relato | Resultado persistido |
|---|---|---|
| 08:47 | Minha gata está muito cansada e ela não está conseguindo ficar de pé, está sempre de boca aberta. | INCERTO; pergunta: Como está o esforço para respirar? |
| 08:48 | ela parece que está tendo dificuldade para respirar | EMERGENCIA |

No primeiro turno foram recuperadas as fichas de artrose, paralisia aguda das
patas traseiras e obstrução uretral; nenhuma foi citada pelo modelo. No segundo,
dificuldade respiratória entrou em primeiro e foi citada, seguida de artrose e
paralisia. Isso comprova a diferença de recuperação e de decisão entre os dois
turnos; não isola causalmente o efeito da base, do novo relato e do classificador.
O primeiro INCERTO fica registrado como falha a investigar em rodada clínica
própria, com paráfrases e controles. Não foi corrigido por esta alteração visual.

Os sinais não estavam vazios no banco:

- Primeiro: `muito cansada`, `não está conseguindo ficar de pé`, `boca aberta`.
- Segundo: `nao esta conseguindo ficar de pe`, `sempre de boca aberta`,
  `dificuldade para respirar`.

Logo, os traços vazios colados pelo usuário não provam saída vazia da LLM.
A causa exata da cópia/renderização anterior não foi reproduzida. A nova interface
mostra os sinais em texto visível, fora do bloco recolhido, e remove itens vazios,
somente pontuação e duplicatas exatas de apresentação.

## Decisões de implementação

O prompt atual pede justificativa de até 20 palavras e recomendação de até 15.
Essa é a origem da concisão. Alterá-lo poderia mudar a classificação; nesta
rodada a comunicação adicional foi implementada no React, sem novas chamadas.

`TriageGuidance.tsx` apresenta contexto breve por classe, sinais específicos já
produzidos pelo modelo, recomendação original e dois próximos passos gerais.
Não gera diagnóstico, não escolhe tratamentos, não altera a classe e não infere
sinais novos. A justificativa original fica disponível numa seção expansível.
O botão de atendimento emergencial permanece, antes das perguntas de acompanhamento.

Exemplo da abertura emergencial:

> Entendo sua preocupação. Os sinais descritos precisam de avaliação veterinária
> agora, para que seu animal receba o cuidado necessário.

Os próximos passos orientam organizar o atendimento e, se possível, avisar a
clínica e pedir orientação para transporte sem atrasar a saída. A orientação de
contatar o serviço veterinário para preparar o atendimento tem apoio no material
[Pet First Aid da AVMA, 2025](https://ebusiness.avma.org/files/ProductDownloads/mcm-client-brochures-pet-first-aid-2025.pdf),
consultado nesta rodada. Não foram incorporadas manobras de primeiros socorros.
O texto de interface ainda não foi avaliado em estudo com tutores/especialistas.

INCERTO explicita que falta informação e que isso não significa estar tudo bem.
NÃO EMERGÊNCIA limita a conclusão às informações disponíveis e orienta consulta
e nova avaliação se houver mudança. Recomendações específicas do modelo são
preservadas, para não apagar prazos ou orientações existentes.

O nome visível passou a VetIA na entrada, logotipo `vetia.`, mensagens, painel da
clínica, título da aba e interface Streamlit legada. Identificadores internos
`vetai.*`, nome do banco/pacote e registros históricos foram preservados, evitando
invalidar sessões ou apagar a rastreabilidade das rodadas anteriores.

## Limites de persistência e comparação

É uma apresentação derivada: funciona também em conversas antigas, mas não
reescreve o JSON, o campo `content` ou os encaminhamentos já persistidos. A cópia
compartilhada com a clínica continua contendo a resposta original do modelo.
Não se apresenta a redação fixa como uma nova conclusão clínica da LLM.

Backend, prompts, fichas, coleção e runner não foram modificados. Portanto não
houve reavaliação clínica nem nova porcentagem de acurácia. Não se afirma correção
do primeiro INCERTO ou benefício de compreensão sem medi-los. A mudança não
adiciona tokens/chamadas à inferência; não foi feito benchmark de latência nesta rodada.

## Verificação

- TypeScript (`tsc -b`), build Vite e build Docker do frontend: aprovados.
- Navegador em Vite `localhost:5173`: sete testes aprovados em 4,9 s.
- Três testes novos verificam E/N/I, acolhimento sem perda do aviso emergencial,
  preservação de recomendação/justificativa, sinais vazios/duplicados, marca VetIA
  e ausência de overflow horizontal em 390 px.
- Quatro testes existentes verificam formulário, recarga, envio único, origem e
  complemento nas opções normal, desconhecida, ausência de alimentação e outra.
- Primeira execução: quatro passaram e três falharam por seletor do teste que
  também encontrava o botão homônimo no menu. O seletor foi limitado à mensagem;
  não foi necessário alterar o comportamento do produto para passar.
- Execução contra Docker em `localhost:3000`: sete aprovados em 5,3 s, zero
  falhas, pulados ou flaky; resultado bruto em
  [browser-tests.json](2026-10-02-comunicacao-vetia/browser-tests.json).
  Os testes usam fixtures HTTP; não são uma nova avaliação Gemini/API clínica.

Comando reproduzível (Node 22.12+):

```sh
cd frontend-react
APP_URL=http://localhost:3000 npx playwright test tests/triage-guidance.spec.ts tests/followup.spec.ts
```

Somente o frontend Docker foi reconstruído e recriado para teste local; backend,
Mongo e conversas foram preservados. As mudanças desta rodada permanecem locais
até commit/publicação; a publicação anterior do PR16 não as inclui automaticamente.
