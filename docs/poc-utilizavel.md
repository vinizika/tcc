# POC utilizável — operação e limites

Esta entrega conecta interface, persistência, RAG e Google. É uma aplicação
acadêmica executável localmente, **não uma autorização para atendimento
veterinário público nem uma implantação em produção na internet**.

## Iniciar

Na raiz do repositório:

```sh
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:3b
```

Abra <http://localhost:3000>. Para desenvolvimento frontend fora do Docker,
use Node 22.12+; o Node 18 da máquina não é compatível com Vite/Playwright atuais.

### Configuração no .env ignorado pelo Git

```dotenv
WORKFLOW_MODE=poc
AUTH_PROVIDER=local
POC_QUICK_LOGIN_ENABLED=true
MAPS_PROVIDER=google
MAPS_KEY_KIND=demo
GOOGLE_MAPS_SERVER_KEY=preencher-localmente
GOOGLE_MAPS_WEB_KEY=preencher-localmente
POC_RAG_PATH=/app/chroma_db
POC_RAG_COLLECTION=nome-da-colecao-existente-validada
```

Não copie uma chave para Git, Markdown, screenshots ou evidências.
A chave web é pública por natureza, entregue por `GET /auth/config`; a chave
de servidor não é devolvida nem usada como argumento de build.

## Identidade e dados

Os dois acessos rápidos são **contas compartilhadas acadêmicas**, habilitadas
explicitamente no servidor. Sessões opacas expiram em 24 h, são revogadas no
logout e o Mongo guarda apenas seu hash. Não coloque dados pessoais nessas contas.

“Conta própria” cria identidade persistida, senha derivada com scrypt e sessão
revogável. No navegador, o token fica em sessionStorage (isolado por aba).
O provedor local não oferece recuperação de senha, confirmação de e-mail ou MFA;
não é indicado para exposição pública sem endurecimento operacional.

Coleções Mongo:

- `poc_accounts`, `poc_sessions`: identidade local e sessões;
- `poc_pets`, `poc_conversations`: workspace privado por usuário;
- `workflow_clinics`, `referrals`: unidades, encaminhamentos, mensagens e eventos.

As rotas legadas `/tutors` e `/pets` continuam usando Supabase. Os registros
antigos não são migrados ou mesclados automaticamente com o workspace novo.
Supabase permanece opção de autenticação com `AUTH_PROVIDER=supabase`.
Trocar o provedor não migra contas locais.

Clínicas próprias começam pendentes. Informar um Google Place ID não prova
titularidade. Somente após conferência institucional manual o administrador
deve vincular conta/unidade e liberar recebimento; nunca use a chave pública
ou metadados enviados pelo cliente para conceder verificação.

## Chat e RAG

`POST /workspace/conversations/{id}/messages` persiste o relato e responde
202. O navegador consulta o estado a cada 2,5 s; o backend executa a análise em
background. Isso remove o acoplamento entre o tempo da LLM e o timeout HTTP.

Pipeline científico reaproveitado, sem mudanças de taxonomia/prompts: retrieval
ligado, consulta original, rewriting/multi-query/HyDE desligados apenas neste
workspace. O adaptador usa uma coleção configurada explicitamente e verifica
integridade antes de consultá-la. Não altera o ponteiro ativo da pesquisa.
Coleções em revisão continuam **base experimental**, não conhecimento validado.

Nova mensagem preserva o relato atual integralmente e acrescenta um trecho
limitado de até 1.800 caracteres dos relatos anteriores; respostas
anteriores do modelo não voltam ao prompt como fatos. Não é memória clínica
ilimitada nem um novo agente médico. RAG não garante segurança/precisão.

A execução é BackgroundTasks no processo web, não fila durável distribuída.
O texto sobrevive a reinícios, mas uma geração interrompida não é retomada
automaticamente; após 20 min ela pode ser tentada novamente. Para operação
multiusuário pública são necessários worker/fila, limite de concorrência,
rate limiting, observabilidade e uma política de recuperação.

## Google Maps real

Busca por Places API (New), texto/CEP/referência por Text Search, fallback
Geocoding v4. O mapa usa Maps JavaScript; deslocamento usa Routes Compute Routes
quando disponível. Não há fallback silencioso para locais fictícios.

