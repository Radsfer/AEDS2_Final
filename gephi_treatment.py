import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'

import pandas as pd
import numpy as np
import csv
import geopandas as gpd
from shapely.geometry import Point

# Pesos para a distância ponderada (baseado na proposta de Whittaker)
w_precip = 0.6  # Peso para a precipitação
w_temp   = 0.4  # Peso para a temperatura

# Carregar o catálogo de estações
stations_catalog = pd.read_csv('station_catalog.csv', delimiter=';', encoding='ISO-8859-1')

# Criar um dicionário de mapeamento de ID para (Cidade, Estado, Latitude, Longitude)
station_mapping = dict(zip(
    stations_catalog['CD_ESTACAO'],
    zip(stations_catalog['DC_NOME'], 
        stations_catalog['SG_ESTADO'], 
        stations_catalog['VL_LATITUDE'], 
        stations_catalog['VL_LONGITUDE'])
))

# Carregar o shapefile dos biomas
biomes = gpd.read_file('Biomas_5000mil/Biomas5000.shp')

# Definir a variável com o nome da coluna que contém o nome do bioma (conforme seu shapefile)
biome_column = 'NOM_BIOMA'

# Selecionar as colunas relevantes para análise dos dados climáticos
# Para a proposta de Whittaker, usamos "precipitacao_total" e as temperaturas máxima e mínima.
climate_columns = [
    'precipitacao_total', 'temperatura_max', 'temperatura_min'
]

# Caminho para a pasta contendo os arquivos CSV consolidados
input_dir = 'consolidated_files'

# Listar todos os arquivos CSV na pasta
csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

# Processar cada arquivo CSV
for csv_file in csv_files:
    # Carregar os dados das estações
    data = pd.read_csv(os.path.join(input_dir, csv_file))
    
    # Verificar se a coluna 'id_estacao' existe
    if 'id_estacao' not in data.columns:
        print(f"O arquivo {csv_file} não contém a coluna 'id_estacao'. Pulando...")
        continue
    # Filtrar apenas os IDs que estão no catálogo de estações
    data = data[data['id_estacao'].isin(station_mapping.keys())]

    # Se após a filtragem não houver mais dados, pule o arquivo
    if data.empty:
        print(f"Após a filtragem, o arquivo {csv_file} não contém IDs válidos. Pulando...")
        continue

    # Usar 'id_estacao' como índice
    data = data.set_index('id_estacao')
    
    # Selecionar as colunas relevantes para análise
    df = data[climate_columns]
    
    # Agregar os dados para que cada estação apareça apenas uma vez (usando a média)
    df = df.groupby(df.index).mean().fillna(df.mean())
    
    # Calcular a temperatura média (T_med) e definir a precipitação total (P_total)
    df['T_med'] = (df['temperatura_max'] + df['temperatura_min']) / 2
    df['P_total'] = df['precipitacao_total']
    
    # Normalizar as duas variáveis de interesse (usando z-score)
    df['T_med_norm'] = (df['T_med'] - df['T_med'].mean()) / df['T_med'].std()
    df['P_total_norm'] = (df['P_total'] - df['P_total'].mean()) / df['P_total'].std()
    
    # Obter os arrays das variáveis normalizadas
    T = df['T_med_norm'].to_numpy().reshape(-1, 1)
    P = df['P_total_norm'].to_numpy().reshape(-1, 1)
    
    # Obter os IDs das estações e o número de estações

    station_ids = list(df.index)
    n_stations = len(station_ids)
    
    # Extrair o intervalo de anos do nome do arquivo (supondo o formato: consolidated_YYYY_YYYY.csv)
    parts = csv_file.split('_')
    year_range = parts[1] + '-' + parts[2].split('.')[0]
    
    # Criar o diretório para o intervalo de anos, se não existir
    output_dir = os.path.join(year_range)
    os.makedirs(output_dir, exist_ok=True)
    
    # Criar o DataFrame dos nós
    nodes = pd.DataFrame({'Id': station_ids})
    nodes[['Localização', 'Estado', 'Latitude', 'Longitude']] = nodes['Id'].map(station_mapping).apply(pd.Series)
    nodes['Label'] = nodes['Localização'] + ' - ' + nodes['Estado']
    
    # Converter Latitude e Longitude para float (caso estejam com vírgula)
    nodes['Latitude'] = nodes['Latitude'].astype(str).str.replace(',', '.').astype(float)
    nodes['Longitude'] = nodes['Longitude'].astype(str).str.replace(',', '.').astype(float)
    
    # Criar a geometria dos nós e transformar em GeoDataFrame
    nodes['geometry'] = nodes.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    nodes_gdf = gpd.GeoDataFrame(nodes, geometry='geometry', crs=biomes.crs)
    
    # Realizar junção espacial para obter o bioma de cada estação usando a coluna "NOM_BIOMA"
    nodes_gdf = gpd.sjoin(nodes_gdf, biomes[['geometry', biome_column]], how='left', predicate='within')
    nodes_gdf = nodes_gdf.rename(columns={biome_column: 'Bioma'})
    
    # Remover a coluna de geometria se não for necessária
    nodes_gdf = nodes_gdf.drop(columns='geometry')
    
    # Salvar o arquivo de nós com a coluna de bioma
    nodes_gdf.to_csv(os.path.join(output_dir, 'nodes.csv'), index=False)
    
    # Criar o arquivo de arestas calculando a distância ponderada
    edges_file = os.path.join(output_dir, 'edges.csv')
    with open(edges_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Source', 'Target', 'Weight'])
        for i in range(n_stations):
            for j in range(i+1, n_stations):
                # Calcular a diferença entre as variáveis normalizadas para cada estação
                delta_P = P[i] - P[j]
                delta_T = T[i] - T[j]
                # Calcular a distância ponderada: sqrt( w_precip*(delta_P)^2 + w_temp*(delta_T)^2 )
                dist = np.sqrt( w_precip * (delta_P**2) + w_temp * (delta_T**2) )
                # Converter a distância em peso: quanto menor a distância, maior o peso
                weight = 1 / (1 + dist)
                weight = float(weight)
                writer.writerow([station_ids[i], station_ids[j], weight])
    
    print(f"Processado o arquivo {csv_file} e gerado os arquivos de nós e arestas na pasta {output_dir}")
