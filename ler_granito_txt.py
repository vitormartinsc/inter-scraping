import paramiko

import os
import csv
from dotenv import load_dotenv

load_dotenv()

def parse_transacao(linha):
    return {
        'tipo_registro': linha[0:1],
        'sequencial': linha[1:7],
        'cnpj_estab': linha[7:21],
        'id_transacao': linha[21:33],
        'data_transacao': linha[33:41],
        'hora_transacao': linha[41:47],
        'tipo_transacao': linha[47:48],
        'bandeira': linha[48:50],
        'valor_bruto': linha[50:60],
        'valor_taxa_adm': linha[60:70],
        'valor_taxa_antecip': linha[70:80],
        'valor_liquido': linha[80:90],
        'qtd_parcelas': linha[90:92],
        'num_parcela': linha[92:94],
        'valor_bruto_parcela': linha[94:104],
        'valor_taxa_adm_parcela': linha[104:114],
        'valor_taxa_antecip_parcela': linha[114:124],
        'valor_liquido_parcela': linha[124:134],
        'data_lancamento': linha[134:142],
        'tipo_lancamento': linha[142:143],
        'id_transacao_original': linha[143:155],
        'tipo_ajuste': linha[155:156],
        'iof': linha[156:166],
        'data_lancamento_original': linha[166:174],
        'cod_simulacao_antecip': linha[174:184],
        'reservado': linha[184:187],
        'origem_transacao': linha[187:188],
        'id_transacao_ecommerce': linha[188:224],
        'merchant_order_id': linha[224:264],
        'cod_retorno_ecommerce': linha[264:271],
        'cnpj_principal': linha[271:285],
        'vago': linha[285:297],
        'cnpj_parceiro': linha[297:311],
        'banco': linha[311:314],
        'agencia': linha[314:319],
        'conta': linha[319:331],
        'taxa_mdr': linha[331:335],
        'taxa_antecipacao': linha[335:339],
        'tipo_transacao2': linha[339:342],
        'autorizacao': linha[342:354],
        'nsu_host': linha[354:386],
        'recorrencia': linha[386:396],
        'id_projeto': linha[396:400],
        'ref_pix': linha[400:436],
        'nsu_pdv': linha[437:443],
        'pdv': linha[443:449],
        'doc_vinculado': linha[449:489],
    }

def interpretar_tipo_transacao(codigo):
    return {
        '0': 'Não se aplica',
        '1': 'Crédito',
        '2': 'Débito',
    }.get(codigo, codigo)

def interpretar_bandeira(codigo):
    return {
        '01': 'VISA',
        '02': 'MASTERCARD',
        '03': 'VISA ELECTRON',
        '04': 'MAESTRO',
        '12': 'ELO CRÉDITO',
        '13': 'ELO DÉBITO',
        '16': 'AMERICAN EXPRESS',
        '19': 'HIPERCARD',
        '20': 'HIPER',
        '55': 'TICKET RESTAURANTE',
        '56': 'TICKET ALIMENTACAO',
        '57': 'TICKET CULTURA',
        '58': 'TICKET',
        '65': 'VR AUTO',
        '66': 'VR ALIMENTACAO',
        '67': 'VR REFEICAO',
        '68': 'VR CULTURA',
        '84': 'SODEXO ALIMENTAC',
        '85': 'SODEXO REFEICAO',
        '86': 'SODEXO COMBUSTIVEL',
        '87': 'SODEXO CULTURA',
        '88': 'SODEXO GIFT',
        '89': 'SODEXO PREMIUM',
    }.get(codigo.zfill(2), codigo)

def baixar_txt_e_gerar_csv():
    # Configurações SFTP
    host = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", 22))
    username = os.getenv("SFTP_USER")
    password = os.getenv("SFTP_PASS")
    remote_dir = os.getenv("SFTP_REMOTE_DIR", "/uploads")
    local_txt_dir = os.getenv("TXT_DIR", "./database/stpf_data")
    local_csv_dir = os.getenv("CSV_DIR", "./database/inter_stpf_data")
    os.makedirs(local_txt_dir, exist_ok=True)
    os.makedirs(local_csv_dir, exist_ok=True)

    # Lista arquivos já processados (csv gerado)
    arquivos_processados = set(
        os.path.splitext(f)[0] for f in os.listdir(local_csv_dir) if f.lower().endswith('.csv')
    )

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.chdir(remote_dir)
        arquivos_remotos = sftp.listdir()
        txts = [arq for arq in arquivos_remotos if arq.lower().endswith(".txt")]
        novos_txts = [arq for arq in txts if os.path.splitext(arq)[0] not in arquivos_processados]

        if not novos_txts:
            print("Nenhum arquivo .txt novo para baixar e processar.")
        else:
            for arq in novos_txts:
                remote_path = f"{remote_dir}/{arq}"
                local_txt_path = os.path.join(local_txt_dir, arq)
                print(f"⬇️  Baixando: {arq}")
                sftp.get(remote_path, local_txt_path)
                gerar_csv_do_txt(local_txt_path, local_csv_dir)
            print("✅ Todos os arquivos .txt novos foram baixados e processados!")
        sftp.close()
        transport.close()
    except Exception as e:
        print(f"❌ Erro: {e}")

