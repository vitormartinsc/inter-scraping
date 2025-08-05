#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste corrigido para verificar conexão com Google Sheets
"""

import json
import gspread
from google.oauth2.service_account import Credentials

def test_google_sheets_connection():
    """
    Testa a conexão com Google Sheets usando Service Account
    """
    print("🔍 Testando conexão com Google Sheets...\n")
    
    # Carrega configuração
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        sheet_id = config['google_sheets']['main_sheet_id']
        print(f"✅ Config carregado. Sheet ID: {sheet_id}")
    except Exception as e:
        print(f"❌ Erro ao carregar config: {e}")
        return False
    
    # Testa Service Account com escopos corretos
    try:
        print("🔐 Testando autenticação via Service Account...")
        
        # Define os escopos necessários
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Carrega credenciais com escopos
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        gc = gspread.authorize(creds)
        
        print("✅ Autenticação realizada com sucesso!")
        
        # Testa abertura da planilha
        sheet = gc.open_by_key(sheet_id)
        print(f"✅ Planilha aberta: {sheet.title}")
        
        # Lista todas as abas
        worksheets = sheet.worksheets()
        print(f"✅ Abas disponíveis ({len(worksheets)} abas):")
        for i, ws in enumerate(worksheets):
            print(f"   {i+1}. {ws.title} ({ws.row_count} linhas, {ws.col_count} colunas)")
        
        # Procura pela aba "Página2"
        try:
            pagina2 = sheet.worksheet("Página2")
            print(f"✅ Aba 'Página2' encontrada!")
            
            # Tenta ler alguns dados
            data = pagina2.get_all_records()
            print(f"✅ Dados lidos da Página2: {len(data)} registros")
            
            if len(data) > 0:
                print("📋 Primeiras colunas encontradas:")
                first_row = data[0] if data else {}
                for key in list(first_row.keys())[:5]:  # Mostra primeiras 5 colunas
                    print(f"   - {key}")
            
        except Exception as e:
            print(f"⚠️ Erro ao acessar aba 'Página2': {e}")
            
            # Tenta a primeira aba
            first_sheet = worksheets[0]
            print(f"🔄 Testando primeira aba: {first_sheet.title}")
            data = first_sheet.get_all_records()
            print(f"✅ Dados lidos da primeira aba: {len(data)} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print(f"🔍 Tipo do erro: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_google_sheets_connection()
    
    if success:
        print("\n🎉 Conexão com Google Sheets estabelecida com sucesso!")
        print("✅ Próximos passos:")
        print("   1. Executar o script principal:")
        print("      python treating_data_with_type_and_brand_inter.py")
        print("   2. Ou testar com dados locais:")
        print("      python process_data_simple.py")
    else:
        print("\n❌ Não foi possível conectar ao Google Sheets")
        print("💡 Possíveis soluções:")
        print("   1. Verificar se o arquivo credentials.json é uma Service Account")
        print("   2. Verificar se as APIs estão habilitadas no Google Cloud Console")
        print("   3. Verificar se a planilha foi compartilhada com a service account")
        print("   4. Tentar recriar as credenciais no Google Cloud Console")
