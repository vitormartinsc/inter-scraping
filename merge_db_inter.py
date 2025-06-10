import os
import pandas as pd

def ler_e_mesclar_db_inter(pasta_csv, arquivo_saida):
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
    df_final.to_csv(arquivo_saida, index=False, encoding='utf-8')
    print(f'Mesclagem concluída! Arquivo salvo em: {arquivo_saida}')

if __name__ == '__main__':
    pasta_csv = './database/inter_stpf_data'
    arquivo_saida = 'db_inter_merged.csv'
    ler_e_mesclar_db_inter(pasta_csv, arquivo_saida)
