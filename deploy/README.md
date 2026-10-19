# Deploy na internet — runbook

**Endereço:** <https://vetia.chilecentral.cloudapp.azure.com>
(reserva, mesmo servidor: <https://57.156.57.72.sslip.io>)

O sistema completo — tela React, login próprio e acessos rápidos de tutor e
clínica, triagem por texto e voz com o Gemini, clínicas e encaminhamento —
numa máquina virtual do Azure for Students, com HTTPS. No ar desde 19/10/2026.

**O que este deploy é:** a POC acadêmica acessível para a banca e para
testadores convidados. **O que não é:** um serviço veterinário público. Antes
de abrir para tutores de verdade, ver "Pendências" no fim.

---

## Ligar e desligar a hospedagem

A máquina só gasta crédito **ligada** (~US$ 0,11 por hora). Como não usamos
todo dia, o combinado é: **liga antes de usar, desliga depois**. Se alguém
esquecer, ela se desliga sozinha **todo dia às 23h** (horário de Brasília).

### Quem consegue

A máquina está na assinatura Azure for Students do João (conta da FEI). Para
outra pessoa do time poder ligar e desligar, o João dá acesso uma vez: no
portal, `vetia-01` → **Controle de acesso (IAM)** → **Adicionar atribuição de
função** → função **Colaborador de Máquina Virtual** → escolher a conta FEI da
pessoa. Essa função liga, desliga e reinicia; não apaga nada nem mexe em
cobrança.

### Pelo navegador (o jeito mais fácil)

1. Abrir <https://portal.azure.com> e entrar com a conta da FEI (ela pede o
   segundo fator, no celular).
2. Na busca do topo, digitar **vetia-01** e abrir a máquina virtual.
3. **Para ligar:** botão **Iniciar**. Em ~1 minuto o status vira
   "Executando". Depois de mais ~1 minuto o site abre e já responde rápido
   (o servidor se aquece sozinho ao ligar).
4. **Para desligar:** botão **Parar** → **Sim**. O status vira
   "Parado (desalocado)" — é esse estado que zera o custo da máquina.

### Pelo celular

App **Microsoft Azure** (Android/iOS) → entrar com a conta da FEI →
**Máquinas virtuais** → **vetia-01** → **Iniciar** ou **Parar**.

### Pelo terminal

Com a [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) e
`az login` feito (no Windows, pelo PowerShell):

```bash
az vm start      -g tcc-vetia -n vetia-01   # liga
az vm deallocate -g tcc-vetia -n vetia-01   # desliga (computação a zero)
az vm show -d    -g tcc-vetia -n vetia-01 --query powerState -o tsv   # está ligada?
```

Se o `az` responder `AADSTS50076` (a FEI exige MFA), entrar com
`az login --use-device-code` e digitar o código em
<https://microsoft.com/devicelogin>.

### O que acontece sozinho

- **Às 23h de Brasília** a máquina se desliga (um agendamento dentro dela; o
  desligamento automático do próprio Azure não existe na região Chile
  Central). Se ela desligar no meio de um uso à noite, é só ligar de novo.
  Para mudar o horário: `/etc/cron.d/desalocar` na VM, em horário UTC.
- **Ao ligar**, tudo sobe sem ninguém mexer: banco, backend, tela, HTTPS.
  O endereço não muda, e contas, conversas e encaminhamentos continuam lá.
- Ligar é sempre manual: nada liga a máquina sozinho.

### Cuidados

- **Desligar sempre pelo portal, app ou `az vm deallocate`.** Desligar de
  dentro da máquina (`sudo poweroff`) para o sistema mas **continua cobrando**.
  "Reiniciar" no portal pode ser usado à vontade.
- **Nunca excluir** a máquina nem o grupo de recursos `tcc-vetia`: apaga o
  servidor e todos os dados.
- Desligada, a máquina ainda custa ~US$ 8–9 por mês (disco e IP fixo).
- Crédito restante: portal → **Education** (Azure for Students) → visão geral.
  O crédito acabando, a assinatura é suspensa; não há cobrança (não há cartão).

---

## Como está configurado

