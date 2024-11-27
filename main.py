from fastapi import FastAPI, Query
from typing import List, Optional
import pandas as pd
import os

app = FastAPI(
    title="Country Data API",
    description="This API returns country data in JSON format.",
    version="1.0.0"
)

folder_path = 'Process_Data_Country'
if not os.path.exists(folder_path):
    raise ValueError(f'The {folder_path} folder does not exist.')


# List the files inside the folder
csv_files = os.listdir(folder_path)
if not csv_files:
    raise ValueError(f'No csv files found in {folder_path}.')

# Read the CSV files
all_dataframes = []
for file in csv_files:
    if file.endswith('.csv'):
        # Create the full file path
        file_path = os.path.join(folder_path, file)
        # Read the CSV file
        df = pd.read_csv(file_path)
        all_dataframes.append(df)

# Concatenate multiple dataframes in case of corrsponder
dataframe = pd.concat(all_dataframes, ignore_index=True)

dataframe['Country'] = dataframe['Country'].str.lower()
     
        
@app.get("/data")
async def get_data(COUNTRIES: Optional[List[str]] = Query(None, description="List of countries to filter"),
                   ):
    filtered_df = dataframe
    
    if COUNTRIES:
        countries_lower = [country.lower() for country in COUNTRIES]
        filtered_df = filtered_df[filtered_df['Country'].isin(countries_lower)]
    
    
    data = filtered_df.to_dict(orient="records")
    return data