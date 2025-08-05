#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Python SIMPLIFICADO para processar dados do Inter
Sem Google Sheets - apenas processamento local e Excel
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

def format_cpf_cnpj(x):
    if pd.isna(x):
        return x
    x = re.sub(r'\D', '', str(x))
    if len(x) == 11:  # CPF
        return f"{x[:3]}.{x[3:6]}.{x[6:9]}-{x[9:11]}"
    elif len(x) == 14:  # CNPJ
        return f"{x[:2]}.{x[2:5]}.{x[5:8]}/{x[8:12]}-{x[12:14]}"
    else:
        return x

def process_cpf_cnpj(df, column_name='cpf_cnpj'):
    df = df.copy()
    df[column_name] = df[column_name].astype(str)
    df[column_name] = df[column_name].str.replace(r'\D', '', regex=True)
    df[column_name] = df[column_name].apply(lambda x: 
        x.zfill(11) if len(x) <= 11 else x.zfill(14) if len(x) > 11 else x)
    df[column_name] = df[column_name].apply(format_cpf_cnpj)
    return df

def main():
    print("🚀 Iniciando processamento dos dados do Inter...")
    
    # Lê dados do arquivo CSV
    try:
        inter_db = pd.read_csv('db_inter_merged.csv')
        print(f"✅ Dados do Inter carregados: {len(inter_db)} registros")
    except FileNotFoundError:
        print("❌ ERRO: Arquivo db_inter_merged.csv não encontrado")
        return
    
    # Processa CPF/CNPJ
    print("🔄 Processando CPF/CNPJ...")
    inter_db = process_cpf_cnpj(inter_db, 'cpf_cnpj')
    
    # Converte tipos
    inter_db['date'] = pd.to_datetime(inter_db['date'], errors='coerce')
    inter_db['value'] = pd.to_numeric(inter_db['value'], errors='coerce')
    inter_db['installments'] = pd.to_numeric(inter_db['installments'], errors='coerce')
    
    # Remove duplicatas
    db_mine = inter_db[['date', 'brand', 'value', 'cpf_cnpj', 'nome', 'payment_method', 'installments', 'Id']].copy()
    db_mine = db_mine.drop_duplicates(subset=['Id'], keep='first')
    
    # Carrega dados dos clientes
    try:
        clientes = pd.read_excel('Dados Clintes Inter.xlsx')
        db_clientes_data = clientes[['name', 'cpf_cnpj', 'state_name', 'fantasy_name', 'branch_of_activity',
                                   'cep', 'phone', 'email', 'city_name', 'street_name', 'status', 'bank_name', 
                                   'agency', 'account_dv', 'account_type']].copy()
        db_clientes_data = process_cpf_cnpj(db_clientes_data, 'cpf_cnpj')
        print(f"✅ Dados dos clientes carregados: {len(db_clientes_data)} registros")
        
        # Faz join
        final_db = db_mine.merge(db_clientes_data, on='cpf_cnpj', how='left')
        print("✅ Join com dados dos clientes realizado")
        
    except FileNotFoundError:
        print("⚠️ Arquivo 'Dados Clintes Inter.xlsx' não encontrado")
        final_db = db_mine.copy()
        for col in ['name', 'state_name', 'fantasy_name', 'branch_of_activity', 'cep', 'phone', 
                   'email', 'city_name', 'street_name', 'status', 'bank_name', 'agency', 'account_dv', 'account_type']:
            final_db[col] = np.nan
    
    # Formata resultado final
    result_db = pd.DataFrame({
        'CPF/CNPJ': final_db['cpf_cnpj'],
        'Valor': final_db['value'],
        'Data': final_db['date'].dt.strftime('%Y-%m-%d') if 'date' in final_db.columns else '',
        'Column 10': np.nan,
        'Meio de Pagamento': final_db['payment_method'],
        'Nº de Parcelas': final_db['installments'],
        'Bandeira': final_db['brand'],
        'Nome': final_db['nome'],
        'UF': final_db.get('state_name', np.nan),
        'Nome Fantasia': final_db.get('fantasy_name', np.nan),
        'Ramo de Atividade': final_db.get('branch_of_activity', np.nan),
        'CEP': final_db.get('cep', np.nan),
        'Telefone': final_db.get('phone', np.nan),
        'Email': final_db.get('email', np.nan),
        'Cidade': final_db.get('city_name', np.nan),
        'Logradouro': final_db.get('street_name', np.nan),
        'Status': final_db.get('status', np.nan),
        'Banco': final_db.get('bank_name', np.nan),
        'Agência': final_db.get('agency', np.nan),
        'Conta DV': final_db.get('account_dv', np.nan),
        'Tipo de Conta': final_db.get('account_type', np.nan),
        'Id': final_db['Id']
    })
    
    # Converte Data para datetime
    result_db['Data'] = pd.to_datetime(result_db['Data'], errors='coerce')
    
    # Preenche nomes vazios
    if not db_clientes_data.empty:
        cpf_to_name = dict(zip(db_clientes_data['cpf_cnpj'], db_clientes_data['name']))
        mask = result_db['Nome'].isna() | (result_db['Nome'] == '')
        result_db.loc[mask, 'Nome'] = result_db.loc[mask, 'CPF/CNPJ'].map(cpf_to_name)
    
    # Substitui 'Não se aplica' por 'Pix'
    result_db['Meio de Pagamento'] = result_db['Meio de Pagamento'].replace('Não se aplica', 'Pix')
    
    # Verifica CPF específico
    cpf_procurado = '013.707.946-06'
    cpf_encontrado = result_db[result_db['CPF/CNPJ'] == cpf_procurado]
    if not cpf_encontrado.empty:
        print(f"✅ CPF {cpf_procurado} encontrado: {len(cpf_encontrado)} registros")
        print("📋 Detalhes:")
        print(cpf_encontrado[['CPF/CNPJ', 'Data', 'Valor', 'Meio de Pagamento', 'Bandeira', 'Nome']].to_string())
    else:
        print(f"❌ CPF {cpf_procurado} NÃO encontrado")
    
    # Salva arquivo Excel
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    excel_filename = f'dados_processados_{timestamp}.xlsx'
    
    try:
        result_db.to_excel(excel_filename, index=False)
        print(f"✅ Arquivo Excel salvo: {excel_filename}")
    except Exception as e:
        print(f"❌ Erro ao salvar Excel: {e}")
    
    print(f"🎉 Processamento concluído! {len(result_db)} registros processados")
    return result_db

if __name__ == "__main__":
    result = main()
