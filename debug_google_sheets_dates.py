#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar os formatos de data no Google Sheets
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

def main():
    print("=== INVESTIGAÇÃO DOS FORMATOS DE DATA NO GOOGLE SHEETS ===\n")
    
    # Carrega configuração
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    sheet_id = config.get('google_sheets', {}).get('main_sheet_id', '')
    
    if not sheet_id or sheet_id == 'seu_sheet_id_aqui':
        print("Google Sheets não configurado")
        return
    
    try:
        # Conecta ao Google Sheets
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
        
        df = pd.DataFrame(data)
        
        if 'Data' not in df.columns:
            print("Coluna 'Data' não encontrada no Google Sheets")
            return
        
        print(f"Total de registros: {len(df)}")
        print(f"Coluna Data tipo original: {df['Data'].dtype}")
        
        # Analisa os diferentes formatos de data
        print("\n=== ANÁLISE DOS FORMATOS DE DATA ===")
        
        # Converte para string para análise
        df['Data_str'] = df['Data'].astype(str)
        
        # Valores únicos dos formatos
        formatos_unicos = df['Data_str'].value_counts()
        print(f"\nTipos de valores únicos encontrados: {len(formatos_unicos)}")
        print("\nPrimeiros 20 valores mais frequentes:")
        print(formatos_unicos.head(20))
        
        # Identifica valores problemáticos
        print("\n=== VALORES PROBLEMÁTICOS ===")
        
        # Testa conversão
        df['Data_converted'] = pd.to_datetime(df['Data'], errors='coerce')
        valores_nulos = df[df['Data_converted'].isnull()]
        
        print(f"Registros que falharam na conversão: {len(valores_nulos)}")
        
        if len(valores_nulos) > 0:
            print("\nExemplos de valores que falharam:")
            problematicos = valores_nulos['Data_str'].value_counts()
            print(problematicos.head(10))
            
            print("\nAmostra dos registros problemáticos:")
            print(valores_nulos[['CPF/CNPJ', 'Data_str', 'Valor']].head(10))
        
        # Identifica padrões
        print("\n=== ANÁLISE DE PADRÕES ===")
        
        # Diferentes padrões encontrados
        padroes = set()
        for val in df['Data_str'].unique():
            if val and val != '' and val != 'nan':
                padroes.add(len(str(val)))
        
        print(f"Comprimentos de string encontrados: {sorted(padroes)}")
        
        # Valores vazios ou não numéricos
        vazios = df[df['Data_str'].isin(['', 'nan', 'NaT', 'None'])]
        print(f"Registros com valores vazios/nan: {len(vazios)}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
