# Segunda etapa — encaminhamento integrado entre tutor e clínica

**Data:** 24/09/2026 · **Trilho:** produto integrado / interface

## O que será feito

Substituir o frontend principal por React + TypeScript, preservando o
Streamlit como interface legada durante a transição, e integrar ao FastAPI o
fluxo posterior à pré-triagem: descoberta de clínicas, revisão e consentimento,
encaminhamento idempotente, estados auditáveis, dashboard e conversa humana.

O modo demonstrativo terá contas e clínicas inequivocamente fictícias. O modo
real exigirá Supabase Auth, clínica verificada e Google Maps configurado; não
deve cair silenciosamente para dados de demonstração.

## Por quê

O protótipo em `mock/` prova o fluxo visual, mas não chama o backend real e não
persiste encaminhamentos. O Streamlit principal, por sua vez, mostra apenas o
texto renderizado de `/chat/`, não a triagem estruturada, e o cadastro atual por
`tutor_id` não autentica ninguém. A segunda etapa exige estado persistente,
autorização por recurso, mapa sincronizado, áreas distintas e polling — um
conjunto mais adequado a uma aplicação React.

## Decisões desta rodada

| Decisão | Motivo |
|---|---|
| FastAPI continua sendo a fonte das regras | Isola a interface do RAG, dos prompts e do texto de `answer` |
| Snapshot versionado da triagem no encaminhamento | Mudanças futuras no modelo não alteram o que foi compartilhado |
| MongoDB já existente guarda encaminhamentos, eventos e mensagens | São documentos agregados e históricos; evita duplicar esses dados no Supabase |
| Supabase Auth e perfis no modo real | Substitui o uso inseguro de IDs como identidade e permite RLS reproduzível |
| Tokens e dados locais apenas no modo `demo` explicitamente configurado | Execução local sem credenciais, sem fingir integração externa |
| Busca Google não é persistida como catálogo | Dados externos são exibidos sob demanda; só clínicas participantes verificadas recebem casos |
| Polling inicial no dashboard/chat | Menor complexidade operacional; intervalo e limitações serão documentados |

## Resultado esperado

1. O fluxo emergência → clínica participante → consentimento → dashboard →
   resposta → chat funciona de ponta a ponta no modo demonstrativo.
2. Clínica pública não participante oferece somente telefone e rota.
3. `INCERTO` e `NAO_EMERGENCIA` nunca criam encaminhamento automaticamente.
4. Negação de localização e indisponibilidade do Google têm estados úteis.
5. Tutor e clínica não conseguem acessar recursos de terceiros; clínica
   pendente não acessa o dashboard.
6. Repetir o envio com a mesma chave não duplica o caso.
7. Atualizar a página recupera encaminhamento e mensagens do backend.

## Resultado obtido

O frontend principal passou a ser React + TypeScript, servido por Nginx no
Compose, e o Streamlit ficou disponível no perfil `legacy`. O fluxo integrado
entrega pré-triagem estruturada, busca de clínicas em mapa/lista, revisão,
consentimento, envio idempotente, histórico de estados, dashboard por unidade e
chat humano persistido no MongoDB.

Foram implementados dois modos separados: `demo`, com personas e clínicas
explicitamente fictícias e sem chamadas Google; e `real`, com Supabase Auth,
perfis, RLS, cadastro institucional pendente e Places/Geocoding sem fallback
silencioso. Tutor, pet, conversa e encaminhamento são filtrados pelo titular;
clínicas só leem casos destinados ao próprio `clinic_id`, e contas pendentes
não abrem o painel.

Validação executada em 24/09/2026:

- suíte completa do backend no container: **234 testes aprovados**;
- TypeScript e build de produção: **Vite 7.3.6, 35 módulos, concluído**;
- `npm audit --omit=dev --audit-level=high`: **0 vulnerabilidades**;
- `docker compose config --quiet` e reconstrução da imagem React: aprovados;
- smoke test local: `/health/`, página Nginx, login demo e busca retornaram;
  um caso fictício foi criado como `delivered` e apareceu no dashboard da
  clínica correta com `awaiting_review=1`.

Como checagem adicional fora do escopo do frontend/backend integrado,
`scripts/tests` teve 161 aprovações e 26 falhas de ambiente concentradas em
`test_capturar_fonte.py`: o host não possui a dependência opcional
`trafilatura`. Nenhuma dessas falhas percorre os módulos alterados nesta rodada.

O resultado confirma os sete comportamentos esperados por testes automatizados
e inspeção integrada. Não comprova a integração externa real, porque nenhuma
credencial Google/Supabase de produção foi usada nesta rodada. Também seguem
como limites: verificação de clínica manual, polling em vez de push, ausência
de SLA/escalonamento automático e voz ainda no frontend legado.

### Correção durante o teste manual — timeout do proxy

No primeiro teste de pré-triagem pela interface, o Nginx respondeu HTTP 504
após 60 segundos, embora o FastAPI e o Ollama continuassem processando. Os logs
registraram `upstream timed out while reading response header`; reescrita e
multi-query em CPU já haviam consumido mais de um minuto. O `proxy_read_timeout`
foi alinhado ao timeout de 600 segundos do cliente Ollama, com margem de 60
segundos. A correção não reduz o tempo do modelo, mas impede que o proxy descarte
uma resposta ainda válida.

## Decisões de IHC a verificar na implementação

- linguagem cotidiana, ação principal evidente e poucas etapas em crise;
- localização sem cadastro obrigatório e alternativa manual;
- mapa acompanhado de lista, sem confundir proximidade com disponibilidade;
- revisão do relato e do conteúdo automático antes de compartilhar;
- consentimento explícito e estados que não prometem confirmação inexistente;
- distinção visual entre dado do tutor, resultado automático e ação humana;
- hipóteses H03, H05, H08–H11 do repositório de IHC permanecem hipóteses.
