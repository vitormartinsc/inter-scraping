#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Python para processar dados de transações do Inter e combinar com dados de TPV
Equivalente ao script R treating_data_with_type_and_brand_inter.R
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


def load_config():
    """
    Carrega configurações (equivalente ao config.R)
    """
    try:
        with open('../config/config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Arquivo config.json não encontrado. Criando configuração básica...")
        config = {
            "google_sheets": {
                "main_sheet_id": "seu_sheet_id_aqui"
            }
        }
        with open('../config/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        return config


def get_google_sheets_client():
    """
    Configura cliente do Google Sheets usando Service Account
    """
    try:
        # Define os escopos necessários
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Carrega as credenciais do Service Account
        credentials = Credentials.from_service_account_file(
            '../config/credentials.json',
            scopes=SCOPES
        )
        
        # Autoriza e retorna o cliente
        return gspread.authorize(credentials)
    except Exception as e:
        print(f"Erro ao configurar cliente Google Sheets: {e}")
        return None


def read_google_sheet(sheet_id, sheet_name="Página2"):
    """
    Lê dados do Google Sheets
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
            print("Planilha vazia ou sem cabeçalhos")
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Remove colunas lógicas vazias (equivalente ao select(-where(~ is.logical(.))))
        # Converte colunas para string antes de usar .str accessor
        df.columns = df.columns.astype(str)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        
        print(f"Dados processados do Google Sheets: {len(df)} registros")
        
        return df
    except Exception as e:
        print(f"Erro ao ler Google Sheets: {e}")
        return pd.DataFrame()


def write_google_sheet(df, sheet_id, sheet_name="Página2"):
    """
    Escreve dados no Google Sheets
    """
    try:
        gc = get_google_sheets_client()
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.worksheet(sheet_name)
        
        # Prepara o DataFrame para envio
        df_to_send = df.copy()
        
        # Converte todas as colunas de data para o formato YYYY-MM-DD que o Google Sheets reconhece
        for col in df_to_send.columns:
            if pd.api.types.is_datetime64_any_dtype(df_to_send[col]):
                # Converte para formato de data que o Google Sheets entende
                df_to_send[col] = df_to_send[col].dt.strftime('%Y-%m-%d')
        
        # Substitui valores NaN por strings vazias
        df_to_send = df_to_send.fillna('')
        
        # Limpa a planilha
        worksheet.clear()
        
        # Escreve os dados
        data_to_write = [df_to_send.columns.values.tolist()] + df_to_send.values.tolist()
        worksheet.update(data_to_write)
        
        # Aplica formatação de data nas colunas de data
        for col_idx, col_name in enumerate(df_to_send.columns, 1):
            if col_name == 'Data':
                # Formatar a coluna como data
                col_letter = chr(64 + col_idx)  # A=1, B=2, etc.
                range_name = f'{col_letter}2:{col_letter}{len(df_to_send) + 1}'
                
                # Aplica formato de data
                worksheet.format(range_name, {
                    "numberFormat": {
                        "type": "DATE",
                        "pattern": "yyyy-mm-dd"
                    }
                })
                print(f"Formatação de data aplicada na coluna {col_name} ({range_name})")
        
        print(f"Dados escritos com sucesso no Google Sheets: {sheet_name}")
        
    except Exception as e:
        print(f"Erro ao escrever no Google Sheets: {e}")


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
    Função principal que replica a lógica do script R
    """
    print("Iniciando processamento dos dados...")
    
    # Carrega configurações
    config = load_config()
    sheet_id = config.get('google_sheets', {}).get('main_sheet_id', '')
    
    # Se não há sheet_id configurado, executa apenas processamento local
    if not sheet_id or sheet_id == 'seu_sheet_id_aqui':
        print("⚠️ Google Sheets ID não configurado. Executando apenas processamento local...")
        use_google_sheets = False
        full_db = pd.DataFrame()
    else:
        use_google_sheets = True
        # Lê dados do Google Sheets
        print("Lendo dados do Google Sheets...")
        full_db = read_google_sheet(sheet_id, "Página2")
        
        if full_db.empty:
            print("ERRO: Não foi possível ler dados do Google Sheets")
            use_google_sheets = False
        else:
            # Processa coluna Valor (remove R$ e converte para numérico)
            if 'Valor' in full_db.columns:
                full_db['Valor'] = full_db['Valor'].astype(str).str.replace('R$ ', '', regex=False)
                full_db['Valor'] = pd.to_numeric(full_db['Valor'], errors='coerce')
            
            # Processa coluna Data
            if 'Data' in full_db.columns:
                full_db['Data'] = pd.to_datetime(full_db['Data'], errors='coerce')
            
            print(f"Dados do Google Sheets carregados: {len(full_db)} registros")
    
    # Carrega configuração
    config = load_config()
    
    # Lê dados do arquivo CSV
    csv_path = config['files']['inter_data']
    print(f"Lendo dados do Inter ({csv_path})...")
    try:
        inter_db = pd.read_csv(csv_path)
        print(f"Dados do Inter carregados: {len(inter_db)} registros")
    except FileNotFoundError:
        print(f"ERRO: Arquivo {csv_path} não encontrado")
        return
    
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
    excel_path = config['files']['clients_data']
    print(f"Carregando dados dos clientes ({excel_path})...")
    try:
        clientes = pd.read_excel(excel_path)
        
        # Seleciona colunas necessárias
        db_clientes_data = clientes[['name', 'cpf_cnpj', 'state_name', 'fantasy_name', 'branch_of_activity',
                                   'cep', 'phone', 'email', 'city_name', 'street_name', 'status', 'bank_name', 
                                   'agency', 'account_dv', 'account_type']].copy()
        
        # Processa CPF/CNPJ dos clientes
        db_clientes_data = process_cpf_cnpj(db_clientes_data, 'cpf_cnpj')
        
        print(f"Dados dos clientes carregados: {len(db_clientes_data)} registros")
        
    except FileNotFoundError:
        print(f"AVISO: Arquivo '{excel_path}' não encontrado. Continuando sem dados de clientes.")
        db_clientes_data = pd.DataFrame()
    
    # Faz join com dados dos clientes
    if not db_clientes_data.empty:
        print("Join com dados dos clientes realizado")
        
        # Debug: verifica alguns CPFs específicos
        cpfs_debug = ['013.707.946-06', '259.644.388-06']
        for cpf in cpfs_debug:
            inter_match = db_mine[db_mine['cpf_cnpj'] == cpf]
            cliente_match = db_clientes_data[db_clientes_data['cpf_cnpj'] == cpf]
            
            print(f"\nDEBUG CPF {cpf}:")
            print(f"  - No Inter: {len(inter_match)} registros")
            if not inter_match.empty:
                print(f"    CPF formatado: '{inter_match.iloc[0]['cpf_cnpj']}'")
            print(f"  - Nos clientes: {len(cliente_match)} registros")
            if not cliente_match.empty:
                print(f"    CPF formatado: '{cliente_match.iloc[0]['cpf_cnpj']}'")
                print(f"    Nome: '{cliente_match.iloc[0]['name']}'")
        
        final_db = db_mine.merge(db_clientes_data, on='cpf_cnpj', how='left')
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
    
    # Os dados dos clientes já foram preenchidos no join anterior
    print("Dados dos clientes já incluídos via join")
    
    # Faz full join com os dados do Google Sheets
    if use_google_sheets and not full_db.empty:
        print("Realizando join com dados do Google Sheets...")
        
        # Garante que as colunas sejam compatíveis
        common_cols = list(set(full_db.columns) & set(result_db.columns))
        
        if common_cols:
            # Primeiro adiciona os dados do Google Sheets
            final_db_sheet = pd.concat([full_db, result_db], ignore_index=True, sort=False)
            
            # Remove duplicatas por Id, mantendo a ÚLTIMA ocorrência (dados mais recentes do Inter)
            if 'Id' in final_db_sheet.columns:
                print(f"Removendo duplicatas... Total antes: {len(final_db_sheet)}")
                final_db_sheet = final_db_sheet.drop_duplicates(subset=['Id'], keep='last')
                print(f"Total após remoção de duplicatas: {len(final_db_sheet)}")
        else:
            final_db_sheet = result_db.copy()
    else:
        final_db_sheet = result_db.copy()
    
    # Ordena por Data
    if 'Data' in final_db_sheet.columns:
        final_db_sheet = final_db_sheet.sort_values('Data', na_position='last')
    
    # Substitui 'Não se aplica' por 'Pix' em Meio de Pagamento
    if 'Meio de Pagamento' in final_db_sheet.columns:
        final_db_sheet['Meio de Pagamento'] = final_db_sheet['Meio de Pagamento'].replace('Não se aplica', 'Pix')
    
    print(f"Dados finais: {len(final_db_sheet)} registros")
    
    # Verifica se o CPF específico está nos dados finais
    cpf_procurado = '013.707.946-06'
    if 'CPF/CNPJ' in final_db_sheet.columns:
        cpf_encontrado = final_db_sheet[final_db_sheet['CPF/CNPJ'] == cpf_procurado]
        if not cpf_encontrado.empty:
            print(f"✅ CPF {cpf_procurado} encontrado nos dados finais: {len(cpf_encontrado)} registros")
            print("Detalhes:")
            print(cpf_encontrado[['CPF/CNPJ', 'Data', 'Valor', 'Meio de Pagamento', 'Bandeira', 'Nome']].to_string())
        else:
            print(f"❌ CPF {cpf_procurado} NÃO encontrado nos dados finais")
            
            # Verifica se está nos dados originais
            cpf_original = result_db[result_db['CPF/CNPJ'] == cpf_procurado]
            if not cpf_original.empty:
                print(f"   Mas está presente nos dados do Inter: {len(cpf_original)} registros")
            else:
                print(f"   Também não está nos dados do Inter")
    
    # Salva arquivo Excel localmente
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    excel_filename = f'transaction_with_type_and_brand_from_inter_db_{timestamp}.xlsx'
    
    try:
        final_db_sheet.to_excel(excel_filename, index=False)
        print(f"✅ Arquivo Excel salvo: {excel_filename}")
    except Exception as e:
        print(f"❌ Erro ao salvar Excel: {e}")
    
    # Escreve no Google Sheets apenas se configurado
    if use_google_sheets:
        print("Atualizando Google Sheets...")
        write_google_sheet(final_db_sheet, sheet_id, "Página2")
    else:
        print("⚠️ Google Sheets não configurado. Dados salvos apenas localmente.")
    
    print("Processamento concluído!")
    
    return final_db_sheet


if __name__ == "__main__":
    # Muda para o diretório do script
    os.chdir(Path(__file__).parent)
    
    print("=== INICIANDO SCRIPT ===")
    
    # Executa função principal
    result = main()
