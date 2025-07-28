#!/bin/bash
# Script para ser executado dentro da instância EC2

echo "🔍 Verificando arquivos na pasta uploads..."
ls -la /home/ediuser/uploads/

echo ""
echo "📊 Contando arquivos .txt..."
find /home/ediuser/uploads/ -name "*.txt" | wc -l

echo ""
echo "📋 Listando primeiros 10 arquivos .txt..."
find /home/ediuser/uploads/ -name "*.txt" | head -10

echo ""
echo "📦 Criando arquivo ZIP com todos os .txt..."
cd /home/ediuser/uploads/
zip -r /tmp/granito_files_$(date +%Y%m%d_%H%M%S).zip *.txt

echo ""
echo "✅ Arquivo ZIP criado em:"
ls -la /tmp/granito_files_*.zip

echo ""
echo "📤 Para baixar, use:"
echo "aws s3 cp /tmp/granito_files_*.zip s3://essencial-form-files/"
echo "Ou copie manualmente via console"
