#!/usr/bin/env bash
# A VM se desaloca sozinha (computação a zero) pela identidade gerenciada dela.
# O desligamento automático nativo do Azure (DevTestLab) não existe em Chile
# Central, então o agendamento fica dentro da própria máquina:
#
#   sudo cp deploy/azure/desalocar-si-mesma.sh /usr/local/bin/ && sudo chmod +x /usr/local/bin/desalocar-si-mesma.sh
#   echo "0 2 * * * root /usr/local/bin/desalocar-si-mesma.sh" | sudo tee /etc/cron.d/desalocar
#
# 02:00 UTC = 23:00 em Brasília. A identidade só tem "Virtual Machine
# Contributor" nesta VM (az vm identity assign ... --scope <id da VM>).
# Ligar de novo é sempre manual: az vm start -g tcc-vetia -n vetia-01.
set -euo pipefail

IMDS=http://169.254.169.254/metadata
META=$(curl -fsS -H Metadata:true "$IMDS/instance/compute?api-version=2021-02-01")
SUB=$(echo "$META" | python3 -c 'import json,sys; print(json.load(sys.stdin)["subscriptionId"])')
RG=$(echo "$META" | python3 -c 'import json,sys; print(json.load(sys.stdin)["resourceGroupName"])')
VM=$(echo "$META" | python3 -c 'import json,sys; print(json.load(sys.stdin)["name"])')

TOKEN=$(curl -fsS -H Metadata:true \
  "$IMDS/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')

logger -t desalocar "desalocando $VM ($RG)"
curl -fsS -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Length: 0" \
  "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Compute/virtualMachines/$VM/deallocate?api-version=2024-07-01"
