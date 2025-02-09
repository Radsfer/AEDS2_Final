# Code Explanation

## Overview
This repository contains three main Python scripts that work together to collect, process, and analyze climatic data. The primary goal is to retrieve raw climatic data, consolidate it into structured datasets, and generate network files for analysis in Gephi.

### Scripts:
1. **scrapping.py** - Extracts climatic data from the `basedosdados` database.
2. **split.py** - Splits `climatic.csv` into smaller files categorized by year intervals and station ID.
3. **sorting.py** - Organizes and consolidates raw data files.
4. **gephi_treatment.py** - Processes climatic data and generates node and edge files for network analysis.

---

## **1. Data Extraction: `scrapping.py`**

### **Functionality:**
This script extracts data from `basedosdados.br_inmet_bdmep.microdados` (a database with climatic information from INMET) and saves it as a CSV file.

### **Key Features:**
- Uses Google BigQuery via `basedosdados`.
- Extracts temperature, humidity, and precipitation data.
- Fetches data in chunks (`100,000` rows at a time) to handle large datasets efficiently.
- Ensures continuity by checking the last processed row.
- Saves data incrementally to `clamatic.csv`.

### **Steps:**
1. Checks if `clamatic.csv` exists to determine the last processed row.
2. Queries the database in chunks using an `OFFSET`.
3. Appends data to the file.
4. Uses `gc.collect()` to optimize memory usage.
5. Stops execution when all data has been fetched.

---

## **4. Data Splitting: `split.py`**

### **Functionality:**
This script takes the `climatic.csv` file and splits it into smaller files based on year intervals and station ID.

### **Key Features:**
- Reads `climatic.csv` and categorizes data by year interval and station ID.
- Saves each subset into `data/data_{yearinterval}/id{stationID}.csv`.
- Ensures files are well-structured and easy to process later.

### **Steps:**
1. Reads `climatic.csv` and ensures required columns (`ano`, `id_estacao`) exist.
2. Converts `ano` to numeric and removes invalid rows.
3. Groups data by `intervalo` (computed using `get_year_interval()`) and `id_estacao`.
4. Saves each subset in `data/data_{yearinterval}/id{stationID}.csv`.

---

## **3. Data Organization: `sorting.py`**

### **Functionality:**
This script organizes the raw data files extracted in `scrapping.py`, consolidating them into structured CSV files based on year intervals.

### **Key Features:**
- Reads climate data files from the `data` directory.
- Groups data into predefined year intervals:
  - 2020 and later: grouped as `2020_2024`.
  - Before 2020: grouped in 3-year intervals (e.g., `2017_2019`, `2014_2016`).
- Removes unnecessary columns and empty rows.
- Saves consolidated datasets in `consolidated_files/`.

### **Steps:**
1. Searches for files following the pattern `data_{start_year}_{end_year}_id_{id_estacao}.csv`.
2. Cleans the data by removing irrelevant columns and empty rows.
3. Determines the year interval for each row using `get_year_interval()`.
4. Groups data accordingly and saves the consolidated file.

---

## **4. Data Processing for Gephi: `gephi_treatment.py`**

### **Functionality:**
This script processes the climatic data and prepares it for network analysis in Gephi.

### **Key Features:**
- Loads metadata from `station_catalog.csv` to map station IDs to geographic locations.
- Reads climatic data from `consolidated_files/`.
- Normalizes precipitation and temperature data using z-score.
- Associates stations with biomes using a shapefile (`Biomas5000.shp`).
- Generates node (`nodes.csv`) and edge (`edges.csv`) files for network analysis.

### **Steps:**
1. **Load Metadata & Shapefiles**
   - Reads station metadata (`station_catalog.csv`).
   - Loads biome shapefile (`Biomas5000.shp`) to associate stations with their respective biomes.
2. **Filter & Process Data**
   - Reads climate data from `consolidated_files/`.
   - Filters stations that exist in the catalog.
   - Computes average temperatures and total precipitation per station.
   - Normalizes variables (`T_med` and `P_total`).
3. **Generate Nodes File (`nodes.csv`)**
   - Assigns labels based on station location and state.
   - Uses `geopandas` to associate each station with a biome.
   - Saves nodes in CSV format.
4. **Generate Edges File (`edges.csv`)**
   - Calculates a weighted distance metric based on temperature and precipitation differences.
   - Defines edge weights using Whittaker's proposal:
     - Higher similarity → higher weight.
   - Saves edges in CSV format.

---

## **Output Files**
- **`clamatic.csv`** → Raw extracted climatic data.
- **`consolidated_files/consolidated_{year_interval}.csv`** → Cleaned & structured data.
- **`{year_range}/nodes.csv`** → Node file for Gephi.
- **`{year_range}/edges.csv`** → Edge file for Gephi.

---

## **Usage Instructions**

1. **Run the scrapping script**:

    Before running the script, set up Google Cloud and enable BigQuery:

    - Create a Google Cloud account and start a new project.
    - Enable the BigQuery API in the Google Cloud Console.
    - Generate a service account key and download the JSON credentials file.
    - Update the billing_id in the script to match your project ID.
    - Place the JSON key file in your project directory.

    When running the script, your browser may open, prompting you to authenticate and grant permissions. Accept the connection to proceed.
    ```sh
    python scrapping.py
    ```
    - This will generate `climatic.csv`.
  
2. **Split climatic data by year interval and station ID**:
   ```sh
   python split.py
   ```
   - This will generate smaller datasets inside `data/`.

3. **Organize extracted data**:
   ```sh
   python sorting.py
   ```
   - This will create structured files inside `consolidated_files/`.

4. **Process data for Gephi**:
   ```sh
   python gephi_treatment.py
   ```
   - This will generate `nodes.csv` and `edges.csv` for visualization in Gephi.

---

## **Conclusion**
This pipeline automates the extraction, cleaning, and processing of climatic data, making it ready for network analysis. The final output can be used for geographical climate studies and network modeling in Gephi.

