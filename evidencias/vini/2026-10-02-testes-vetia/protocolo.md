# Protocolo congelado antes da rodada VetIA

Rodada de 02/10/2026, posterior à mudança de apresentação e marca. Referência
de código: HEAD 07bb480 mais alterações locais registradas em snapshot.json.

1. Reexecutar verificações Python, build TypeScript/Vite e sincronização da base.
2. Reexecutar os 18 casos congelados, duas repetições em cada braço (72 decisões),
   com baseline histórico e workspace atual, no mesmo processo/ambiente e ordem
   alternada. Aquecimento excluído. Banco separado: tcc_eval_vetia_20261002.
3. Repetir os quatro cenários reais de API da validação anterior.
4. Exploração separada: três repetições do relato manual seguido da segunda
   mensagem exata; três do relato respiratório explícito; três de controle sem
   sinais respiratórios. Não misturar exploração com a calibração ou atribuir
   rótulos clínicos certificados aos casos novos.
5. Executar os 12 testes de navegador: quatro de formulário, três de apresentação
   e cinco fluxos reais já existentes. Usar uma conversa real concluída no teste
   de encaminhamento. Não substituir falha real por fixture.
6. Comparar com PR16 original, correção v2 e validação anterior: classes, recall E,
   abstenção, erros, tokens, latência, fontes e hashes de entrada. Diferenças entre
   execuções sem alteração de backend não provam efeito causal da interface.

Preservar artefatos históricos e todos os resultados negativos. Se houver falha
de infraestrutura ou cota, registrar resultados parciais e motivo. Esta rodada
não altera classificador, ficha, gabarito ou conjunto independente para melhorar
métricas. Não há teste com usuários humanos ou validação clínica nova.

Os próximos passos fixos da interface não consomem tokens nem alteram prompts;
os testes de apresentação avaliam comportamento/renderização, não compreensão
humana, utilidade clínica ou acurácia. O banco compartilhado de demonstração só
receberá casos sintéticos dos smokes autorizados.
