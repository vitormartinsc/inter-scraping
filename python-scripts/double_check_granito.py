import os
import paramiko
import pandas as pd
from ler_granito_txt import parse_transacao, interpretar_bandeira, interpretar_tipo_transacao
from dotenv import load_dotenv

load_dotenv()

def ler_todos_txt_e_gerar_dataframe():
    # Configurações SFTP
    host = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", 22))
    username = os.getenv("SFTP_USER")
    password = os.getenv("SFTP_PASS")
    remote_dir = os.getenv("SFTP_REMOTE_DIR", "/uploads")
    local_tmp_dir = "./database/tmp_granito_check"
    os.makedirs(local_tmp_dir, exist_ok=True)

    # Conecta e baixa todos os .txt
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(remote_dir)
    arquivos_remotos = sftp.listdir()
    txts = [arq for arq in arquivos_remotos if arq.lower().endswith(".txt")]

    todos_registros = []
    for arq in txts:
        remote_path = f"{remote_dir}/{arq}"
        local_path = os.path.join(local_tmp_dir, arq)
        print(f"⬇️  Baixando: {arq}")
        sftp.get(remote_path, local_path)
        # Lê e processa o arquivo
        with open(local_path, encoding='utf-8') as f:
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
                        'nome': '',  # Nome não está no txt
                        'Tipo': interpretar_tipo_transacao(dados['tipo_transacao']),
                        'Numero Parcelas': int(dados['qtd_parcelas']) if dados['qtd_parcelas'].isdigit() else dados['qtd_parcelas'],
                        'Id': dados['id_transacao'],
                        'Arquivo': arq
                    }
                    todos_registros.append(registro)
    sftp.close()
    transport.close()
    df = pd.DataFrame(todos_registros)
    print(f"Total de registros lidos: {len(df)}")
    return df

if __name__ == "__main__":
    df = ler_todos_txt_e_gerar_dataframe()
    df.to_csv("./database/double_check_granito.csv", index=False, encoding="utf-8")
    print("Arquivo double_check_granito.csv gerado!")
