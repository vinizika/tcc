# Deploy na internet

**Data:** 19/10/2026 · **Trilho:** B2 · **Rodada:** 32 ·
**Commits:** este e o anterior (troca de chave do Gemini)

> Rodada de **infraestrutura**, sem mudar o caminho medido: mesmas fichas,
> mesma busca, mesmo prompt, mesmo modelo. O sistema completo — tela React,
> login, triagem por texto e voz, clínicas e encaminhamento — passa a ficar
> acessível em <https://vetia.chilecentral.cloudapp.azure.com>, para a banca
> e testadores convidados, numa máquina que liga e desliga para não gastar
> crédito. Como ligar e desligar: [`deploy/README.md`](../../deploy/README.md#ligar-e-desligar-a-hospedagem).

## O que foi feito

1. **Onde hospedar.** O backend precisa de ~2,5 GB de RAM só para o bge-m3 e
   de respostas de até minutos, o que tira do jogo as plataformas serverless
   (Vercel, Netlify: limite de tempo e memória por requisição). Ficou uma
   máquina virtual no **Azure for Students** (crédito anual, sem cartão), na
   região **Chile Central**: das cinco regiões que a assinatura de estudante
   permite, é a única com a série B x86 (B2as_v2, 2 vCPU, 8 GB); no Brazil
   South só há a série D, ~40% mais cara.
2. **A pilha de produção** (`docker-compose.prod.yml` + `deploy/`): Caddy na
   frente com HTTPS automático (Let's Encrypt), o Nginx do frontend com limites
   por IP, backend sem `--reload`, Mongo e backend sem porta publicada, Ollama
   fora (sem GPU). A configuração é a da POC local
   ([`docs/poc-utilizavel.md`](../../docs/poc-utilizavel.md)): contas próprias e
   acessos rápidos de tutor e clínica, Gemini sem troca silenciosa, Google Maps
   real (Places, Geocoding, mapa e rotas), com a chave fora do Git.
3. **Troca de chave do Gemini** (commit anterior). `GEMINI_API_KEYS` lista
   chaves de reserva: quando a cota do dia de uma acaba, o atendente passa na
   hora para a próxima, com o mesmo modelo; a chave esgotada volta na virada da
   cota (08:00 UTC). Só a posição da chave vai ao log. Cinco testes novos.
4. **Ligar e desligar.** O desligamento automático do Azure (DevTestLab) não
   existe em Chile Central: a VM ganhou uma identidade com permissão só sobre
   ela mesma e se desaloca às 23h de Brasília por um agendamento interno. Ao
   ligar, uma busca de aquecimento carrega o bge-m3 antes do primeiro visitante.
5. **Endereço com o nome do projeto**: rótulo DNS gratuito do IP fixo,
   `vetia.chilecentral.cloudapp.azure.com`; `57.156.57.72.sslip.io` segue
   como reserva.

## Resultado obtido

| Medida (19/10, B2as_v2) | Valor |
|---|---|
| Triagem por texto, servidor aquecido | ~26 s (busca 0,5 s; o resto é o Gemini) |
| Primeira busca depois de ligar (carrega o bge-m3) | 25–66 s |
| Voz (Whisper small, CPU), 1 s de áudio | 14 s na primeira vez |
| Busca de clínicas reais ao redor da FEI (3 km) | 20 clínicas, mapa na tela |
| Desligar / ligar até a VM responder | ~1 min / ~15 s |
| Memória em uso | ~1,6 GB de 8 GB |
| Custo com ~40 h ligada por mês | ~US$ 13/mês |

Os relatos de teste deram a classe e a ficha esperadas (chocolate em cão
pequeno: EMERGENCIA, ficha de chocolate em 1º; espirro leve em gata:
NAO_EMERGENCIA), respondidos pelo Gemini, sem troca de modelo. Depois de
desligar, religar e reiniciar a máquina, tudo voltou sozinho, com o mesmo IP e
os dados no lugar. Suíte do backend: 318 testes.

## Observações

- Recriar só o backend deixava a API inteira em 502: o Nginx guardava o IP
  antigo do contêiner. Corrigido com `resolve` no upstream (Nginx 1.27.5).
- Com o login rápido desligado, as clínicas fictícias que recebem
  encaminhamentos nem são criadas no banco, e o fluxo de encaminhamento fica
  sem destino; por isso ele fica ligado, como na POC local.
- Num servidor sem GPU, escolher o modelo local dá aviso genérico na tela e 500
  no `/chat/` ([B-81](../backlog.md#b-81)).
- A parte de rede do [B-78](../backlog.md#b-78) ficou resolvida no servidor;
  identidade nas rotas públicas, teto de `num_ctx` e relato no log, não.

## Deixado para depois

- **Domínio próprio** (ex.: `vetia.me`): o GitHub Student Pack dá um no
  primeiro ano, mas o registro é do João; o runbook diz como apontar.
- **Duas chaves do Maps**: hoje a mesma chave serve ao servidor e ao
  navegador, então a de servidor fica visível em `/auth/config`. Separar em
  duas, a web restrita aos domínios e a de servidor ao IP da VM.
- [B-81](../backlog.md#b-81) e o restante do [B-78](../backlog.md#b-78).

## Próximo passo

A rodada que transpõe o conteúdo certificado para o mapa (antes chamada de
rodada 32) passa a ser a 33.
