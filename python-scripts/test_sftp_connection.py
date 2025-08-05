#!/usr/bin/env python3
"""
Script para testar as conexões SFTP configuradas
"""
import paramiko
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def test_sftp_connection(host, port, username, password, remote_dir):
    """Testa a conexão SFTP"""
    try:
        # Criar cliente SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Conectar
        print(f"🔄 Conectando ao servidor {host} como {username}...")
        ssh.connect(hostname=host, port=port, username=username, password=password)
        
        # Criar cliente SFTP
        sftp = ssh.open_sftp()
        
        # Testar listagem do diretório
        print(f"📁 Listando diretório remoto: {remote_dir}")
        try:
            files = sftp.listdir(remote_dir)
            print(f"✅ Arquivos encontrados: {files}")
        except FileNotFoundError:
            print(f"⚠️  Diretório {remote_dir} não encontrado, tentando criar...")
            try:
                sftp.mkdir(remote_dir)
                print(f"✅ Diretório {remote_dir} criado com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao criar diretório: {e}")
        
        # Testar upload de um arquivo simples
        test_content = f"Teste de conexão SFTP para {username} - {host}"
        local_test_file = f"/tmp/test_{username}.txt"
        remote_test_file = f"{remote_dir}/test_{username}.txt"
        
        # Criar arquivo local
        with open(local_test_file, 'w') as f:
            f.write(test_content)
        
        # Upload do arquivo
        print(f"📤 Fazendo upload do arquivo de teste...")
        sftp.put(local_test_file, remote_test_file)
        print(f"✅ Upload realizado com sucesso!")
        
        # Verificar se o arquivo foi enviado
        files = sftp.listdir(remote_dir)
        if f"test_{username}.txt" in files:
            print(f"✅ Arquivo de teste encontrado no servidor!")
        
        # Limpar
        os.remove(local_test_file)
        sftp.close()
        ssh.close()
        
        print(f"✅ Teste de conexão SFTP para {username} PASSOU!\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão SFTP para {username}: {e}\n")
        return False

def main():
    print("🚀 Testando configurações SFTP do servidor...")
    print("=" * 50)
    
    # Configurações do ediuser
    host1 = os.getenv('SFTP_HOST')
    port1 = int(os.getenv('SFTP_PORT', 22))
    user1 = os.getenv('SFTP_USER')
    pass1 = os.getenv('SFTP_PASS')
    dir1 = os.getenv('SFTP_REMOTE_DIR')
    
    # Configurações do bluedatauser
    host2 = os.getenv('SFTP_HOST_BLUEDATA')
    port2 = int(os.getenv('SFTP_PORT_BLUEDATA', 22))
    user2 = os.getenv('SFTP_USER_BLUEDATA')
    pass2 = os.getenv('SFTP_PASS_BLUEDATA')
    dir2 = os.getenv('SFTP_REMOTE_DIR_BLUEDATA')
    
    print(f"Host: {host1}")
    print(f"Usuários: {user1}, {user2}")
    print("=" * 50)
    
    # Testar conexões
    results = []
    
    print(f"1️⃣ Testando usuário: {user1}")
    result1 = test_sftp_connection(host1, port1, user1, pass1, dir1)
    results.append(("ediuser", result1))
    
    print(f"2️⃣ Testando usuário: {user2}")
    result2 = test_sftp_connection(host2, port2, user2, pass2, dir2)
    results.append(("bluedatauser", result2))
    
    # Resumo final
    print("=" * 50)
    print("📊 RESUMO DOS TESTES:")
    for user, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {user}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 Todos os testes passaram! O servidor SFTP está configurado corretamente!")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique as configurações.")

if __name__ == "__main__":
    main()