| Serviço | Imagem | Exposto? | Função |
|---|---|---|---|
| caddy | `caddy:2-alpine` | **80/443** | HTTPS automático (Let's Encrypt) e proxy |
| frontend | build de `frontend-react/` | não | React estático + Nginx com limites, repassa `/api/` |
| backend | build de `backend/` (torch CPU) | não | FastAPI; bge-m3 e Whisper em CPU; Chroma versionado |
| mongo | `mongo:7.0.41` | não | contas, pets, conversas, clínicas, encaminhamentos |
| ollama | — | não sobe | sem GPU no servidor; `--profile local` liga se houver |

O `.env` do servidor segue [`env.prod.example`](env.prod.example), que é a
configuração de [`docs/poc-utilizavel.md`](../docs/poc-utilizavel.md) — a POC
completa, como o time roda localmente:

- **Login:** contas próprias no Mongo (`AUTH_PROVIDER=local`) e os acessos
  rápidos "Entrar como tutor" e "Entrar como clínica"
  (`POC_QUICK_LOGIN_ENABLED=true`). Os acessos rápidos são **contas
  compartilhadas**: quem entra por eles vê o que os outros fizeram por eles.
  Não colocar dados pessoais nessas contas.
- **Atendente:** Gemini, sem troca silenciosa. `GEMINI_API_KEYS` guarda chaves
  de reserva: quando a cota do dia de uma acaba, o atendente passa para a
  próxima (mesmo modelo). O modelo local aparece como opção, mas sem GPU o
  Ollama não sobe: escolhido, a análise falha com aviso genérico e o relato
  fica salvo ([B-81](../evidencias/backlog.md#b-81)).
- **Clínicas:** Google Maps real (`MAPS_PROVIDER=google`) com duas chaves,
  `GOOGLE_MAPS_SERVER_KEY` e `GOOGLE_MAPS_WEB_KEY`. A
  [Demo Key do Google](https://developers.google.com/maps/demo-key) serve:
  gratuita, sem cartão, cobre mapa, Places (New), Geocoding v4 e Compute
  Routes, sem avaliações e fotos; ao esgotar a cota do dia, pausa até o dia
  seguinte. Sem chave, use `MAPS_PROVIDER=fixtures` (só as clínicas fictícias).
  O encaminhamento digital continua indo só para clínicas participantes: as
  fictícias, pelos acessos rápidos, ou unidades verificadas manualmente.
- **Limites (Nginx):** triagem, voz e clínicas, 12 pedidos por minuto por IP;
  o resto da API, 120. Mongo e backend não ficam expostos.

Medido em 19/10 (B2as_v2): triagem com o servidor aquecido em ~26 s, quase
tudo do Gemini; a primeira busca depois de ligar carrega o bge-m3 em ~25–40 s,
e o aquecimento automático faz isso antes do primeiro visitante. Memória em
uso: ~1,6 GB de 8 GB. Desligar leva ~1 min; ligar, ~15 s até a máquina
responder.

---

## Montar do zero

Só é preciso para recriar o servidor (outra conta, outra região). O passo 4
em diante vale para qualquer VPS x86 com Ubuntu.

### 1. Pré-requisitos (na sua máquina)

- Azure CLI (`winget install Microsoft.AzureCLI`) e `az login` com a conta da
  FEI; a assinatura "Azure for Students" precisa estar **Ativa** (Education
  Hub). No Windows, rodar o `az` pelo PowerShell (o Git Bash tropeça no espaço
  de `C:\Program Files`).
- Uma chave SSH só para o deploy: `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_tcc_deploy`.

### 2. Criar a máquina

```bash
bash deploy/azure/criar-vm.sh   # Chile Central, B2as_v2 (8 GB), disco 32 GB
```

Cria o grupo de recursos, a VM Ubuntu 24.04 (B2as_v2, 8 GB, em Chile Central —
a assinatura de estudante só libera cinco regiões, e só lá há a série B x86),
IP fixo com o nome `vetia.chilecentral.cloudapp.azure.com`, portas 22/80/443 e
uma identidade gerenciada com permissão só sobre a própria VM (é ela que
permite o desligamento automático). Para 4 GB: `SIZE=Standard_B2als_v2`.

### 3. Endereço

- **Nome do Azure (o atual):** o IP fixo ganha um rótulo DNS gratuito,
  `ROTULO.chilecentral.cloudapp.azure.com`. Numa VM já criada:
  `az network public-ip update -g tcc-vetia -n vetia-01PublicIP --dns-name vetia`.
- **Sem nada:** `IP.sslip.io` funciona com qualquer IP.
- **Domínio próprio** (ex.: `vetia.me`): um registro `A` apontando para o IP
  fixo. O GitHub Student Developer Pack dá um domínio grátis no primeiro ano
  (Namecheap, Name.com, .TECH). Depois, acrescentar o nome em `DOMAIN` e em
  `FRONTEND_ORIGINS` no `.env` e rodar `docker compose ... up -d`.

`DOMAIN` aceita vários nomes separados por vírgula; o Caddy certifica todos.

### 4. Primeira subida (na VM, por SSH)

```bash
ssh -i ~/.ssh/id_ed25519_tcc_deploy vetia@IP

# Docker e 4 GB de swap (folga para o build do torch)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && newgrp docker
sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Código e configuração
git clone https://github.com/vinizika/tcc.git && cd tcc
cp deploy/env.prod.example .env
nano .env   # DOMAIN, FRONTEND_ORIGINS, chaves do Gemini e do Maps
chmod 600 .env

# Desligamento automático às 23h de Brasília (02:00 UTC), pela identidade da VM
sudo install -m 755 deploy/azure/desalocar-si-mesma.sh /usr/local/bin/
echo "0 2 * * * root /usr/local/bin/desalocar-si-mesma.sh" | sudo tee /etc/cron.d/desalocar

# Aquecimento: ao ligar, uma busca carrega o bge-m3 na memória, para o
# primeiro visitante não esperar. Trocar DOMINIO pelo primeiro nome do DOMAIN.
D=DOMINIO; echo "@reboot root sleep 30 && curl -s -m 300 --retry 20 --retry-delay 10 --retry-all-errors --resolve $D:443:127.0.0.1 -X POST https://$D/api/search/ -H \"Content-Type: application/json\" -d \"{\\\"question\\\":\\\"aquecimento\\\"}\" -o /dev/null" | sudo tee /etc/cron.d/aquecer

# Sobe. A primeira vez constrói as imagens (~10 min) e baixa o bge-m3 (2,2 GB)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend
```

Pronto quando `https://DOMAIN/api/health/` responde `ok` e a tela abre em
`https://DOMAIN`. Testar: acesso rápido de tutor e de clínica, conta própria,
relato por texto, voz (exige HTTPS), conversa com pergunta, busca de clínicas
e encaminhamento até a clínica aceitar.

---

## Atualizar o código

```bash
ssh -i ~/.ssh/id_ed25519_tcc_deploy vetia@57.156.57.72
cd tcc && git pull --ff-only
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Mudou só o `.env`: basta o `up -d` (sem `--build`), que recria o que mudou. O
Nginx volta a achar o backend recriado sozinho.

## Backup do Mongo

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T mongo \
  mongodump --archive --gzip > backup-$(date +%F).gz
```

Copiar para fora com `scp`. Antes de apagar o servidor de vez, um backup.

## Custos (Azure for Students, aproximados)

| Uso | B2als_v2 (4 GB) | B2as_v2 (8 GB, o atual) |
|---|---|---|
| ligada 24 h | ~US$ 45/mês | ~US$ 85/mês |
| ligada ~40 h/mês, desligada o resto | ~US$ 11/mês | ~US$ 13/mês |

Preços de Chile Central (B2as_v2 ~US$ 0,105/h), já com disco e IP fixo
(~US$ 8–9/mês, ligada ou não). No segundo regime, o crédito anual do programa
dura até a banca com folga.

## Pendências antes de abrir para tutores de verdade

- Texto de aviso/consentimento antes do primeiro relato e retenção dos dados
  ([B-64](../evidencias/backlog.md#b-64)); "Respondido por" visível
  ([B-74](../evidencias/backlog.md#b-74)).
- O relato ainda vai inteiro ao log em INFO; teto de `num_ctx` no servidor
  ([B-78](../evidencias/backlog.md#b-78)).
- Prazo total no cliente Gemini ([B-65](../evidencias/backlog.md#b-65)).
- Acessos rápidos são contas compartilhadas; a triagem avulsa (`/api/chat/`
  sem conversa salva) não pede login e gasta cota do Gemini de quem tiver o
  link ([B-78](../evidencias/backlog.md#b-78)).
- Maps: hoje a mesma chave serve ao servidor e ao navegador, e a de servidor
  fica visível em `/auth/config`. Separar em duas, a web restrita aos domínios
  do `DOMAIN` e a de servidor ao IP da VM; para produção, projeto com billing.
- Cota do Gemini: 500 chamadas/dia por chave na conta gratuita, somando todos
  os visitantes.
