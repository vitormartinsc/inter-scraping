#!/usr/bin/env python3
import pandas as pd
import glob

# Encontra o arquivo Excel mais recente
excel_files = glob.glob("transaction_with_type_and_brand_from_inter_db_*.xlsx")
if excel_files:
    latest_file = max(excel_files)
    print(f"Verificando arquivo: {latest_file}")
    
    # Lê o arquivo
    df = pd.read_excel(latest_file)
    
    # Procura por Lana Rose
    lana_data = df[df['CPF/CNPJ'] == '259.644.388-06']
    
    if not lana_data.empty:
        print(f"\n✅ Encontrados {len(lana_data)} registros para Lana Rose (259.644.388-06):")
        print("\nDados completos:")
        for col in ['CPF/CNPJ', 'Nome', 'UF', 'Telefone', 'Email', 'Cidade', 'Status']:
            if col in lana_data.columns:
                valor = lana_data.iloc[0][col]
                print(f"  {col}: {valor}")
        
        print(f"\nPrimeiro registro completo:")
        print(lana_data.iloc[0].to_string())
    else:
        print("❌ Lana Rose não encontrada no arquivo")
        
    # Também verifica Romilson
    romilson_data = df[df['CPF/CNPJ'] == '013.707.946-06']
    if not romilson_data.empty:
        print(f"\n✅ Encontrados {len(romilson_data)} registros para Romilson (013.707.946-06):")
        for col in ['CPF/CNPJ', 'Nome', 'UF', 'Telefone', 'Email', 'Cidade', 'Status']:
            if col in romilson_data.columns:
                valor = romilson_data.iloc[0][col]
                print(f"  {col}: {valor}")
else:
    print("❌ Nenhum arquivo Excel encontrado")
