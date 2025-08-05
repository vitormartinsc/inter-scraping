#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Python simplificado para processar dados de transações do Inter
Versão sem Google Sheets para teste inicial
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

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
    """
    Função principal que processa os dados do Inter
    """
    print("Iniciando processamento dos dados do Inter...")
    
    # Lê dados do arquivo CSV
    print("Lendo dados do Inter (db_inter_merged.csv)...")
    try:
        inter_db = pd.read_csv('db_inter_merged.csv')
        print(f"Dados do Inter carregados: {len(inter_db)} registros")
    except FileNotFoundError:
        print("ERRO: Arquivo db_inter_merged.csv não encontrado")
        return
    
    # Verifica se o CPF específico está nos dados originais
    cpf_procurado_original = '1370794606'
    registros_originais = inter_db[inter_db['cpf_cnpj'].astype(str).str.contains(cpf_procurado_original, na=False)]
    print(f"Registros com CPF {cpf_procurado_original} nos dados originais: {len(registros_originais)}")
    
    # Processa CPF/CNPJ do Inter
    print("Processando CPF/CNPJ dos dados do Inter...")
    inter_db = process_cpf_cnpj(inter_db, 'cpf_cnpj')
    
    # Converte tipos de dados
    inter_db['date'] = pd.to_datetime(inter_db['date'], errors='coerce')
    inter_db['value'] = pd.to_numeric(inter_db['value'], errors='coerce')
    inter_db['installments'] = pd.to_numeric(inter_db['installments'], errors='coerce')
    
    # Seleciona e renomeia colunas (equivalente ao db_mine)
    db_mine = inter_db[['date', 'brand', 'value', 'cpf_cnpj', 'nome', 'payment_method', 'installments', 'Id']].copy()
    
    # Remove duplicatas por Id
    db_mine = db_mine.drop_duplicates(subset=['Id'], keep='first')
    
    print(f"Dados únicos do Inter: {len(db_mine)} registros")
    
    # Carrega dados dos clientes
    print("Carregando dados dos clientes...")
    try:
        clientes = pd.read_excel('Dados Clintes Inter.xlsx')
        
        # Seleciona colunas necessárias
        db_clientes_data = clientes[['name', 'cpf_cnpj', 'state_name', 'fantasy_name', 'branch_of_activity',
                                   'cep', 'phone', 'email', 'city_name', 'street_name', 'status', 'bank_name', 
                                   'agency', 'account_dv', 'account_type']].copy()
        
        # Processa CPF/CNPJ dos clientes
        db_clientes_data = process_cpf_cnpj(db_clientes_data, 'cpf_cnpj')
        
        print(f"Dados dos clientes carregados: {len(db_clientes_data)} registros")
        
    except FileNotFoundError:
        print("AVISO: Arquivo 'Dados Clintes Inter.xlsx' não encontrado. Continuando sem dados de clientes.")
        db_clientes_data = pd.DataFrame()
    
    # Faz join com dados dos clientes
    if not db_clientes_data.empty:
        final_db = db_mine.merge(db_clientes_data, on='cpf_cnpj', how='left')
        print("Join com dados dos clientes realizado")
        
        # Verifica quantos registros do CPF específico foram unidos
        cpf_procurado = '013.707.946-06'
        registros_unidos = final_db[final_db['cpf_cnpj'] == cpf_procurado]
        print(f"Registros do CPF {cpf_procurado} após join: {len(registros_unidos)}")
        
        if not registros_unidos.empty:
            print("Detalhes dos registros unidos:")
            print(registros_unidos[['date', 'cpf_cnpj', 'value', 'payment_method', 'name', 'state_name']].to_string())
        
    else:
        final_db = db_mine.copy()
        # Adiciona colunas vazias para manter compatibilidade
        for col in ['name', 'state_name', 'fantasy_name', 'branch_of_activity', 'cep', 'phone', 
                   'email', 'city_name', 'street_name', 'status', 'bank_name', 'agency', 'account_dv', 'account_type']:
            final_db[col] = np.nan
    
    # Formata banco final (equivalente ao transmute do R)
    print("Formatando dados finais...")
    result_db = pd.DataFrame({
        'CPF/CNPJ': final_db['cpf_cnpj'],
        'Valor': final_db['value'],
        'Data': final_db['date'].dt.strftime('%Y-%m-%d') if 'date' in final_db.columns else '',
        'Column 10': np.nan,  # Substitua por coluna real se necessário
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
    
    # Remove colunas lógicas
    result_db = result_db.select_dtypes(exclude=['bool'])
    
    print(f"Dados formatados: {len(result_db)} registros")
    
    # Substitui 'Não se aplica' por 'Pix' em Meio de Pagamento
    if 'Meio de Pagamento' in result_db.columns:
        result_db['Meio de Pagamento'] = result_db['Meio de Pagamento'].replace('Não se aplica', 'Pix')
        print("Substituído 'Não se aplica' por 'Pix' em Meio de Pagamento")
    
    # Verifica se o CPF específico está nos dados finais
    cpf_procurado = '013.707.946-06'
    if 'CPF/CNPJ' in result_db.columns:
        cpf_encontrado = result_db[result_db['CPF/CNPJ'] == cpf_procurado]
        if not cpf_encontrado.empty:
            print(f"✅ CPF {cpf_procurado} encontrado nos dados finais: {len(cpf_encontrado)} registros")
            print("Detalhes:")
            print(cpf_encontrado[['CPF/CNPJ', 'Data', 'Valor', 'Meio de Pagamento', 'Bandeira', 'Nome']].to_string())
        else:
            print(f"❌ CPF {cpf_procurado} NÃO encontrado nos dados finais")
    
    # Salva arquivo Excel localmente
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    excel_filename = f'transaction_with_type_and_brand_from_inter_db_{timestamp}.xlsx'
    
    try:
        result_db.to_excel(excel_filename, index=False)
        print(f"✅ Arquivo Excel salvo: {excel_filename}")
    except Exception as e:
        print(f"❌ Erro ao salvar Excel: {e}")
    
    print("Processamento concluído!")
    
    return result_db


if __name__ == "__main__":
    # Muda para o diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Executa função principal
    result = main()
