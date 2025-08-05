#!/usr/bin/env python3
"""
Script para baixar arquivos GRANITO do S3 e processar usando ler_granito_txt.py
"""

import boto3
import os
import tempfile
import zipfile
from datetime import datetime
from ler_granito_txt import gerar_csv_do_txt, merge_db_inter

def listar_arquivos_s3(bucket_name, prefix="granito_auto/"):
    """Lista todos os arquivos GRANITO no S3"""
    s3 = boto3.client('s3')
    
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' not in response:
            print(f"❌ Nenhum arquivo encontrado em s3://{bucket_name}/{prefix}")
            return []
        
        arquivos = []
        for obj in response['Contents']:
            key = obj['Key']
            size = obj['Size']
            modified = obj['LastModified']
            
            # Filtrar apenas arquivos .txt
            if key.lower().endswith('.txt'):
                arquivos.append({
                    'key': key,
                    'size': size,
                    'modified': modified,
                    'filename': os.path.basename(key)
                })
        
        return sorted(arquivos, key=lambda x: x['modified'], reverse=True)
    
    except Exception as e:
        print(f"❌ Erro ao listar arquivos S3: {e}")
        return []

def baixar_arquivo_s3(bucket_name, s3_key, local_path):
    """Baixa um arquivo específico do S3"""
    s3 = boto3.client('s3')
    
    try:
        print(f"⬇️  Baixando: {os.path.basename(s3_key)}")
        s3.download_file(bucket_name, s3_key, local_path)
        return True
    except Exception as e:
        print(f"❌ Erro ao baixar {s3_key}: {e}")
        return False

def baixar_todos_arquivos_s3(bucket_name, prefix="granito_auto/", local_dir="./database/stpf_data"):
    """Baixa todos os arquivos GRANITO do S3"""
    
    # Criar diretório local se não existir
    os.makedirs(local_dir, exist_ok=True)
    
    # Listar arquivos no S3
    print(f"📋 Listando arquivos em s3://{bucket_name}/{prefix}...")
    arquivos_s3 = listar_arquivos_s3(bucket_name, prefix)
    
    if not arquivos_s3:
        print("❌ Nenhum arquivo .txt encontrado no S3!")
        return []
    
    print(f"📊 Encontrados {len(arquivos_s3)} arquivos .txt no S3")
    
    # Verificar quais arquivos já existem localmente
    arquivos_locais = set(os.listdir(local_dir)) if os.path.exists(local_dir) else set()
    
    arquivos_baixados = []
    arquivos_novos = 0
    
    for arquivo in arquivos_s3:
        filename = arquivo['filename']
        local_path = os.path.join(local_dir, filename)
        
        # Verificar se o arquivo já existe
        if filename in arquivos_locais:
            print(f"⏭️  Pulando (já existe): {filename}")
            arquivos_baixados.append(local_path)
            continue
        
        # Baixar arquivo
        if baixar_arquivo_s3(bucket_name, arquivo['key'], local_path):
            arquivos_baixados.append(local_path)
            arquivos_novos += 1
        
    print(f"✅ Download concluído! {arquivos_novos} novos arquivos baixados.")
    print(f"📁 Total de arquivos disponíveis: {len(arquivos_baixados)}")
    
    return arquivos_baixados

def processar_arquivos_baixados():
    """Processa os arquivos baixados do S3 usando as funções do ler_granito_txt.py"""
    
    local_txt_dir = "./database/stpf_data"
    local_csv_dir = "./database/inter_stpf_data"
    
    print(f"\n🔄 Processando arquivos TXT...")
    
    # Criar diretório CSV se não existir
    os.makedirs(local_csv_dir, exist_ok=True)
    
    # Verificar se existem arquivos TXT
    if not os.path.exists(local_txt_dir):
        print(f"❌ Pasta {local_txt_dir} não encontrada!")
        return False
    
    arquivos_txt = [f for f in os.listdir(local_txt_dir) if f.lower().endswith('.txt')]
    
    if not arquivos_txt:
        print(f"❌ Nenhum arquivo TXT encontrado em {local_txt_dir}")
        return False
    
    # Lista arquivos já processados (csv gerado)
    arquivos_processados = set(
        os.path.splitext(f)[0] for f in os.listdir(local_csv_dir) if f.lower().endswith('.csv')
    )
    
    # Filtrar apenas arquivos novos
    novos_arquivos = [arq for arq in arquivos_txt if os.path.splitext(arq)[0] not in arquivos_processados]
    
    if not novos_arquivos:
        print("✅ Todos os arquivos TXT já foram processados!")
    else:
        print(f"📁 Processando {len(novos_arquivos)} arquivos novos...")
        
        for arquivo in novos_arquivos:
            caminho_txt = os.path.join(local_txt_dir, arquivo)
            print(f"🔄 Processando: {arquivo}")
            gerar_csv_do_txt(caminho_txt, local_csv_dir)
        
        print(f"✅ {len(novos_arquivos)} arquivos processados com sucesso!")
    
    return True

def gerar_relatorio_final():
    """Gera o arquivo CSV mesclado final"""
    
    print(f"\n📊 Gerando arquivo final mesclado...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_final = f"db_inter_merged_s3_{timestamp}.csv"
    
    merge_db_inter('./database/inter_stpf_data', arquivo_final)
    
    if os.path.exists(arquivo_final):
        # Mostrar estatísticas do arquivo final
        import pandas as pd
        df = pd.read_csv(arquivo_final)
        
        print(f"\n📈 ESTATÍSTICAS DO ARQUIVO FINAL:")
        print(f"   📄 Arquivo: {arquivo_final}")
        print(f"   📊 Total de transações: {len(df)}")
        print(f"   📅 Período: {df['date'].min()} a {df['date'].max()}")
        print(f"   💰 Valor total: R$ {df['value'].sum():,.2f}")
        print(f"   🏦 Bandeiras únicas: {df['brand'].nunique()}")
        print(f"   👥 CPF/CNPJ únicos: {df['cpf_cnpj'].nunique()}")
        
        return arquivo_final
    
    return None

def main():
    """Função principal"""
    
    print("🚀 DOWNLOAD E PROCESSAMENTO S3 - GRANITO")
    print("=" * 50)
    
    # Configurações
    bucket_name = "essencial-form-files"
    prefix = "granito_auto/"
    
    try:
        # 1. Baixar arquivos do S3
        print("📥 ETAPA 1: Download do S3")
        arquivos_baixados = baixar_todos_arquivos_s3(bucket_name, prefix)
        
        if not arquivos_baixados:
            print("❌ Nenhum arquivo foi baixado. Encerrando.")
            return
        
        # 2. Processar arquivos TXT -> CSV
        print("\n🔄 ETAPA 2: Processamento TXT -> CSV")
        if not processar_arquivos_baixados():
            print("❌ Erro no processamento. Encerrando.")
            return
        
        # 3. Gerar arquivo final mesclado
        print("\n📋 ETAPA 3: Geração do arquivo final")
        arquivo_final = gerar_relatorio_final()
        
        if arquivo_final:
            print(f"\n🎉 PROCESSAMENTO CONCLUÍDO!")
            print(f"📄 Arquivo final disponível: {arquivo_final}")
        else:
            print("❌ Erro na geração do arquivo final.")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
