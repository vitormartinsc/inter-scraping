#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar dados dos clientes
"""

import pandas as pd
import numpy as np
import re
import json

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

def main():
    # Carrega config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Carrega dados dos clientes
    excel_path = config['files']['clients_data']
    print(f"Lendo arquivo: {excel_path}")
    
    try:
        clientes = pd.read_excel(excel_path)
        print(f"\n=== DADOS BRUTOS ===")
        print(f"Total de registros: {len(clientes)}")
        print(f"Colunas disponíveis: {list(clientes.columns)}")
        
        # Processa CPF/CNPJ
        clientes = process_cpf_cnpj(clientes, 'cpf_cnpj')
        
        # Busca por CPFs específicos
        cpfs_procurados = ['013.707.946-06', '259.644.388-06']
        
        for cpf in cpfs_procurados:
            print(f"\n=== BUSCANDO CPF {cpf} ===")
            match = clientes[clientes['cpf_cnpj'] == cpf]
            
            if not match.empty:
                print(f"✅ Encontrado! {len(match)} registro(s)")
                cliente = match.iloc[0]
                print(f"Nome: {cliente.get('name', 'N/A')}")
                print(f"UF: {cliente.get('state_name', 'N/A')}")
                print(f"CEP: {cliente.get('cep', 'N/A')}")
                print(f"Telefone: {cliente.get('phone', 'N/A')}")
                print(f"Email: {cliente.get('email', 'N/A')}")
                print(f"Cidade: {cliente.get('city_name', 'N/A')}")
                print(f"Status: {cliente.get('status', 'N/A')}")
                print(f"Banco: {cliente.get('bank_name', 'N/A')}")
                
                print(f"\nTodos os dados do cliente:")
                for col in cliente.index:
                    valor = cliente[col]
                    if pd.notna(valor) and str(valor).strip() != '':
                        print(f"  {col}: {valor}")
            else:
                print(f"❌ CPF {cpf} NÃO encontrado")
                
                # Busca por nome
                if cpf == '013.707.946-06':
                    nome_busca = 'Romilson'
                elif cpf == '259.644.388-06':
                    nome_busca = 'Lana'
                else:
                    continue
                    
                print(f"\nBuscando por nome contendo '{nome_busca}':")
                nome_match = clientes[clientes['name'].str.contains(nome_busca, case=False, na=False)]
                if not nome_match.empty:
                    print(f"Encontrados {len(nome_match)} registros com nome similar:")
                    for _, row in nome_match.iterrows():
                        print(f"  - {row['name']} | CPF: {row['cpf_cnpj']}")
                else:
                    print(f"Nenhum registro encontrado com nome '{nome_busca}'")
        
        # Lista todos os CPFs para verificação
        print(f"\n=== TODOS OS CPFs NA BASE ===")
        print("Primeiros 20 CPFs:")
        for i, cpf in enumerate(clientes['cpf_cnpj'].head(20)):
            print(f"  {i+1}: {cpf}")
            
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")

if __name__ == "__main__":
    main()
