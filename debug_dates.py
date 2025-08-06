#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para investigar o problema das datas nulas
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path

def load_config():
    """Carrega configurações"""
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    return config

def main():
    print("=== DEBUG DAS DATAS ===\n")
    
    # 1. Carrega dados originais do Inter
    print("1. DADOS ORIGINAIS DO INTER:")
    inter_db = pd.read_csv('db_inter_merged.csv')
    print(f"   Total: {len(inter_db)} registros")
    print(f"   Datas nulas: {inter_db['date'].isnull().sum()}")
    print(f"   Tipo de dados: {inter_db['date'].dtype}")
    print(f"   Amostra: {inter_db['date'].head(3).tolist()}")
    
    # 2. Após conversão para datetime
    print("\n2. APÓS CONVERSÃO PARA DATETIME:")
    inter_db['date'] = pd.to_datetime(inter_db['date'], errors='coerce')
    print(f"   Datas nulas após conversão: {inter_db['date'].isnull().sum()}")
    print(f"   Tipo de dados: {inter_db['date'].dtype}")
    print(f"   Amostra: {inter_db['date'].head(3).tolist()}")
    
    # 3. Seleciona colunas
    print("\n3. APÓS SELEÇÃO DE COLUNAS:")
    db_mine = inter_db[['date', 'brand', 'value', 'cpf_cnpj', 'nome', 'payment_method', 'installments', 'Id']].copy()
    print(f"   Total: {len(db_mine)} registros")
    print(f"   Datas nulas: {db_mine['date'].isnull().sum()}")
    
    # 4. Carrega dados do Google Sheets (simulação)
    config = load_config()
    sheet_id = config.get('google_sheets', {}).get('main_sheet_id', '')
    
    if sheet_id and sheet_id != 'seu_sheet_id_aqui':
        print("\n4. DADOS DO GOOGLE SHEETS:")
        # Simula leitura do Google Sheets
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            SCOPES = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                'config/credentials.json',
                scopes=SCOPES
            )
            
            gc = gspread.authorize(credentials)
            sheet = gc.open_by_key(sheet_id)
            worksheet = sheet.worksheet("Página2")
            data = worksheet.get_all_records()
            
            full_db = pd.DataFrame(data)
            
            if 'Data' in full_db.columns:
                print(f"   Total do Google Sheets: {len(full_db)} registros")
                print(f"   Tipo original: {full_db['Data'].dtype}")
                print(f"   Amostra original: {full_db['Data'].head(3).tolist()}")
                
                # Converte para datetime
                full_db['Data'] = pd.to_datetime(full_db['Data'], errors='coerce')
                print(f"   Datas nulas após conversão: {full_db['Data'].isnull().sum()}")
                print(f"   Tipo após conversão: {full_db['Data'].dtype}")
                
        except Exception as e:
            print(f"   Erro ao ler Google Sheets: {e}")
            full_db = pd.DataFrame()
    else:
        print("\n4. GOOGLE SHEETS NÃO CONFIGURADO")
        full_db = pd.DataFrame()
    
    # 5. Formata dados finais
    print("\n5. FORMATAÇÃO DOS DADOS FINAIS:")
    result_db = pd.DataFrame({
        'CPF/CNPJ': db_mine['cpf_cnpj'],
        'Valor': db_mine['value'],
        'Data': db_mine['date'],  # Mantém como datetime
        'Meio de Pagamento': db_mine['payment_method'],
        'Nº de Parcelas': db_mine['installments'],
        'Bandeira': db_mine['brand'],
        'Nome': db_mine['nome'],
        'Id': db_mine['Id']
    })
    
    print(f"   Total result_db: {len(result_db)} registros")
    print(f"   Datas nulas em result_db: {result_db['Data'].isnull().sum()}")
    print(f"   Tipo de dados: {result_db['Data'].dtype}")
    
    # 6. Join com Google Sheets
    if not full_db.empty:
        print("\n6. APÓS JOIN COM GOOGLE SHEETS:")
        
        # Padroniza nomes das colunas
        if 'Data' in full_db.columns and 'Data' in result_db.columns:
            # Concatena
            final_db_sheet = pd.concat([full_db, result_db], ignore_index=True, sort=False)
            print(f"   Total após concat: {len(final_db_sheet)} registros")
            print(f"   Datas nulas após concat: {final_db_sheet['Data'].isnull().sum()}")
            
            # Remove duplicatas
            if 'Id' in final_db_sheet.columns:
                final_db_sheet = final_db_sheet.drop_duplicates(subset=['Id'], keep='last')
                print(f"   Total após duplicatas: {len(final_db_sheet)} registros")
                print(f"   Datas nulas após duplicatas: {final_db_sheet['Data'].isnull().sum()}")
        else:
            final_db_sheet = result_db.copy()
            print("   Usando apenas dados do Inter")
    else:
        final_db_sheet = result_db.copy()
        print("\n6. SEM GOOGLE SHEETS - USANDO APENAS INTER")
        print(f"   Total final: {len(final_db_sheet)} registros")
        print(f"   Datas nulas final: {final_db_sheet['Data'].isnull().sum()}")
    
    # 7. Verifica onde estão os nulos
    print("\n7. INVESTIGAÇÃO DOS VALORES NULOS:")
    if 'Data' in final_db_sheet.columns:
        nulos = final_db_sheet[final_db_sheet['Data'].isnull()]
        print(f"   Registros com data nula: {len(nulos)}")
        
        if len(nulos) > 0:
            print("   Amostra de registros com data nula:")
            print(nulos[['CPF/CNPJ', 'Data', 'Valor', 'Meio de Pagamento', 'Id']].head(5))
            
            # Verifica se os IDs com data nula estão no Inter original
            if len(nulos) > 0:
                ids_nulos = nulos['Id'].tolist()
                inter_ids = inter_db['Id'].tolist()
                ids_nulos_no_inter = [id for id in ids_nulos if id in inter_ids]
                print(f"   IDs com data nula que estão no Inter: {len(ids_nulos_no_inter)}")
                
                if len(ids_nulos_no_inter) > 0:
                    print("   Dados originais desses IDs no Inter:")
                    sample_ids = ids_nulos_no_inter[:3]
                    for id_val in sample_ids:
                        inter_row = inter_db[inter_db['Id'] == id_val]
                        if not inter_row.empty:
                            print(f"     ID {id_val}: date = {inter_row['date'].iloc[0]} (tipo: {type(inter_row['date'].iloc[0])})")

if __name__ == "__main__":
    main()
