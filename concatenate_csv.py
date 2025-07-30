import pandas as pd
import os
from datetime import datetime

def process_and_concatenate_csv():
    # Arquivo atual que precisa ser processado
    current_file = "database/040525196-39_Cícero Sousa Araújo Filho_27-07-2025.csv"
    
    # Arquivo de destino
    merged_file = "db_inter_merged.csv"
    
    # Ler o arquivo atual
    print(f"Lendo arquivo: {current_file}")
    df_current = pd.read_csv(current_file, sep=';')
    
    print("Colunas do arquivo atual:", df_current.columns.tolist())
    print("Primeiras linhas do arquivo atual:")
    print(df_current.head())
    
    # Extrair CPF do nome do arquivo
    cpf_cnpj = current_file.split('/')[-1].split('_')[0]  # "040525196-39"
    nome = current_file.split('/')[-1].split('_')[1]  # "Cícero Sousa Araújo Filho"
    
    print(f"CPF/CNPJ extraído: {cpf_cnpj}")
    print(f"Nome extraído: {nome}")
    
    # Processar os dados para o formato do db_inter_merged
    processed_data = []
    
    for _, row in df_current.iterrows():
        # Converter data de DD/MM/YYYY HH:MM:SS para YYYY-MM-DD
        date_str = row['Data e hora'].split(' ')[0]  # Pega só a parte da data
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        
        # Mapear tipo de pagamento
        tipo = row['Tipo']
        if 'Debito' in tipo:
            payment_method = 'Débito'
        elif 'Credito' in tipo:
            payment_method = 'Crédito'
        else:
            payment_method = 'Não se aplica'
        
        # Converter valor de "33,00" para 33.0
        valor_str = str(row['Valor']).replace(',', '.')
        valor = float(valor_str)
        
        # Bandeira
        bandeira = row['Bandeira'] if pd.notna(row['Bandeira']) else '00'
        
        # Número de parcelas
        parcelas = int(row['Numero Parcelas']) if pd.notna(row['Numero Parcelas']) else 0
        
        # ID
        transaction_id = row['Id']
        
        processed_data.append({
            'date': formatted_date,
            'brand': bandeira,
            'value': valor,
            'cpf_cnpj': cpf_cnpj,
            'nome': nome,
            'payment_method': payment_method,
            'installments': parcelas,
            'Id': transaction_id
        })
    
    # Criar DataFrame com os dados processados
    df_processed = pd.DataFrame(processed_data)
    
    print("Dados processados:")
    print(df_processed.head())
    
    # Ler o arquivo merged existente
    if os.path.exists(merged_file):
        print(f"Lendo arquivo existente: {merged_file}")
        df_merged = pd.read_csv(merged_file)
        
        # Concatenar os dados
        df_final = pd.concat([df_merged, df_processed], ignore_index=True)
        
        print(f"Total de linhas antes: {len(df_merged)}")
        print(f"Linhas adicionadas: {len(df_processed)}")
        print(f"Total de linhas depois: {len(df_final)}")
    else:
        print(f"Arquivo {merged_file} não existe, criando novo arquivo")
        df_final = df_processed
    
    # Salvar o arquivo final
    df_final.to_csv(merged_file, index=False)
    print(f"Arquivo salvo: {merged_file}")
    
    # Mostrar as últimas linhas para verificação
    print("Últimas linhas do arquivo final:")
    print(df_final.tail())

if __name__ == "__main__":
    process_and_concatenate_csv()
