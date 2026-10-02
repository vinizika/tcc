# Rodada 22 — revisão geral e prioridades

## Escopo e método

Revisão estática em 02/10/2026 sobre o commit `07bb480`, com árvore limpa no
início. Pedido: examinar o projeto após as alterações, avaliar maturidade e
ordenar próximos passos. Foram inspecionados arquitetura, rotas, autenticação,
persistência, orquestração, frontend, configuração Docker/Nginx/CI, backlog e
evidências históricas/finais. Esta revisão não é pentest, auditoria de cada linha,
nova avaliação clínica, medição de carga ou nova execução de todas as suítes.
Os números de testes abaixo são da validação anterior, identificada por artefatos.
Nenhum código de aplicação, base, gabarito ou pacote congelado foi alterado.

## Avaliação

Nota de julgamento técnico, não métrica experimental: **7,5/10 como POC de TCC**;
**4/10 em prontidão para operação pública**. Há produto integrado demonstrável,
recuperação documentada da regressão e boa rastreabilidade experimental. Faltam
validação independente do fluxo final, estudo com usuários e robustez operacional.
Essas notas avaliam objetivos distintos e não representam probabilidade de acerto.

Pontos fortes: reutilização do pipeline medido, isolamento de entradas clínicas,
catálogo estável de perguntas, opções normais/desconhecidas, consentimento e
snapshot de encaminhamento, checagens de propriedade, sessões revogáveis,
idempotência e controle de concorrência na persistência. A existência dessas
proteções não equivale a uma auditoria completa de segurança.

## Evidência de desempenho disponível

- Calibração pareada de 18 casos, duas repetições: antes 34/36 (94,4%), PR16
  original 30/36 (83,3%), corrigido 34/36 (94,4%). Emergências 18/18 na correção.
- Oito diálogos corretos por canal; 14 pares com entrada clínica e classe iguais,
  incluindo repetições. Não são 14 casos independentes nem garantia de determinismo.
- Mediana inicial 3,00 s antes e 3,05 s corrigida, tokens +12,9%. Houve espera
  máxima de 55,32 s nos turnos finais de formulário, com erros/cotas de provedor.
- Histórico independente: 109/122 (89,3%), com uma emergência classificada como
  não emergência e cinco como INCERTO. Essa medição é da arquitetura anterior
  ao novo fluxo conversacional. Os 96,3% em 134 casos pertencem a outro conjunto.
- Última validação registrada: 340 testes backend, 224 scripts, 10 mock,
  nove navegador e quatro cenários API reais aprovados; build TypeScript/Vite aprovado.

Fontes: [panorama histórico](2026-10-02-21-panorama-historico-e-etapa-atual.md),
[validação final](2026-10-02-validacao-final/README.md),
[auditoria congelada](2026-10-02-correcao-conversacional-v2/final-integrity.json).

## Achados e ordem de execução

