# Rodada 20 — correção das regressões conversacionais

## Pedido e diagnóstico

O usuário manteve o PR #16 aberto e pediu correção antes de aprová-lo: separar
texto clínico e orquestração, eliminar dependência da origem texto/formulário,
corrigir opções ausentes/perguntas compostas e repetir os casos congelados.

O código enviava `RULES + JSON` tanto ao classificador quanto à busca. O JSON
incluía `origem`, permitindo que o canal influenciasse a decisão. A regra de
progresso também tratava `selected_option` isoladamente: “Não observei” poderia
ocultar um fato novo no complemento apenas no braço formulário. Perguntas e
opções eram texto gerado livremente, e contar pontos de interrogação não impedia
perguntas com dois assuntos ou mudança de significado de uma chave.

## Implementação corrigida

- `ChatPipeline.execute(..., retrieval_question=...)` separa a consulta de busca
  do histórico para classificação. Sem o argumento, o pipeline científico mantém
  o caminho anterior. Embeddings, roteamento e reranking recebem só relatos do tutor.
- O primeiro relato é classificado no formato original, sem envelope conversacional.
  Nos demais turnos, preservam-se perguntas/respostas como contexto, sem `origem`,
  IDs ou opções de controle na entrada clínica. A persistência ainda os conserva.
- O progresso usa o mesmo texto completo nos dois canais; complemento com fatos
  não é descartado porque a opção escolhida foi desconhecimento.
- `FollowupSelection` faz o modelo escolher uma observação pertinente às fichas
  e ao relato. O catálogo v2 fixa a pergunta e suas opções por chave: um assunto,
  alternativas normais/negativas, alterações, outra observação e desconhecimento.
  A chave não pode passar a significar outra pergunta. Se não existir observação
  pertinente no catálogo, mantém INCERTO e encerra o acompanhamento.

O catálogo é uma restrição explícita de cobertura, não um classificador por regras.
Não há classes esperadas ou IDs da avaliação na implementação. As perguntas ainda
dependem da seleção contextual do modelo; a nova rodada avalia essa seleção.

## Primeira tentativa: resultado e falha residual

18 casos provisórios de calibração, duas repetições por versão. A baseline antiga
foi executada novamente, intercalada com a versão corrigida. A coluna PR #16 é
histórica e não deve ser usada para inferir causalidade de diferenças de latência.

| Métrica | Baseline reexecutada | PR #16 original (28/09) | Corrigida (02/10) |
|---|---:|---:|---:|
| Concordância com os rótulos | 34/36 (94,4%) | 30/36 (83,3%) | 34/36 (94,4%) |
| Recall de emergência | 18/18 (100%) | 16/18 (88,9%) | 18/18 (100%) |
| Emergência classificada não emergência | 0 | 0 | 0 |
| Emergência classificada INCERTO | 0 | 2 | 0 |
| Macro-F1 | 0,8667 | 0,7328 | 0,8667 |
| Mediana por turno | 3,23 s | 2,99 s | 3,35 s |
| Média por turno | 4,69 s | 4,32 s | 4,62 s |
| p95 por turno | 13,06 s | 6,23 s | 14,17 s |
| Tokens totais | 36.565 | 49.726 | 41.269 |
| Chamadas lógicas | 36 | 44 | 40 |

Nenhuma classificação inicial mudou entre baseline reexecutada e corrigida.
p11 e p14 voltaram à classe esperada nas duas repetições. p16 permaneceu INCERTO
nas duas versões, embora o rótulo provisório seja NAO_EMERGENCIA. Tokens cresceram
12,9% frente à baseline atual, pois quatro decisões incertas acionaram o planejador.
Latências são de submit/serviços/Mongo/RAG/modelo, sem HTTP/renderização/tempo humano.

## Diálogos e limites

Os oito relatos iniciais permaneceram INCERTO. Todos chegaram a formulário após
uma resposta desconhecida, por repetição da mesma informação faltante. As chaves
e perguntas permaneceram estáveis, sem questão composta ou lacuna de normalidade.

