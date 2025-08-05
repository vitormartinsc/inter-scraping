#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar o processamento do CPF específico
"""

import pandas as pd
import re

def format_cpf_cnpj(x):
    """
    Formata CPF/CNPJ com pontos, traços e barras
    """
    if pd.isna(x):
        return x
    
    # Remove todos os caracteres não numéricos
    x = re.sub(r'\D', '', str(x))
    
    if len(x) == 11:  # CPF
        return f"{x[:3]}.{x[3:6]}.{x[6:9]}-{x[9:11]}"
    elif len(x) == 14:  # CNPJ
        return f"{x[:2]}.{x[2:5]}.{x[5:8]}/{x[8:12]}-{x[12:14]}"
    else:
        return x

def process_cpf_cnpj(df, column_name='cpf_cnpj'):
    """
    Processa e padroniza CPF/CNPJ
    """
    df = df.copy()
    
    # Converte para string e remove caracteres não numéricos
    df[column_name] = df[column_name].astype(str)
    df[column_name] = df[column_name].str.replace(r'\D', '', regex=True)
    
    # Adiciona zeros à esquerda conforme necessário
    df[column_name] = df[column_name].apply(lambda x: 
        x.zfill(11) if len(x) <= 11 else x.zfill(14) if len(x) > 11 else x)
    
    # Formata com pontos e traços
    df[column_name] = df[column_name].apply(format_cpf_cnpj)
    
    return df

# Teste do processamento
print("Testando processamento do CPF...")

# Lê dados do arquivo CSV
try:
    inter_db = pd.read_csv('db_inter_merged.csv')
    print(f"Dados carregados: {len(inter_db)} registros")
    
    # Procura pelo CPF problemático antes do processamento
    cpf_pattern = '1370794606'
    registros_cpf = inter_db[inter_db['cpf_cnpj'].astype(str).str.contains(cpf_pattern, na=False)]
    print(f"Registros com CPF {cpf_pattern} antes do processamento: {len(registros_cpf)}")
    if not registros_cpf.empty:
        print("Primeiros registros encontrados:")
        print(registros_cpf[['date', 'cpf_cnpj', 'value', 'payment_method']].head())
    
    # Processa CPF/CNPJ
    print("\nProcessando CPF/CNPJ...")
    inter_db_processed = process_cpf_cnpj(inter_db, 'cpf_cnpj')
    
    # Procura pelo CPF após processamento
    cpf_formatado = '013.707.946-06'
    registros_cpf_formatado = inter_db_processed[inter_db_processed['cpf_cnpj'] == cpf_formatado]
    print(f"\nRegistros com CPF {cpf_formatado} após processamento: {len(registros_cpf_formatado)}")
    if not registros_cpf_formatado.empty:
        print("Registros formatados encontrados:")
        print(registros_cpf_formatado[['date', 'cpf_cnpj', 'value', 'payment_method']])
    
    # Verifica se existem outras variações
    print(f"\nTodos os CPFs únicos que contêm '13707946':")
    cpfs_similares = inter_db_processed[inter_db_processed['cpf_cnpj'].str.contains('13707946', na=False)]['cpf_cnpj'].unique()
    for cpf in cpfs_similares:
        count = len(inter_db_processed[inter_db_processed['cpf_cnpj'] == cpf])
        print(f"  {cpf}: {count} registros")
    
except FileNotFoundError:
    print("ERRO: Arquivo db_inter_merged.csv não encontrado")
except Exception as e:
    print(f"ERRO: {e}")
