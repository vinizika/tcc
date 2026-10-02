# Observação de espera e condições da execução

No caso p02, repetição 0, braço atual, o tempo observado foi 84,421 s; a chamada
de classificação ao cliente Gemini consumiu 83,269 s, com 1,128 s de recuperação.
O braço baseline recebeu o mesmo hash de entrada e terminou em 6,804 s.

No caso p04, repetição 0, braço atual: 326,498 s totais, 325,151 s dentro de
`classify`, 1,318 s de recuperação. O turno acabou normalmente, com classe
NÃO EMERGÊNCIA. Não houve erro transformado em classificação neste turno.

Verificações locais durante a espera:

- Configuração efetiva lida sem credenciais: modelo `gemini-3.5-flash-lite`,
  `GEMINI_TIMEOUT_S=60.0`, `GEMINI_MIN_INTERVAL_S=4.0`.
- Cliente do SDK instanciado sem rede e com chave fictícia: `retry_options=None`.
- Fonte instalada de `retry_args(None)`: apenas uma tentativa no SDK.
- O processo da avaliação permaneceu vivo, com a thread principal esperando I/O.
  Uso observado do container: 0,88% CPU e 1,926 GiB/3,825 GiB de memória em uma
  das leituras. Isso não é um benchmark de recursos nem um perfil completo.

Após o término, o log completo permitiu identificar a causa observada: no p04
houve quatro respostas HTTP 503, seguidas de esperas de 20, 40, 80 e 160 segundos
no wrapper `GeminiLLMClient._gerar` do projeto. São 300 segundos de backoff,
além do tempo das requisições. O SDK não é a origem dessas retentativas.
O p02 teve duas respostas 503, com 20 e 40 segundos de espera.

Assim, 60 segundos é o timeout de uma requisição, não um prazo total incluindo
as retentativas da aplicação. Não se trata de uma única requisição HTTP de 325 s.
`attempts=1` é contagem lógica da geração validada e não revela os retries HTTP.
No conjunto completo foram sete eventos 503 e dois eventos 429 registrados.
Os logs eram parcialmente bufferizados durante a execução; por isso a causa
ficou confirmada apenas após o fechamento. Não houve alteração de timeout/modelo.

Os testes de navegador rodaram durante a avaliação congelada, sem gerar novas
classificações. Depois da espera prolongada, a exploração manual também rodou
em paralelo com a parte restante da calibração. Os timestamps estão nos arquivos
brutos. Portanto as diferenças de latência entre rodadas NÃO são estimativas
causais do efeito da mudança visual. A espera de p04 precedeu essa exploração.

Decisão: preservar os outliers; não excluir para melhorar média/p95. Recomenda-se
medir e implementar um prazo total para a tarefa, além de limites por requisição,
em uma mudança própria com testes de cancelamento/retentativa. Nada disso foi
implementado ou declarado resolvido nesta rodada de avaliação.