| Ordem | Trabalho e fundamento observado | Critério de conclusão proposto |
|---|---|---|
| 1 | Consolidar PR16 e proteção contra regressões. `.github/workflows/tests.yml` só executa Python/sincronizações; não constrói React nem executa Playwright. | CI com Node compatível, build e testes de formulário sem chaves externas; revisão do PR e smoke de clone/build Docker limpo. Integrações pagas em execução separada e explícita. |
| 2 | Validar catálogo e cenários difíceis. As 16 observações fixas limitam cobertura; teste atual não mede generalização nem benefício humano. | Revisão veterinária das perguntas/opções e casos novos de negação, contradição, piora, troca de assunto, respostas vagas e sinais novos no fim de histórico longo. Registrar erros por gravidade. |
| 3 | Fechar protocolo e executar avaliação independente final. Calibração de 18 casos foi usada durante correções. | Separar desenvolvimento/teste da prova 2, congelar antes de ajustes, comparar braços com mesmas informações e medir matriz E/N/I, recall E, E→N e E→I separadamente, abstenção, recuperação, latência e tokens. Qualquer ajuste posterior exige outra prova reservada. |
| 4 | Testar se o formulário ajuda pessoas. Igualdade de resultado quando o teste fornece os mesmos fatos só comprova paridade de integração. | Estudo contrabalanceado com casos sintéticos; medir obtenção de informação correta, opções inadequadas, tempo, turnos, abandono e indução. Revisar teclado, leitor de tela e dispositivos móveis. |
| 5 | Tornar execução recuperável. `api/workspace.py` usa BackgroundTasks; `WorkspaceService.get` libera recuperação de processing antigo após 20 min. | Worker/fila durável ou mecanismo persistente de retomada, limite global de concorrência, prazos e testes de reinício durante análise, cancelamento e retentativa sem duplicação. Medir carga e p50/p95/p99. |
| 6 | Preparar acesso remoto restrito. `/chat/` sem referência pessoal, `/search/` e `/voice/` não exigem identidade; Compose publica backend e Ollama sem bind exclusivo de loopback. Não foi verificada exposição efetiva pela rede/firewall. | Política explícita para endpoints científicos, autenticação/quota/rate limit, configuração de rede e TLS, contas individuais, segredos e chaves próprias. Antes de qualquer exposição, esta prioridade passa a bloqueadora. |
| 7 | Operação e ciclo de dados. `/health/` retorna ok sem testar dependências; localização expira por limpeza nas leituras; não há fluxo de exclusão no workspace inspecionado. | Separar liveness/readiness, monitorar falhas e custos, testar backup/restauração, definir retenção/exclusão e limpeza agendada. Rever tratamento de dados antes de coletar dados pessoais reais. |
| 8 | Reduzir dívida e alinhar documentação. `TutorFlow.tsx` tem 743 linhas e `ClinicDashboard.tsx` 623; existem caminhos legados Supabase e workspace Mongo. | Extrair responsabilidades com testes de comportamento, explicitar caminhos mantidos/depreciados e revisar backlog sem apagar histórico. Corrigir documentação divergente e consolidar comandos reproduzíveis. |

As prioridades 2–4 são o caminho de validação científica; 5–7 são condições de
operação, elevadas para antes da publicação se houver intenção de hospedar agora.
Não recomendo adicionar CoT/Self-Refine, trocar modelo ou ampliar a base na mesma
rodada de estabilização: cada mudança precisa de hipótese e comparação próprias.

## Pontos adicionais concretos

1. `docs/poc-utilizavel.md` descreve até 1.800 caracteres anteriores. O atual
   `followup_service.transcript` inclui todos os relatos; `clinical_query` também
   concatena todos. Há teto de 4.000 caracteres por mensagem e 100 mensagens na
   conversa. Existe proteção de contexto no Ollama, mas isso não comprova
   qualidade da recuperação em histórico longo. Investigar orçamento de contexto,
   custo acumulado e preservação dos fatos recentes antes de escolher truncamento
   ou resumo. Não foi reproduzido um erro clínico de histórico longo nesta revisão.
2. O Nginx não declara `client_max_body_size`, enquanto a API admite áudio de até
   25 MB. Verificar o limite efetivo da imagem e testar upload pelo caminho `/api/`
   do Docker; os testes atuais de navegador não cobrem gravação/transcrição.
   Trata-se de incompatibilidade potencial, não de falha reproduzida nesta rodada.
3. A tabela do backlog ainda apresenta itens como ausência de CI e frontend com
   hostname fixo, embora existam CI e frontend React configurável. Revisar item
   por item com seu histórico; não interpretar a tabela antiga como inventário
   integral das falhas atuais nem marcar tudo resolvido automaticamente.
4. O modo local Qwen configurado não foi medido nesta máquina na rodada final:
   modelo não instalado. Expor a alternativa exige validar sua disponibilidade e
   desempenho, sem extrapolar os resultados Gemini.
5. Notas altas em engenharia não compensam erros de classificação: a decisão
   sobre tolerância a E→N, abstenção e encaminhamento precisa ser definida com
   especialistas e mantida explícita na avaliação final.

## Decisão recomendada

Manter a arquitetura e o frontend atuais, consolidar o PR16 e priorizar a prova
do fluxo completo. Estamos bem para uma POC acadêmica em estabilização, com
evidências mais fortes que uma demonstração visual. Ainda não há evidência para
declarar benefício do formulário com tutores ou prontidão de atendimento público.
