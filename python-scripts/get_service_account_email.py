#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair o email da Service Account
"""

import json

def get_service_account_email():
    """
    Extrai o email da service account do credentials.json
    """
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        if 'client_email' in creds:
            email = creds['client_email']
            print("📧 EMAIL DA SERVICE ACCOUNT:")
            print("="*50)
            print(f"   {email}")
            print("="*50)
            print()
            print("📋 PRÓXIMOS PASSOS:")
            print("1. Copie este email acima")
            print("2. Abra sua planilha do Google Sheets:")
            print(f"   https://docs.google.com/spreadsheets/d/1jT-q_aEqR9OxcfsYna8UAAwXauH3-9QiM4lI-l6hHYU/edit")
            print("3. Clique em 'Compartilhar' (botão azul no canto superior direito)")
            print("4. Cole o email da service account")
            print("5. Defina permissão como 'Editor'")
            print("6. Clique em 'Enviar'")
            print()
            print("🔄 Depois execute novamente:")
            print("   python test_google_sheets.py")
            
            return email
        else:
            print("❌ Este não é um arquivo de Service Account")
            print("💡 Você tem um arquivo OAuth. Vamos tentar criar um novo Service Account...")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao ler credentials.json: {e}")
        return None

if __name__ == "__main__":
    email = get_service_account_email()
    
    if not email:
        print("\n" + "="*60)
        print("📖 COMO CRIAR UMA SERVICE ACCOUNT:")
        print("="*60)
        print("1. Acesse: https://console.cloud.google.com/")
        print("2. Vá em 'IAM e Admin' > 'Contas de Serviço'")
        print("3. Clique em 'CRIAR CONTA DE SERVIÇO'")
        print("4. Nome: 'Inter Scraping Service'")
        print("5. Clique em 'CRIAR E CONTINUAR'")
        print("6. Pule as permissões (clique em 'CONTINUAR')")
        print("7. Clique em 'CONCLUÍDO'")
        print("8. Clique na conta criada")
        print("9. Vá na aba 'CHAVES'")
        print("10. Clique em 'ADICIONAR CHAVE' > 'Criar nova chave'")
        print("11. Escolha 'JSON' e clique em 'CRIAR'")
        print("12. Substitua o arquivo credentials.json")
        print("="*60)
