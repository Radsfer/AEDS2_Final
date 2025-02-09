import os
import pandas as pd
import basedosdados as bd
import gc  # Garbage Collector

billing_id = "mapeamentodebiomas"
output_file = "climatic.csv"
chunk_size = 100_000  # Número de linhas por vez

# Descobre a última linha processada
if os.path.exists(output_file):
    with open(output_file, "r") as f:
        last_line = sum(1 for _ in f)  # Conta as linhas
    offset = last_line  # Continua da última linha
    first_chunk = False  # Não adiciona cabeçalho
else:
    offset = 0  # Começa do zero se o arquivo não existir
    first_chunk = True  # Adiciona cabeçalho na primeira execução

while True:
    query = f"""
    SELECT
        dados.ano as ano,
        dados.data as data,
        dados.id_estacao as id_estacao,
        dados.precipitacao_total as precipitacao_total,
        dados.temperatura_bulbo_hora as temperatura_bulbo_hora,
        dados.temperatura_orvalho_hora as temperatura_orvalho_hora,
        dados.temperatura_max as temperatura_max,
        dados.temperatura_min as temperatura_min,
        dados.temperatura_orvalho_max as temperatura_orvalho_max,
        dados.temperatura_orvalho_min as temperatura_orvalho_min,
        dados.umidade_rel_max as umidade_rel_max,
        dados.umidade_rel_min as umidade_rel_min
    FROM `basedosdados.br_inmet_bdmep.microdados` AS dados
    LIMIT {chunk_size} OFFSET {offset}
    """

    print(f"Baixando linhas {offset} até {offset + chunk_size}...")

    df = bd.read_sql(query=query, billing_project_id=billing_id)

    if df.empty:
        print("Finalizado! Todos os dados foram processados.")
        break  # Se não há mais dados, encerra o loop

    df.to_csv(output_file, index=False, mode='a', header=first_chunk)
    first_chunk = False  # Apenas o primeiro bloco precisa do cabeçalho

    del df  # Remove da memória RAM
    gc.collect()  # Força liberação de memória

    offset += chunk_size  # Move para o próximo bloco
