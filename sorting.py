import os
import glob
import pandas as pd

def get_year_interval(year):
    """
    Retorna o intervalo de anos para consolidação.
    """
    if year >= 2020:
        return "2020_2024"
    else:
        start = year - ((year - 2000) % 3)
        end = start + 2
        return f"{start}_{end}"

# Pasta onde estão os arquivos separados
input_folder = 'data'  
# Pasta de saída para os arquivos consolidados
output_folder = "consolidated_files"
os.makedirs(output_folder, exist_ok=True)

# Padrão dos arquivos: assumindo nomes como "dados_{start_year}_{end_year}_id_{id_estacao}.csv"
pattern = os.path.join(input_folder, "data_*_id_*.csv")
files = glob.glob(pattern)

# Dicionário para agrupar DataFrames por intervalo
interval_dfs = {}

for file in files:
    try:
        df = pd.read_csv(file)
        
        # Remover a última coluna, se for irrelevante
        df = df.iloc[:, :-1]
        
        # Converte a coluna "ano" para numérico (caso não esteja)
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        
        # Remove linhas onde todas as colunas após a terceira (índice 2) estão vazias
        mask = df.iloc[:, 3:].notna().any(axis=1)
        df = df[mask]
        
        # Determina o intervalo de anos para cada linha
        df['intervalo'] = df['ano'].apply(get_year_interval)
        
        # Agrupa os DataFrames por intervalo
        for interval, group_df in df.groupby('intervalo'):
            if interval not in interval_dfs:
                interval_dfs[interval] = []
            interval_dfs[interval].append(group_df)
    except Exception as e:
        print(f"Erro ao processar {file}: {e}")

# Consolida e salva os DataFrames por intervalo
for interval, dfs in interval_dfs.items():
    consolidated_df = pd.concat(dfs, ignore_index=True)
    # Remove a coluna "intervalo" antes de salvar
    consolidated_df = consolidated_df.drop(columns=['intervalo'])
    output_filename = os.path.join(output_folder, f"consolidated_{interval}.csv")
    consolidated_df.to_csv(output_filename, index=False)
    print(f"Arquivo consolidado salvo: {output_filename}")
