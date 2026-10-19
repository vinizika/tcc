#!/usr/bin/env bash
# Cria a VM do deploy no Azure (assinatura Azure for Students) com a CLI `az`.
# Pré-requisitos: `az login` feito; a chave pública SSH em $KEY.
#
#   bash deploy/azure/criar-vm.sh            (padrões abaixo)
#
# Padrões: grupo tcc-vetia, região Chile Central — a única das cinco que a
# assinatura Azure for Students permite (chilecentral, eastus2, spaincentral,
# southcentralus, brazilsouth) com a série B x86 liberada; no Brazil South só há
# a série D, ~40% mais cara. Tamanho B2as_v2 (2 vCPU AMD, 8 GB, ~US$ 0,105/h),
# Ubuntu 24.04, IP público fixo, disco de 32 GB SSD padrão, portas 22/80/443, e
# a identidade que permite à VM se desligar sozinha às 23h de Brasília (02:00
# UTC) para não gastar crédito à toa. Ligar é manual: az vm start -g $RG -n $VM.
#
# A conta da FEI exige MFA para gerenciar recursos. Se o `az` responder
# AADSTS50076, entrar pelo código de dispositivo:
#   az login --use-device-code --tenant <id do tenant da FEI>
set -euo pipefail

RG=${RG:-tcc-vetia}
LOC=${LOC:-chilecentral}
VM=${VM:-vetia-01}
SIZE=${SIZE:-Standard_B2as_v2}
USER=${ADMIN:-vetia}
KEY=${KEY:-$HOME/.ssh/id_ed25519_tcc_deploy.pub}
DNS=${DNS:-vetia}   # nome: $DNS.$LOC.cloudapp.azure.com

[ -f "$KEY" ] || { echo "chave pública não encontrada: $KEY"; exit 1; }

# Assinatura renovada vem sem os provedores registrados (gratuito, uma vez).
for p in Microsoft.Compute Microsoft.Network Microsoft.Storage; do
  az provider register -n "$p" --wait -o none
done

az group create -n "$RG" -l "$LOC" -o table

az vm create \
  -g "$RG" -n "$VM" \
  --image Ubuntu2404 \
  --size "$SIZE" \
  --admin-username "$USER" \
  --ssh-key-values "$KEY" \
  --public-ip-sku Standard \
  --public-ip-address-allocation static \
  --public-ip-address-dns-name "$DNS" \
  --os-disk-size-gb 32 \
  --storage-sku StandardSSD_LRS \
  --nsg-rule SSH \
  -o table

az vm open-port -g "$RG" -n "$VM" --port 80,443 --priority 1010 -o none

# Auto-desligamento. O nativo (`az vm auto-shutdown`, do DevTestLab) não existe
# em Chile Central; a VM ganha uma identidade com permissão só sobre ela mesma e
# se desaloca por um cron interno (deploy/azure/desalocar-si-mesma.sh, instalado
# no passo 4 do README).
VM_ID=$(az vm show -g "$RG" -n "$VM" --query id -o tsv)
az vm identity assign -g "$RG" -n "$VM" \
  --role "Virtual Machine Contributor" --scope "$VM_ID" -o none

IP=$(az vm show -d -g "$RG" -n "$VM" --query publicIps -o tsv)
echo
echo "VM pronta. IP fixo: $IP"
echo "Endereço: https://${DNS}.${LOC}.cloudapp.azure.com (reserva: ${IP}.sslip.io)"
echo "SSH: ssh -i ${KEY%.pub} ${USER}@${IP}"
