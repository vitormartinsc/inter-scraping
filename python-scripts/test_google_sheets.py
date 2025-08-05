#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar conexão com Google Sheets
"""

import json
import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

def test_google_sheets_connection():
    """
    Testa a conexão com Google Sheets usando diferentes métodos
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
    
    # Método 1: Tentar Service Account (se credentials.json for service account)
    try:
        print("🔐 Testando autenticação via Service Account...")
        creds = Credentials.from_service_account_file('credentials.json')
        gc = gspread.authorize(creds)
        
        # Testa abertura da planilha
        sheet = gc.open_by_key(sheet_id)
        print(f"✅ Planilha aberta via Service Account: {sheet.title}")
        
        # Testa leitura da primeira aba
        worksheet = sheet.get_worksheet(0)
        print(f"✅ Primeira aba: {worksheet.title}")
        
        # Tenta ler alguns dados
        data = worksheet.get_all_records()
        print(f"✅ Dados lidos: {len(data)} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Service Account falhou: {e}")
    
    # Método 2: OAuth 2.0 (se credentials.json for OAuth)
    try:
        print("\n🔐 Testando autenticação via OAuth 2.0...")
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        creds = None
        # Verifica se existe token salvo
        if os.path.exists('token.json'):
            creds = OAuthCredentials.from_authorized_user_file('token.json', SCOPES)
        
        # Se não há credenciais válidas, faz o fluxo OAuth
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salva as credenciais
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        gc = gspread.authorize(creds)
        
        # Testa abertura da planilha
        sheet = gc.open_by_key(sheet_id)
        print(f"✅ Planilha aberta via OAuth: {sheet.title}")
        
        # Testa leitura da primeira aba
        worksheet = sheet.get_worksheet(0)
        print(f"✅ Primeira aba: {worksheet.title}")
        
        # Lista todas as abas
        worksheets = sheet.worksheets()
        print(f"✅ Abas disponíveis:")
        for i, ws in enumerate(worksheets):
            print(f"   {i+1}. {ws.title}")
        
        # Procura pela aba "Página2"
        try:
            pagina2 = sheet.worksheet("Página2")
            data = pagina2.get_all_records()
            print(f"✅ Aba 'Página2' encontrada com {len(data)} registros")
        except Exception as e:
            print(f"⚠️ Aba 'Página2' não encontrada: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth falhou: {e}")
    
    return False

if __name__ == "__main__":
    import os
    success = test_google_sheets_connection()
    
    if success:
        print("\n🎉 Conexão com Google Sheets estabelecida com sucesso!")
        print("✅ Agora você pode executar o script principal:")
        print("   python treating_data_with_type_and_brand_inter.py")
    else:
        print("\n❌ Não foi possível conectar ao Google Sheets")
        print("💡 Verifique se:")
        print("   1. O arquivo credentials.json está correto")
        print("   2. As APIs estão habilitadas no Google Cloud Console")
        print("   3. O ID da planilha está correto")
        print("   4. A planilha é compartilhada com sua conta Google")
