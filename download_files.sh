#!/bin/bash
# Script para baixar arquivos via EC2 Instance Connect

echo "🔍 Listando arquivos na pasta uploads..."
aws ec2-instance-connect send-ssh-public-key \
    --instance-id i-08bffcc42c37c8fc8 \
    --availability-zone us-east-2c \
    --instance-os-user ediuser \
    --ssh-public-key file://par-chaves.pem.pub

echo "📂 Criando diretório local..."
mkdir -p ./database/stpf_data

echo "⬇️  Tentando baixar arquivos..."
# Método 1: SCP direto
scp -i par-chaves.pem -o ConnectTimeout=30 -o StrictHostKeyChecking=no \
    ediuser@13.59.195.73:/home/ediuser/uploads/*.txt ./database/stpf_data/ 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Arquivos baixados com sucesso!"
    ls -la ./database/stpf_data/
else
    echo "❌ Falha no SCP. Tentando método alternativo..."
    
    # Método 2: rsync
    rsync -avz -e "ssh -i par-chaves.pem -o ConnectTimeout=30 -o StrictHostKeyChecking=no" \
        ediuser@13.59.195.73:/home/ediuser/uploads/*.txt ./database/stpf_data/ 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Arquivos baixados via rsync!"
        ls -la ./database/stpf_data/
    else
        echo "❌ Ambos os métodos falharam. Verificando conectividade..."
        telnet 13.59.195.73 22
    fi
fi