def gerar_csv_do_txt(caminho_txt, pasta_csv):
    registros = []
    with open(caminho_txt, encoding='utf-8') as f:
        for linha in f:
            linha = linha.rstrip('\r\n')
            if not linha:
                continue
            tipo = linha[0]
            if tipo == '1' or tipo == '5':
                dados = parse_transacao(linha)
                registro = {
                    'Data': f"{dados['data_transacao'][6:8]}/{dados['data_transacao'][4:6]}/{dados['data_transacao'][0:4]}",
                    'Bandeira': interpretar_bandeira(dados['bandeira']),
                    'Valor': float(dados['valor_bruto'])/100 if dados['valor_bruto'].isdigit() else dados['valor_bruto'],
                    'cpf_cnpj': dados['cnpj_estab'].strip(),
                    'nome': '',  # Nome não está no txt, pode ser preenchido depois
                    'Tipo': interpretar_tipo_transacao(dados['tipo_transacao']),
                    'Numero Parcelas': int(dados['qtd_parcelas']) if dados['qtd_parcelas'].isdigit() else dados['qtd_parcelas'],
                    'Id': dados['id_transacao'],
                }
                registros.append(registro)
    if registros:
        base_nome = os.path.splitext(os.path.basename(caminho_txt))[0]
        csv_path = os.path.join(pasta_csv, base_nome + '.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'Data', 'Bandeira', 'Valor', 'cpf_cnpj', 'nome', 'Tipo', 'Numero Parcelas', 'Id'
            ])
            writer.writeheader()
            writer.writerows(registros)
        print(f'CSV gerado em: {csv_path}')
    else:
        print(f'Nenhum registro encontrado em {caminho_txt}.')

def merge_db_inter(pasta_csv, arquivo_saida):
    import pandas as pd
    arquivos = [os.path.join(pasta_csv, f) for f in os.listdir(pasta_csv) if f.lower().endswith('.csv')]
    if not arquivos:
        print('Nenhum arquivo CSV encontrado na pasta.')
        return
    dfs = []
    for arq in arquivos:
        try:
            df = pd.read_csv(arq)
            dfs.append(df)
        except Exception as e:
            print(f'Erro ao ler {arq}: {e}')
    if not dfs:
        print('Nenhum dado válido para mesclar.')
        return
    df_final = pd.concat(dfs, ignore_index=True)
    # Renomear e reformatar colunas
    df_final = df_final.rename(columns={
        'Data': 'date',
        'Bandeira': 'brand',
        'Valor': 'value',
        'cpf_cnpj': 'cpf_cnpj',
        'nome': 'nome',
        'Tipo': 'payment_method',
        'Numero Parcelas': 'installments',
        'Id': 'Id'
    })
    # Converter data para yyyy-mm-dd
    import datetime
    def parse_date(d):
        try:
            return datetime.datetime.strptime(d, '%d/%m/%Y').strftime('%Y-%m-%d')
        except:
            return d
    df_final['date'] = df_final['date'].astype(str).apply(parse_date)
    # Garantir tipos
    df_final['value'] = pd.to_numeric(df_final['value'], errors='coerce')
    df_final['installments'] = pd.to_numeric(df_final['installments'], errors='coerce')
    # Distinct by Id
    df_final = df_final.drop_duplicates(subset=['Id'])
    # Reordenar colunas
    col_order = ['date', 'brand', 'value', 'cpf_cnpj', 'nome', 'payment_method', 'installments', 'Id']
    df_final = df_final[[c for c in col_order if c in df_final.columns]]
    df_final.to_csv(arquivo_saida, index=False, encoding='utf-8')
    print(f'Mesclagem concluída! Arquivo salvo em: {arquivo_saida}')

if __name__ == '__main__':
    baixar_txt_e_gerar_csv()
    merge_db_inter('./database/inter_stpf_data', 'db_inter_merged.csv')