| Braço | Resultado nos oito casos |
|---|---|
| Formulário + fatos congelados | 8/8 esperados: 3 E, 3 N, 2 I |
| Mesmo texto, origem texto livre | 8/8, mesmas classes e fontes do formulário |
| Baseline antiga com os mesmos fatos | 8/8 |
| Controle sem observação nova | 8/8 INCERTO |

Cinco dos seis casos com fatos conhecidos tinham opção predefinida compatível
com parte do fato, contra três na rodada anterior. c05 agora oferece “Comeu a
quantidade habitual”. c02 mantém esforço respiratório em vez de mudar para cor
da mucosa. c03 pergunta pela resposta ao chamado e tem “Não reage ao chamado”.

c06 recebeu uma pergunta única sobre tamanho da barriga, pertinente ao relato
inicial, mas sem resposta nos fatos congelados. Foi respondido honestamente como
“Não observei”, com o relato de vômito leve no complemento. Portanto, 8/8 decisões
esperadas não significa que oito formulários descobriram informação por suas
opções, nem que houve benefício humano demonstrado. A baseline que recebeu os
mesmos fatos também acertou todos.

Três pares extras de c03 com o histórico novo deram EMERGENCIA nos dois canais
em todas as repetições. Porém, reconstruindo o histórico exato de 28/09, houve
uma resposta INCERTO entre seis chamadas. Os seis hashes de prompt foram iguais:
a origem deixou de ser variável de entrada, mas o modelo ainda variou ao ler o
envelope de regras/JSON. Essa falha residual motivou uma segunda tentativa.

A primeira tentativa está congelada com 144 turnos reais e seus resultados
negativos. O [patch de reconstrução](2026-10-02-transcript-tentativa1.patch), aplicado
só em uma cópia da versão final, restaura sua função de histórico. Os demais
arquivos de produção são iguais; o fingerprint permite conferir a reconstrução.

## Segunda tentativa: histórico clínico legível

A função de histórico agora usa relatos anteriores e relato atual em texto,
mantendo as perguntas identificadas como não observações. Isso preserva o
contexto de respostas curtas sem embutir instruções ou JSON no relato clínico.
O primeiro relato continua no formato original. A segunda execução completa
fica em [pacote separado](2026-10-02-correcao-conversacional-v2/protocolo.md), sem
substituir os números da primeira.

Durante a segunda execução, foi detectado um defeito no **runner**, não no produto:
o conjunto de turnos concluídos não incluía a fase. Como `legacy_recheck` foi
executado primeiro, c03/formulário e c03/texto da fase principal eram pulados.
Corrigimos a retomada para considerar fase, caso, braço e repetição, acrescentamos
dois testes e retomamos somente os turnos principais faltantes. O aquecimento
adicional e os logs permanecem nos dados; rechecagens não substituem amostra
principal. Nenhum resultado clínico foi descartado nessa correção do instrumento.

### Resultado da versão final

| Métrica (36 decisões por versão) | Baseline reexecutada | Correção final |
|---|---:|---:|
| Acertos | 34/36 (94,4%) | 34/36 (94,4%) |
| Recall de emergência | 18/18 | 18/18 |
| Macro-F1 | 0,8667 | 0,8667 |
| Regressões pareadas | referência | 0 |
| Mediana por turno | 3,00 s | 3,05 s |
| Média por turno | 3,78 s | 3,67 s |
| p95 | 8,16 s | 6,72 s |
| Máximo | 18,71 s | 22,92 s |
| Tokens reportados | 36.555 | 41.284 (+12,9%) |
| Chamadas lógicas | 36 | 40 |

Os oito diálogos finais acertaram nos três braços com fatos (formulário, mesmo
texto e baseline antiga). Os oito controles sem fatos novos ficaram INCERTO e
`insufficient`. A auditoria das opções repetiu o resultado da primeira tentativa:
normalidade presente, chaves estáveis, cinco presets compatíveis entre seis casos
com fatos conhecidos, com c06 resolvido pelo complemento.

