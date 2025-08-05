#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processamento de dados Granito - BluedataUser
Desenvolvido para conexão SFTP e conversão de arquivos TXT para CSV

ATENÇÃO: Configure o arquivo .env com suas credenciais antes de usar!

Instruções de uso:
1. Copie .env.example para .env e configure as credenciais
2. Execute o script: python script_bluedata.py
3. Os arquivos CSV serão gerados na pasta especificada
"""

import paramiko
import os
import csv
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações SFTP (agora via variáveis de ambiente para BlueData)
SFTP_HOST = os.getenv("SFTP_HOST_BLUEDATA")
SFTP_PORT = int(os.getenv("SFTP_PORT_BLUEDATA", 22))
SFTP_USER = os.getenv("SFTP_USER_BLUEDATA")
SFTP_PASS = os.getenv("SFTP_PASS_BLUEDATA")
SFTP_REMOTE_DIR = os.getenv("SFTP_REMOTE_DIR_BLUEDATA")

# Verificação de credenciais
if not all([SFTP_HOST, SFTP_USER, SFTP_PASS, SFTP_REMOTE_DIR]):
    print("❌ ERRO: Credenciais SFTP BlueData não configuradas!")
    print("Por favor, configure as variáveis SFTP_HOST_BLUEDATA, SFTP_USER_BLUEDATA,")
    print("SFTP_PASS_BLUEDATA e SFTP_REMOTE_DIR_BLUEDATA no arquivo .env")
    exit(1)

# =============================================================================
# CONFIGURAÇÕES - ALTERE CONFORME NECESSÁRIO
# =============================================================================

# Configurações locais
LOCAL_TXT_DIR = "./dados_txt"      # Pasta para salvar arquivos TXT baixados
LOCAL_CSV_DIR = "./dados_csv"      # Pasta para salvar arquivos CSV gerados

# =============================================================================
# FUNÇÕES DE PROCESSAMENTO
# =============================================================================

def parse_transacao(linha):
    """
    Extrai os dados de uma linha de transação do arquivo TXT do Granito
    """
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
    """Converte código de tipo de transação para texto"""
    return {
        '0': 'Não se aplica',
        '1': 'Crédito',
        '2': 'Débito',
    }.get(codigo, codigo)

def interpretar_bandeira(codigo):
    """Converte código de bandeira para nome da bandeira"""
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

def conectar_sftp():
    """Estabelece conexão com o servidor SFTP"""
    try:
        print(f"🔗 Conectando ao servidor SFTP: {SFTP_HOST}")
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("✅ Conexão SFTP estabelecida com sucesso!")
        return transport, sftp
    except Exception as e:
        print(f"❌ Erro ao conectar ao SFTP: {e}")
        return None, None

def baixar_arquivos_txt(sftp):
    """Baixa todos os arquivos TXT da pasta remota"""
    try:
        # Criar diretório local se não existir
        os.makedirs(LOCAL_TXT_DIR, exist_ok=True)
        
        # Navegar para pasta remota
        sftp.chdir(SFTP_REMOTE_DIR)
        arquivos_remotos = sftp.listdir()
        
        # Filtrar apenas arquivos .txt
        txts = [arq for arq in arquivos_remotos if arq.lower().endswith(".txt")]
        
        if not txts:
            print("⚠️  Nenhum arquivo .txt encontrado na pasta remota.")
            return []
        
        print(f"📁 Encontrados {len(txts)} arquivos .txt na pasta remota")
        
        # Baixar cada arquivo
        arquivos_baixados = []
        for arq in txts:
            remote_path = f"{SFTP_REMOTE_DIR}/{arq}"
            local_path = os.path.join(LOCAL_TXT_DIR, arq)
            
            print(f"⬇️  Baixando: {arq}")
            sftp.get(remote_path, local_path)
            arquivos_baixados.append(local_path)
            
        print(f"✅ {len(arquivos_baixados)} arquivos baixados com sucesso!")
        return arquivos_baixados
        
    except Exception as e:
        print(f"❌ Erro ao baixar arquivos: {e}")
        return []

def converter_txt_para_csv(caminho_txt):
    """Converte um arquivo TXT para CSV"""
    try:
        # Criar diretório CSV se não existir
        os.makedirs(LOCAL_CSV_DIR, exist_ok=True)
        
        registros = []
        nome_arquivo = os.path.splitext(os.path.basename(caminho_txt))[0]
        
        print(f"🔄 Processando: {nome_arquivo}.txt")
        
        with open(caminho_txt, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.rstrip('\r\n')
                if not linha:
                    continue
                
                # Processar apenas registros tipo 1 e 5 (transações)
                tipo = linha[0]
                if tipo == '1' or tipo == '5':
                    dados = parse_transacao(linha)
                    
                    # Formattar dados para CSV
                    registro = {
                        'Data': f"{dados['data_transacao'][6:8]}/{dados['data_transacao'][4:6]}/{dados['data_transacao'][0:4]}",
                        'Hora': f"{dados['hora_transacao'][0:2]}:{dados['hora_transacao'][2:4]}:{dados['hora_transacao'][4:6]}",
                        'CNPJ_Estabelecimento': dados['cnpj_estab'].strip(),
                        'ID_Transacao': dados['id_transacao'].strip(),
                        'Tipo_Transacao': interpretar_tipo_transacao(dados['tipo_transacao']),
                        'Bandeira': interpretar_bandeira(dados['bandeira']),
                        'Valor_Bruto': float(dados['valor_bruto'])/100 if dados['valor_bruto'].isdigit() else dados['valor_bruto'],
                        'Valor_Taxa_ADM': float(dados['valor_taxa_adm'])/100 if dados['valor_taxa_adm'].isdigit() else dados['valor_taxa_adm'],
                        'Valor_Liquido': float(dados['valor_liquido'])/100 if dados['valor_liquido'].isdigit() else dados['valor_liquido'],
                        'Qtd_Parcelas': int(dados['qtd_parcelas']) if dados['qtd_parcelas'].isdigit() else dados['qtd_parcelas'],
                        'Num_Parcela': int(dados['num_parcela']) if dados['num_parcela'].isdigit() else dados['num_parcela'],
                        'Data_Lancamento': f"{dados['data_lancamento'][6:8]}/{dados['data_lancamento'][4:6]}/{dados['data_lancamento'][0:4]}" if len(dados['data_lancamento']) == 8 else dados['data_lancamento'],
                        'Arquivo_Origem': nome_arquivo
                    }
                    registros.append(registro)
        
        if registros:
            # Salvar CSV
            csv_path = os.path.join(LOCAL_CSV_DIR, f"{nome_arquivo}.csv")
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Data', 'Hora', 'CNPJ_Estabelecimento', 'ID_Transacao', 
                    'Tipo_Transacao', 'Bandeira', 'Valor_Bruto', 'Valor_Taxa_ADM', 
                    'Valor_Liquido', 'Qtd_Parcelas', 'Num_Parcela', 'Data_Lancamento', 
                    'Arquivo_Origem'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(registros)
            
            print(f"✅ CSV gerado: {csv_path} ({len(registros)} registros)")
            return csv_path
        else:
            print(f"⚠️  Nenhum registro válido encontrado em {nome_arquivo}.txt")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao processar {caminho_txt}: {e}")
        return None

def gerar_relatorio_consolidado(csvs_gerados):
    """Gera um relatório consolidado com estatísticas"""
    try:
        total_arquivos = len(csvs_gerados)
        total_registros = 0
        
        for csv_path in csvs_gerados:
            if csv_path and os.path.exists(csv_path):
                with open(csv_path, 'r', encoding='utf-8') as f:
                    # Contar linhas (menos o header)
                    linhas = len(f.readlines()) - 1
                    total_registros += linhas
        
        # Gerar relatório
        relatorio_path = os.path.join(LOCAL_CSV_DIR, "relatorio_processamento.txt")
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE PROCESSAMENTO GRANITO - BLUEDATA\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"="*50 + "\n\n")
            f.write(f"Total de arquivos processados: {total_arquivos}\n")
            f.write(f"Total de registros extraídos: {total_registros}\n\n")
            f.write(f"Arquivos gerados:\n")
            
            for csv_path in csvs_gerados:
                if csv_path and os.path.exists(csv_path):
                    nome_arquivo = os.path.basename(csv_path)
                    f.write(f"- {nome_arquivo}\n")
        
        print(f"📊 Relatório gerado: {relatorio_path}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    print("="*60)
    print("PROCESSADOR DE DADOS GRANITO - BLUEDATA")
    print("="*60)
    
    # Conectar ao SFTP
    transport, sftp = conectar_sftp()
    if not sftp:
        return
    
    try:
        # Baixar arquivos TXT
        arquivos_txt = baixar_arquivos_txt(sftp)
        
        if not arquivos_txt:
            print("⚠️  Nenhum arquivo para processar.")
            return
        
        # Converter cada TXT para CSV
        csvs_gerados = []
        for txt_path in arquivos_txt:
            csv_path = converter_txt_para_csv(txt_path)
            if csv_path:
                csvs_gerados.append(csv_path)
        
        # Gerar relatório consolidado
        if csvs_gerados:
            gerar_relatorio_consolidado(csvs_gerados)
            print(f"\n✅ Processamento concluído!")
            print(f"📁 Arquivos CSV salvos em: {LOCAL_CSV_DIR}")
        else:
            print("⚠️  Nenhum arquivo CSV foi gerado.")
            
    finally:
        # Fechar conexões
        sftp.close()
        transport.close()
        print("🔐 Conexão SFTP encerrada.")

if __name__ == "__main__":
    main()
