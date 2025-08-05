import pysftp

# Configurações de acesso
hostname = "18.188.31.230"
username = "bluedatauser"
password = "BlueData@25"
remote_path = "/home/ediuser/uploads"

# Ignorar verificação de host (usado para teste, não recomendado em produção)
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # ⚠️ Cuidado: desabilita verificação de chave do host

try:
    with pysftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts) as sftp:
        print("✅ Conectado com sucesso!")

        # Mudar para a pasta desejada
        if sftp.exists(remote_path):
            sftp.cwd(remote_path)
            print(f"📂 Conteúdo de {remote_path}:")
            for arquivo in sftp.listdir():
                print("  -", arquivo)
                local_path = f"./{arquivo}"
                sftp.get(arquivo, local_path)
                print(f"    ⬇️  Baixado para {local_path}")
        else:
            print("❌ A pasta remota não existe:", remote_path)

except Exception as e:
    print("❌ Erro ao conectar ou acessar o servidor SFTP:", str(e))
