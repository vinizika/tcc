# Rodada 21 — desempenho histórico e etapa atual

Pedido do usuário: explicar mudanças, comparar com outras fases do projeto,
executar verificações pendentes, registrar dados/decisões e entregar o PR.

## Como ler os números

Acurácia estrita é a proporção de classes corretas. Acurácia balanceada é a média
dos recalls por classe. Os conjuntos, classes e modelos mudaram ao longo do
projeto: não se deve construir uma curva única de “acurácia do sistema” misturando
essas medições. Os 18 casos atuais são calibração; não substituem os 122 relatos
independentes ou a futura prova final. Repetir casos não aumenta a independência
da amostra. Latências de máquinas/provedores/camadas distintas também não são
comparações diretas de velocidade.

## Marcos relevantes nas evidências

| Momento e conjunto | Configuração | Resultado documentado | Interpretação |
|---|---|---|---|
| 04/05, 98 listas de sintomas | Prompt antigo sem RAG | Estrita 70,4%; balanceada 53,2% | Conjunto desbalanceado; a acurácia simples escondia dificuldade com casos leves. |
| 04/09, mesmos 98 casos | Prompt novo sem RAG | Estrita 87,8%; balanceada 89,3%; 8/71 E→N | Melhor referência daquela etapa, mas já afinada no conjunto. |
| 04/09, mesmos 98 casos | Prompt novo com RAG antigo | Estrita 67,4%; balanceada 76,3%; 30/71 E→N | Contexto pouco pertinente piorava a decisão. |
| 24–25/09, 122 relatos de autores sem acesso ao mapa | Artigos/MiniLM/llama → fichas/bge-m3/Gemini | 60/122 (49,2%) → 109/122 (89,3%) | Comparação pareada da mudança de arquitetura; emergências perdidas 40→6. |
| 25/09, prova + régua (134 casos) | Fichas/bge-m3/Gemini | 129/134 (96,3%); 2 emergências perdidas e 1 falso alarme | Referência da arquitetura implementada e replicada pela API. Não é o mesmo conjunto da avaliação conversacional. |
| 28/09, 18 casos × 2 | Antes da conversa → PR #16 original | 34/36 (94,4%) → 30/36 (83,3%); recall E 100%→88,9% | Regressão real da integração conversacional na classificação inicial. |
| 02/10, mesma calibração | Primeira correção | 34/36 (94,4%); recall E 18/18 | Recuperou a comparação inicial, mas houve uma oscilação na rechecagem do histórico antigo; motivou nova execução. |
| 02/10, mesma calibração, execução final | Histórico clínico textual e busca separada | 34/36 (94,4%) nas duas versões; recall E 18/18 | Sem regressões pareadas; mediana 3,00 s baseline e 3,05 s corrigida; tokens +12,9%. |

“Emergências perdidas” nas rodadas de autópsia inclui INCERTO. Nos 122 relatos
independentes do Gemini, foram **1 emergência classificada como não emergência e
5 como INCERTO**, totalizando seis. A réplica registrou 88,44% de balanceada e
89,34% de estrita. Isso evita confundir a contagem de falsos não urgentes do runner
com a contagem mais ampla de emergências não reconhecidas na síntese.

Fontes históricas consultadas:

- [Runner de 04/09](../joao/2026-09-04-05-runner-de-avaliacao.md).
- [Comparação das arquiteturas nos mesmos relatos](../joao/2026-09-24-22-arquitetura-proposta-contra-a-de-hoje.md).
- [Réplica pela API, Gemini e Qwen](../joao/2026-09-25-27-atendente-gemini-e-replica.md).
- [Resultado bruto/relatório dos 122 relatos](../../data/evaluation/cited/20260925-041607_r2_gemini_indep_conta1/report.md).
- [Avaliação conversacional original](2026-09-28-17-avaliacao-pre-triagem-conversacional.md).
- [Correções e nova comparação](2026-10-02-20-correcao-regressoes-conversacionais.md).

## O que mudou agora

A arquitetura documental de 25/09 continua: 61 fichas de busca, bge-m3, três fichas
de leitura e Gemini como atendente padrão; tradutor e CoT desligados neste fluxo.
A interface React remodelada já estava na main pelo PR #15. O PR #16 acrescenta
acompanhamento real de INCERTO, formulário, histórico, controles de repetição e
integração do resultado com o encaminhamento. As correções desta rodada separam
a busca do controle da conversa, removem o canal da entrada clínica e fixam o
sentido de cada pergunta e suas opções.

O formulário oferece uma maneira de obter informação que falta; não constitui
um novo classificador nem demonstrou ainda benefício humano. Nos testes, o
sistema antigo também resolve os casos quando recebe gratuitamente os mesmos
fatos. A próxima pesquisa de UX deve medir se tutores conseguem fornecer esses
fatos melhor, com menos esforço e sem respostas induzidas.

## Etapa atual e próximos passos

Temos uma **POC acadêmica integrada em estabilização**: frontend React, cadastro
e histórico persistente, triagem com fontes, acompanhamento da incerteza,
encaminhamento com consentimento e fluxo de clínica. O trabalho atual é corrigir
e medir essa integração, mantendo o PR #16 aberto para revisão da equipe.

1. Fechar a comparação da versão final e revisar o PR #16 com as limitações
   restantes e as duas tentativas preservadas. Atualizar o mesmo PR evita dois
   PRs concorrentes para a mesma funcionalidade; não apagar os commits anteriores.
2. Validar com especialistas a pertinência e a redação do catálogo de perguntas,
   testar respostas livres variadas e transições de quadro. A certificação das
   fichas não equivale à validação deste novo fluxo conversacional.
3. Fazer teste de uso com pessoas, com casos sintéticos: compreensão das opções,
   completude das respostas, tempo, abandonos e indução. Ainda não executado.
4. Preparar a avaliação independente conforme o protocolo da prova 2, sem usá-la
   para ajustar estas correções. Os 330 rótulos foram registrados como validados
   por ASAVET em 26/09; isso não significa que a classificação conversacional
   já tenha sido avaliada nesses casos.
5. Para disponibilização remota, concluir host/HTTPS, configuração de API/CORS,
   persistência, credenciais/cotas, acesso individual e testes na URL escolhida.

CoT e Self-Refine continuam sendo etapas de pesquisa separadas: o CoT está
desligado neste fluxo, e Self-Refine ainda não está implementado. O backlog
registra que a ablação completa vem depois da consolidação do projeto; não foi
substituída pela pequena avaliação de regressão deste PR.

Referências de estado: [ingestão e coleção ativa](../../docs/estado-atual.md),
[operação da POC](../../docs/poc-utilizavel.md),
[registro de validação dos especialistas](../joao/2026-09-26-31-validacao-dos-especialistas.md).

A ampliação das fichas de leitura com conteúdo certificado, a decisão de direitos
das novas fontes e a prova 2 pertencem a rodadas próprias; não foram misturadas
à correção do formulário. Recuperar a calibração atual não demonstra superar os
89,3% nos relatos independentes: isso exigiria medir o mesmo conjunto/configuração.
