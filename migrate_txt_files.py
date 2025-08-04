#!/usr/bin/env python3
"""
Script para migrar arquivos TXT da pasta stpf_data para o servidor SFTP
"""
import paramiko
import os
import glob
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def upload_txt_files_to_sftp():
    """Faz upload de todos os arquivos TXT para o servidor SFTP"""
    
    # Configurações SFTP para BluedataUser (Granito)
    host = os.getenv('SFTP_HOST_BLUEDATA')
    port = int(os.getenv('SFTP_PORT_BLUEDATA', 22))
    username = os.getenv('SFTP_USER_BLUEDATA')
    password = os.getenv('SFTP_PASS_BLUEDATA')
    remote_dir = os.getenv('SFTP_REMOTE_DIR_BLUEDATA', 'uploads')
    
    # Diretório local com os arquivos TXT
    local_txt_dir = "./database/stpf_data"
    
    print("🚀 Iniciando migração de arquivos TXT para o servidor SFTP...")
    print("=" * 60)
    print(f"📂 Pasta local: {local_txt_dir}")
    print(f"🌐 Servidor: {username}@{host}:{port}")
    print(f"📁 Diretório remoto: {remote_dir}")
    print("=" * 60)
    
    try:
        # Conectar ao servidor SFTP
        print("🔄 Conectando ao servidor SFTP...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=username, password=password)
        sftp = ssh.open_sftp()
        
        # Mudar para o diretório remoto
        sftp.chdir(remote_dir)
        
        # Encontrar todos os arquivos TXT
        txt_files = glob.glob(os.path.join(local_txt_dir, "*.txt"))
        txt_files.sort()  # Ordenar por nome
        
        if not txt_files:
            print("⚠️  Nenhum arquivo TXT encontrado na pasta local!")
            return
        
        print(f"📊 Encontrados {len(txt_files)} arquivos TXT para fazer upload")
        print("-" * 60)
        
        uploaded_count = 0
        skipped_count = 0
        error_count = 0
        
        for local_file in txt_files:
            filename = os.path.basename(local_file)
            remote_file = filename
            
            try:
                # Verificar se o arquivo já existe no servidor
                try:
                    remote_stat = sftp.stat(remote_file)
                    local_stat = os.stat(local_file)
                    
                    # Se o arquivo remoto é mais recente ou igual, pular
                    if remote_stat.st_mtime >= local_stat.st_mtime:
                        print(f"⏭️  {filename} - já existe (mais recente)")
                        skipped_count += 1
                        continue
                except FileNotFoundError:
                    # Arquivo não existe no servidor, fazer upload
                    pass
                
                # Fazer upload do arquivo
                print(f"📤 Uploading: {filename}")
                sftp.put(local_file, remote_file)
                
                # Obter tamanho do arquivo para feedback
                file_size = os.path.getsize(local_file)
                file_size_kb = file_size / 1024
                print(f"✅ {filename} - {file_size_kb:.1f} KB enviado com sucesso!")
                
                uploaded_count += 1
                
            except Exception as e:
                print(f"❌ Erro ao enviar {filename}: {e}")
                error_count += 1
        
        # Listar arquivos no servidor para confirmação
        print("\n" + "=" * 60)
        print("📋 Arquivos no servidor após upload:")
        try:
            remote_files = sftp.listdir('.')
            txt_files_remote = [f for f in remote_files if f.endswith('.txt')]
            txt_files_remote.sort()
            
            for i, remote_file in enumerate(txt_files_remote, 1):
                file_stat = sftp.stat(remote_file)
                file_size_kb = file_stat.st_size / 1024
                print(f"   {i:2d}. {remote_file} ({file_size_kb:.1f} KB)")
                
            print(f"\n📊 Total de arquivos TXT no servidor: {len(txt_files_remote)}")
            
        except Exception as e:
            print(f"⚠️  Erro ao listar arquivos remotos: {e}")
        
        # Fechar conexões
        sftp.close()
        ssh.close()
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📈 RESUMO DA MIGRAÇÃO:")
        print(f"   ✅ Arquivos enviados: {uploaded_count}")
        print(f"   ⏭️  Arquivos pulados: {skipped_count}")
        print(f"   ❌ Erros: {error_count}")
        print(f"   📊 Total processado: {uploaded_count + skipped_count + error_count}")
        
        if error_count == 0:
            print(f"\n🎉 Migração concluída com sucesso!")
        else:
            print(f"\n⚠️  Migração concluída com {error_count} erro(s)")
            
    except Exception as e:
        print(f"❌ Erro na conexão SFTP: {e}")
        return False
    
    return True

if __name__ == "__main__":
    upload_txt_files_to_sftp()
