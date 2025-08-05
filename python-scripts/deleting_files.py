import os

download_dir = r'C:\Users\servi\Downloads'

# Percorre os arquivos da pasta
for arquivo in os.listdir(download_dir):
    if arquivo.startswith("PAGO") and arquivo.endswith(".csv"):
        caminho_arquivo = os.path.join(download_dir, arquivo)
        try:
            os.remove(caminho_arquivo)
            print(f"Arquivo removido: {arquivo}")
        except Exception as e:
            print(f"Erro ao remover {arquivo}: {e}")
