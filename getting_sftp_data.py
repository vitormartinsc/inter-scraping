import paramiko
import os

# 🔐 Credenciais do servidor SFTP
host = "18.188.31.230"
port = 22
username = "ediuser"
password = "InterEssencial@25"
remote_dir = "/uploads"
local_dir = "./database/stpf_data"  # Pasta local onde os arquivos serão salvos

# ✅ Cria pasta local se não existir
os.makedirs(local_dir, exist_ok=True)

# 🚀 Conectar e baixar arquivos .txt
def baixar_txt():
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.chdir(remote_dir)
        arquivos_remotos = sftp.listdir()

        txts = [arq for arq in arquivos_remotos if arq.lower().endswith(".txt")]

        if not txts:
            print("Nenhum arquivo .txt encontrado no servidor.")
        else:
            for arq in txts:
                remote_path = f"{remote_dir}/{arq}"
                local_path = os.path.join(local_dir, arq)
                print(f"⬇️  Baixando: {arq}")
                sftp.get(remote_path, local_path)

            print("✅ Todos os arquivos .txt foram baixados!")

        sftp.close()
        transport.close()

    except Exception as e:
        print(f"❌ Erro: {e}")

# ▶️ Executar
baixar_txt()