A [Demo Key do Google](https://developers.google.com/maps/demo-key) permite
esses testes, mas possui cotas e restrições: não inclui avaliações/fotos de
usuários e pode pausar até o dia seguinte. As solicitações no modo demo não
pedem esses campos. Não é uma credencial de produção. Para publicação, usar
projeto próprio com billing, restrições por API/origem e chaves separadas.

“Próximas” significa as até 20 primeiras opções retornadas no raio de 10 km,
ordenadas por distância em linha reta. Não significa 20 emergências 24 h,
qualidade certificada ou disponibilidade. Horários podem estar ausentes ou
desatualizados. A interface orienta confirmar por telefone.

Unidades fictícias ficam em seção separada para teste do encaminhamento.
Um estabelecimento encontrado no Google não recebe acesso ao painel por isso:
precisa ser participante verificado, vinculado a uma conta institucional.

## Compartilhamento e deslocamento

Resumo revisado + relato original + snapshot automático são enviados só após
consentimento. Conversa completa é opt-in separado e cópia do instante do envio;
mensagens futuras não são compartilhadas silenciosamente.
O snapshot automático vem da conversa persistida, não do valor enviado pelo navegador.

Após aceitação, apenas o tutor confirma “Estou a caminho”. Localização é opt-in,
capturada enquanto a página estiver aberta; a clínica não vê posição desatualizada
como tempo real. A estimativa vem do Google Routes, sem trânsito ao vivo. Em erro,
falta de permissão ou unidade acadêmica, fica indisponível — nunca inventada.
Chegada, conclusão, recusa e cancelamento removem a posição. Posições sem
atualização há 120 s são ocultadas pela API e removidas oportunisticamente
nas leituras do repositório; sem tráfego, não há um cron de limpeza.

### Verificar uma unidade após conferência manual

Não execute só para desbloquear dados. Confira instituição/responsável por canal
independente e registre a evidência em local restrito. Então:

```sh
docker compose exec backend python -m app.scripts.verify_clinic \
  --clinic-id unit-ID-DA-CONTA --reviewer ADMINISTRADOR \
  --evidence-reference REGISTRO-RESTRITO \
  --confirm-ownership-checked
```

O comando valida o vínculo, registra responsável/data/referência e libera
conta e unidade. Não imprime documento pessoal. Faça login novamente.

## Testes automatizados

```sh
docker compose exec backend pip install -r requirements-dev.txt
docker compose exec backend python -m pytest
cd frontend-react
npm ci
npx playwright install chromium
npx playwright test
```

Os testes unitários isolam Mongo/Google/LLM. Os testes Playwright usam a
aplicação local de verdade e criam dados identificados como teste: não apontar
para uma implantação com dados pessoais. O quarto teste requer
`LIVE_RAG_CONVERSATION_ID` de uma conversa concluída do acesso tutor acadêmico.
Sem essa variável ele é explicitamente ignorado, não substituído por mock.

## Teste manual

1. Abra tutor e clínica em abas separadas; use os acessos rápidos.
2. No tutor, cadastre um gato/cachorro; associe à conversa ou deixe para depois.
3. Envie relato fictício, recarregue e confira histórico/estado de análise.
4. Abra atendimento, busque endereço e confira mapa/lista Google.
5. Para simular entrega, escolha a unidade **acadêmica**, revise e autorize.
6. Na clínica, abra o caso, confira resumo/conversa autorizada e aceite.
7. No tutor, confirme deslocamento e envie mensagem. No painel, confira atualização.
8. Revogue localização, registre chegada e conclua. Confira persistência após recarga.
9. Crie contas próprias para testar isolamento; uma clínica própria continua
   bloqueada até verificação, e contas próprias não enviam para unidades acadêmicas.

## Antes de publicar

Exigem decisão/validação do grupo: hospedagem e TLS, domínio, Google billing,
gestão de segredos, backups/restauração, retenção/exclusão de dados, autenticação
endurecida, proteção de abuso, monitoramento, consentimentos/revisão LGPD,
validação clínica e avaliação IHC com participantes. Nenhum desses resultados é
presumido nesta entrega.
