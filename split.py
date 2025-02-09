import os
import pandas as pd

def get_year_interval(year):
    """
    Returns the appropriate year interval for a given year.
    """
    if year >= 2020:
        return "2020_2024"
    else:
        start = year - ((year - 2000) % 3)
        end = start + 2
        return f"{start}_{end}"

# Load the climatic data
input_file = "climatic.csv"
data_folder = "data"
os.makedirs(data_folder, exist_ok=True)

df = pd.read_csv(input_file)

# Ensure necessary columns exist
required_columns = {'ano', 'id_estacao'}
if not required_columns.issubset(df.columns):
    raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")

# Convert 'ano' to numeric
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')

# Drop rows with NaN years or station IDs
df = df.dropna(subset=['ano', 'id_estacao'])

# Create year interval column
df['intervalo'] = df['ano'].apply(get_year_interval)

# Split and save data by interval and station ID
for (interval, station_id), group_df in df.groupby(['intervalo', 'id_estacao']):
    output_dir = os.path.join(data_folder, f"data_{interval}")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"id{station_id}.csv")
    group_df.drop(columns=['intervalo'], inplace=True)
    group_df.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")

print("Data successfully split and saved!")
