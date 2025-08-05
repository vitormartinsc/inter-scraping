#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar o Google Sheets API
"""

import json
import os

def setup_google_sheets():
    """
    Configura as credenciais e ID da planilha do Google Sheets
    """
    print("=== Configuração do Google Sheets ===\n")
    
    # 1. Verificar se existe credentials.json
    if not os.path.exists('credentials.json'):
        print("❌ Arquivo 'credentials.json' não encontrado!")
        print("\n📋 Para configurar o Google Sheets, você precisa:")
        print("1. Ir para: https://console.cloud.google.com/")
        print("2. Criar um projeto ou selecionar um existente")
        print("3. Ativar a Google Sheets API")
        print("4. Criar credenciais (OAuth 2.0)")
        print("5. Baixar o arquivo credentials.json e colocar nesta pasta")
        print("\n📖 Tutorial detalhado:")
        print("https://developers.google.com/sheets/api/quickstart/python")
        return False
    
    # 2. Pedir o ID da planilha
    print("✅ Arquivo credentials.json encontrado!")
    print("\n📋 Agora preciso do ID da sua planilha do Google Sheets")
    print("O ID está na URL da planilha:")
    print("https://docs.google.com/spreadsheets/d/[SEU_ID_AQUI]/edit")
    
    sheet_id = input("\n🔗 Cole o ID da planilha aqui: ").strip()
    
    if not sheet_id:
        print("❌ ID da planilha é obrigatório!")
        return False
    
    # 3. Atualizar config.json
    config = {
        "google_sheets": {
            "main_sheet_id": sheet_id
        },
        "files": {
            "inter_data": "db_inter_merged.csv",
            "clients_data": "Dados Clintes Inter.xlsx"
        }
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuração salva em config.json")
    print(f"📊 ID da planilha: {sheet_id}")
    
    # 4. Testar configuração
    print("\n🧪 Testando configuração...")
    try:
        # Importar e testar o script principal
        import sys
        sys.path.append('.')
        
        from treating_data_with_type_and_brand_inter import get_google_sheets_client, read_google_sheet
        
        print("📡 Conectando ao Google Sheets...")
        gc = get_google_sheets_client()
        
        print("📋 Lendo dados da planilha...")
        df = read_google_sheet(sheet_id, "Página2")
        
        if not df.empty:
            print(f"✅ Sucesso! Planilha lida com {len(df)} registros")
            print("🎉 Google Sheets configurado corretamente!")
            return True
        else:
            print("⚠️ Planilha vazia ou aba 'Página2' não encontrada")
            print("💡 Certifique-se que a aba 'Página2' existe na planilha")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        print("💡 Verifique se:")
        print("- O ID da planilha está correto")
        print("- A planilha é compartilhada publicamente ou com sua conta Google")
        print("- As credenciais são válidas")
        return False

def show_credentials_tutorial():
    """
    Mostra tutorial detalhado para obter credenciais
    """
    print("\n" + "="*60)
    print("📖 TUTORIAL: Como obter credentials.json")
    print("="*60)
    
    steps = [
        "1. Acesse: https://console.cloud.google.com/",
        "2. Crie um novo projeto ou selecione um existente",
        "3. No menu lateral, vá em 'APIs e Serviços' > 'Biblioteca'",
        "4. Procure por 'Google Sheets API' e clique nela",
        "5. Clique em 'ATIVAR'",
        "6. Vá em 'APIs e Serviços' > 'Credenciais'",
        "7. Clique em '+ CRIAR CREDENCIAIS' > 'ID do cliente OAuth'",
        "8. Escolha 'Aplicativo para computador'",
        "9. Dê um nome (ex: 'Inter Scraping')",
        "10. Clique em 'CRIAR'",
        "11. Baixe o arquivo JSON",
        "12. Renomeie para 'credentials.json'",
        "13. Coloque na pasta do projeto"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n💡 DICA: A primeira execução abrirá o navegador para autorizar o acesso")
    print("="*60)

if __name__ == "__main__":
    if not setup_google_sheets():
        show_credentials_tutorial()
