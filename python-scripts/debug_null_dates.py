#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar valores nulos nas datas
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
import os
import json
from pathlib import Path

# Importar bibliotecas do Google Sheets
try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Instalando bibliotecas necessárias...")
    os.system("pip install gspread google-auth")
    import gspread
    from google.oauth2.service_account import Credentials

def load_config():
    """
    Carrega configurações
    """
    try:
        current_dir = Path.cwd()
        if current_dir.name == 'python-scripts':
            config_path = '../config/config.json'
        else:
            config_path = 'config/config.json'
            
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Erro: config.json não encontrado")
        return {}

def get_google_sheets_client():
    """
    Configura cliente do Google Sheets
    """
    try:
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        current_dir = Path.cwd()
        if current_dir.name == 'python-scripts':
            credentials_path = '../config/credentials.json'
        else:
            credentials_path = 'config/credentials.json'
        
        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=SCOPES
        )
        
        return gspread.authorize(credentials)
    except Exception as e:
        print(f"Erro ao configurar cliente Google Sheets: {e}")
        return None

def read_google_sheet(sheet_id, sheet_name="Página2"):
    """
    Lê dados do Google Sheets SEM processar
    """
    try:
        gc = get_google_sheets_client()
        if not gc:
            return pd.DataFrame()
            
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        
        print(f"Dados brutos do Google Sheets: {len(data)} registros")
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Erro ao ler Google Sheets: {e}")
        return pd.DataFrame()

def main():
    """
    Função principal de debug
    """
    print("=== DEBUG: INVESTIGANDO VALORES NULOS NAS DATAS ===")
    
    # Carrega configurações
    config = load_config()
    sheet_id = config.get('google_sheets', {}).get('main_sheet_id', '')
    
    if not sheet_id:
        print("Erro: Google Sheets ID não configurado")
        return
    
    # Lê dados do Google Sheets SEM processamento
    print("\n1. Lendo dados RAW do Google Sheets...")
    full_db = read_google_sheet(sheet_id, "Página2")
    
    if full_db.empty:
        print("Erro: Não foi possível ler dados do Google Sheets")
        return
    
    print(f"Total de registros: {len(full_db)}")
    
    # Verifica coluna Data
    if 'Data' in full_db.columns:
        print(f"\n2. Analisando coluna 'Data'...")
        
        # Conta valores únicos
        print("Tipos de valores na coluna Data:")
        print(full_db['Data'].value_counts().head(10))
        
        # Verifica valores vazios/nulos
        empty_dates = full_db[full_db['Data'].isin(['', ' ', 'nan', 'NaT', 'None', None])]
        print(f"\nRegistros com datas vazias/nulas: {len(empty_dates)}")
        
        if len(empty_dates) > 0:
            print("Exemplos de registros com datas vazias:")
            print(empty_dates[['CPF/CNPJ', 'Data', 'Valor', 'Meio de Pagamento']].head())
        
        # Verifica valores que não conseguem ser convertidos para data
        try:
            converted_dates = pd.to_datetime(full_db['Data'], errors='coerce')
            null_after_conversion = converted_dates.isna().sum()
            print(f"\nRegistros que se tornam NaT após conversão: {null_after_conversion}")
            
            if null_after_conversion > 0:
                problematic = full_db[converted_dates.isna()]
                print("Valores problemáticos que não conseguem ser convertidos:")
                print(problematic['Data'].value_counts().head(10))
                
        except Exception as e:
            print(f"Erro na conversão de datas: {e}")
    
    # Verifica dados do Inter
    print(f"\n3. Verificando dados do Inter...")
    csv_path = config['files']['inter_data']
    try:
        inter_db = pd.read_csv(csv_path)
        print(f"Registros do Inter: {len(inter_db)}")
        
        # Verifica datas do Inter
        if 'date' in inter_db.columns:
            inter_dates = pd.to_datetime(inter_db['date'], errors='coerce')
            inter_null_dates = inter_dates.isna().sum()
            print(f"Datas nulas no Inter: {inter_null_dates}")
            
            if inter_null_dates > 0:
                problematic_inter = inter_db[inter_dates.isna()]
                print("Datas problemáticas no Inter:")
                print(problematic_inter['date'].value_counts().head(5))
        
    except FileNotFoundError:
        print(f"Arquivo {csv_path} não encontrado")
    except Exception as e:
        print(f"Erro ao ler dados do Inter: {e}")
    
    print("\n=== FIM DO DEBUG ===")

if __name__ == "__main__":
    main()