As três repetições adicionais de c03 novo e as três do histórico antigo deram
EMERGENCIA nos dois canais. Ao todo, **14/14 pares** (oito diálogos + três novos +
três antigos) tiveram prompt clínico com hash idêntico e classificação concordante.
Os 14 pares não são 14 casos independentes: seis repetem c03. Isso verifica a
remoção do canal como variável de entrada e a concordância observada; não prova
determinismo absoluto do Gemini em qualquer execução futura.

Foram **145 turnos reais e 177 chamadas lógicas** na versão final, com todos os
turnos concluídos. Somando a tentativa anterior preservada: **289 turnos e 354
chamadas lógicas**, sem contar os testes funcionais posteriores pela API.
Nenhum arquivo de aplicação/dado mudou durante cada execução. Casos, baseline,
fichas, rótulos e coleção mantiveram a identidade verificada nos artefatos.

Houve 17 eventos de espera por 429 e um por 503 na rodada final. Uma resposta
de formulário levou 55,32 s; a mediana desse braço foi 4,37 s, versus 2,72 s no
mesmo texto. Os logs preservam as esperas, inclusive 5+10+20 s em uma chamada.
Não se atribui essa diferença ao canal, cujas entradas são iguais. O máximo e
os backoffs deixam claro que o produto ainda depende da capacidade/cota do provedor.
Tokens reportados não contabilizam necessariamente todos os custos de tentativas
HTTP; não foram convertidos em estimativa monetária.

Conclusão de engenharia: a regressão inicial medida no PR #16 foi recuperada
nesta amostra; o acompanhamento e a concordância entre canais passaram pelos
casos avaliados. Permanecem p16 como INCERTO nas duas versões, o catálogo finito,
a necessidade de validação especializada das perguntas e ausência de estudo de UX.

## Validação final e entrega

340 testes backend, 224 de scripts e dez do protótipo passaram. TypeScript/Vite,
compilação Python e as conferências de fichas/vocabulário passaram. Na API real,
quatro cenários passaram, incluindo emergência imediata, resolução por relato,
formulário desconhecido e emergência revelada só pela opção de ausência de urina.
Os nove testes de navegador passaram em 59,36 s, sem pulados ou instáveis:
quatro contratos com fixtures explícitas e cinco integrações reais, incluindo
encaminhamento com consentimento, snapshot e conversa entre tutor/clínica.

As saídas completas estão no [pacote de validação final](2026-10-02-validacao-final/README.md).
O backend local foi recarregado após verificar zero análises em processamento.
O PR existente [#16](https://github.com/vinizika/tcc/pull/16) recebe as correções e
os registros, preservando o commit original. Não foi necessário abrir PR concorrente.

Não houve avaliação clínica do Qwen local (modelo configurado ausente no ambiente),
ensaio de carga, estudo com pessoas ou avaliação da URL remota. Esses limites estão
explícitos; não são anunciados como testes aprovados. O relatório de etapa e a
comparação histórica estão na [rodada 21](2026-10-02-21-panorama-historico-e-etapa-atual.md).

## Rastreabilidade

- [Protocolo anterior às chamadas](2026-10-02-correcao-conversacional/protocolo.md).
- [Métricas derivadas](2026-10-02-correcao-conversacional/summary.json).
- [Verificações e incidentes de ambiente](2026-10-02-correcao-conversacional/validacao.md).
- [Resultados históricos completos](2026-09-28-17-avaliacao-pre-triagem-conversacional.md).

Fichas, rótulos, casos, baseline e coleção ativa preservados. As duas repetições
não são animais independentes. Este é um conjunto de desenvolvimento com rótulos
provisórios; recuperar a comparação não equivale a demonstrar eficácia clínica
ou benefício de uso do formulário por pessoas.
