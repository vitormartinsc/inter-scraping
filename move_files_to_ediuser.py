#!/usr/bin/env python3
"""
Script para mover arquivos TXT do bluedatauser para ediuser
"""
import paramiko
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def move_files_to_ediuser():
    """Move arquivos TXT do bluedatauser para ediuser"""
    
    print("🚀 Movendo arquivos TXT do bluedatauser para ediuser...")
    print("=" * 60)
    
    # Configurações para ambos os usuários
    host = os.getenv('SFTP_HOST')
    port = int(os.getenv('SFTP_PORT', 22))
    
    # BluedataUser (origem)
    user_blue = os.getenv('SFTP_USER_BLUEDATA')
    pass_blue = os.getenv('SFTP_PASS_BLUEDATA')
    
    # EdiUser (destino)
    user_edi = os.getenv('SFTP_USER')
    pass_edi = os.getenv('SFTP_PASS')
    
    remote_dir = 'uploads'
    
    try:
        # Conectar como bluedatauser para baixar arquivos
        print("🔄 Conectando como bluedatauser para listar arquivos...")
        ssh_blue = paramiko.SSHClient()
        ssh_blue.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_blue.connect(hostname=host, port=port, username=user_blue, password=pass_blue)
        sftp_blue = ssh_blue.open_sftp()
        sftp_blue.chdir(remote_dir)
        
        # Listar arquivos TXT do bluedatauser
        blue_files = sftp_blue.listdir('.')
        txt_files = [f for f in blue_files if f.endswith('.txt') and not f.startswith('test_')]
        
        print(f"📊 Encontrados {len(txt_files)} arquivos TXT para mover")
        
        if not txt_files:
            print("⚠️  Nenhum arquivo TXT encontrado para mover")
            return
        
        # Conectar como ediuser para upload
        print("🔄 Conectando como ediuser para fazer upload...")
        ssh_edi = paramiko.SSHClient()
        ssh_edi.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_edi.connect(hostname=host, port=port, username=user_edi, password=pass_edi)
        sftp_edi = ssh_edi.open_sftp()
        sftp_edi.chdir(remote_dir)
        
        print("-" * 60)
        
        moved_count = 0
        error_count = 0
        
        # Diretório temporário local
        temp_dir = "/tmp/sftp_migration"
        os.makedirs(temp_dir, exist_ok=True)
        
        for txt_file in txt_files:
            try:
                print(f"📤 Movendo: {txt_file}")
                
                # Download do bluedatauser
                local_temp_file = os.path.join(temp_dir, txt_file)
                sftp_blue.get(txt_file, local_temp_file)
                
                # Upload para ediuser
                sftp_edi.put(local_temp_file, txt_file)
                
                # Verificar se o upload foi bem-sucedido
                try:
                    edi_stat = sftp_edi.stat(txt_file)
                    blue_stat = sftp_blue.stat(txt_file)
                    
                    if edi_stat.st_size == blue_stat.st_size:
                        # Remover do bluedatauser após confirmação
                        sftp_blue.remove(txt_file)
                        print(f"✅ {txt_file} - movido com sucesso!")
                        moved_count += 1
                    else:
                        print(f"❌ {txt_file} - tamanhos diferentes, não removendo do origem")
                        error_count += 1
                        
                except Exception as e:
                    print(f"❌ {txt_file} - erro na verificação: {e}")
                    error_count += 1
                
                # Limpar arquivo temporário
                if os.path.exists(local_temp_file):
                    os.remove(local_temp_file)
                    
            except Exception as e:
                print(f"❌ Erro ao mover {txt_file}: {e}")
                error_count += 1
        
        # Limpar diretório temporário
        try:
            os.rmdir(temp_dir)
        except:
            pass
        
        # Verificar resultado final
        print("\n" + "=" * 60)
        print("📋 Arquivos no ediuser após migração:")
        try:
            edi_files = sftp_edi.listdir('.')
            edi_txt_files = [f for f in edi_files if f.endswith('.txt')]
            edi_txt_files.sort()
            
            for i, txt_file in enumerate(edi_txt_files, 1):
                file_stat = sftp_edi.stat(txt_file)
                file_size_kb = file_stat.st_size / 1024
                print(f"   {i:2d}. {txt_file} ({file_size_kb:.1f} KB)")
                
            print(f"\n📊 Total de arquivos TXT no ediuser: {len(edi_txt_files)}")
            
        except Exception as e:
            print(f"⚠️  Erro ao listar arquivos do ediuser: {e}")
        
        print("\n📋 Arquivos restantes no bluedatauser:")
        try:
            blue_files_final = sftp_blue.listdir('.')
            blue_txt_files_final = [f for f in blue_files_final if f.endswith('.txt')]
            blue_txt_files_final.sort()
            
            for i, txt_file in enumerate(blue_txt_files_final, 1):
                file_stat = sftp_blue.stat(txt_file)
                file_size_kb = file_stat.st_size / 1024
                print(f"   {i:2d}. {txt_file} ({file_size_kb:.1f} KB)")
                
            print(f"\n📊 Total de arquivos TXT restantes no bluedatauser: {len(blue_txt_files_final)}")
            
        except Exception as e:
            print(f"⚠️  Erro ao listar arquivos do bluedatauser: {e}")
        
        # Fechar conexões
        sftp_blue.close()
        ssh_blue.close()
        sftp_edi.close()
        ssh_edi.close()
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📈 RESUMO DA MIGRAÇÃO:")
        print(f"   ✅ Arquivos movidos: {moved_count}")
        print(f"   ❌ Erros: {error_count}")
        print(f"   📊 Total processado: {moved_count + error_count}")
        
        if error_count == 0:
            print(f"\n🎉 Migração concluída com sucesso!")
        else:
            print(f"\n⚠️  Migração concluída com {error_count} erro(s)")
            
    except Exception as e:
        print(f"❌ Erro na conexão SFTP: {e}")
        return False
    
    return True

if __name__ == "__main__":
    move_files_to_ediuser()
