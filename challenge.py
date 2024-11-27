import requests
from selenium.webdriver.support import expected_conditions as EC 
import time
import requests
import os
import pandas as pd
import random
from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.float_format', '{:,.0f}'.format)

# URL World Bank
BASE_URL = 'https://data.worldbank.org'

# Directory where the csv with the raw data will be saved
folder_path = 'Raw_Data_Country'
# Create route if it does not exist
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
# List the files within the directory
all_files = os.listdir(folder_path)
# Filter and select files ending in '.csv'
csv_files = [file for file in all_files if file.endswith('.csv')]


# Check if there is at least one CSV file in the list
if len(csv_files) == 0:
    print("No CSV files found in the specified directory.")
else:
    # Grab the first CSV file in the list (or any other file you prefer)
    file_path = os.path.join(folder_path, csv_files[0])
    
    # Read CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Replace the 'N/A' values ​​with 'pd.NA' for pandas handling and then fill the NaNs with '0'
    df = df.replace('N/A', pd.NA)
    df = df.fillna('0')

# Feature to extract links and country names
def get_country_links():
    '''Function to extract country links and names
        This function fetches the main country page from the World Bank website and extracts the names and URLs countries listed.
        It takes no parameters and returns a list of tuples, each containing a country name and its corresponding URL.'''
    
    url = f'{BASE_URL}/country'
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f'Error accessing {url}: {response.status_code}')
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    country_links = []

    # Iterate through each section with the class 'nav-item'
    for section in soup.select('section.nav-item'):
        # Find all 'a' tags within the section
        for link in section.find_all('a'):
            country_name = link.text.strip()
            country_url = BASE_URL + link['href']
            country_links.append((country_name, country_url))

    return country_links

# Feature to extract country specific data  
def extract_country_data(country_name, country_url):
    '''# Function to extract specific data of a country
        This function takes the name and URL of a country and extracts key economic and social data such as life expectancy, population, GDP, and access to electricity.
        Parameters:
        - country_name: The name of the country (str).
        - country_url: The URL that points to the country's specific data page (str).
        It returns a dictionary with the extracted data, or 'N/A' if the data is not found.'''
    
    print(f'Accessing data of: {country_name}')
    
    # Send a GET request to the country's data URL
    response = requests.get(country_url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f'Error accesing to: {country_url}: {response.status_code}')
        return {
            'Country': country_name,
            'Life Expectancy': 'N/A',
            'Year (Life Expectancy)': 'N/A',
            'Population': 'N/A',
            'Year (Population)': 'N/A',
            'GDP (Current US$)': 'N/A',
            'Year (GDP)': 'N/A',
            'GDP Per Capita (Current US$)': 'N/A',
            'Year (GDP Per Capita)': 'N/A',
            'Access to Electricity (% Of Population)': 'N/A',
            'Year (Access Electricity)': 'N/A'
        }
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize the dictionary with default 'N/A' values for each data point
    data = {
        'Country': country_name,
        'Life Expectancy': 'N/A',
        'Year (Life Expectancy)': 'N/A',
        'Population': 'N/A',
        'Year (Population)': 'N/A',
        'GDP (Current US$)': 'N/A',
        'Year (GDP)': 'N/A',
        'GDP Per Capita (Current US$)': 'N/A',
        'Year (GDP Per Capita)': 'N/A',
        'Access to Electricity (% Of Population)': 'N/A',
        'Year (Access Electricity)': 'N/A'
    }

    # List of indicators to extract: name, value, and year
    indicators = [
        ('Life expectancy at birth, total (years)', 'Life Expectancy', 'Year (Life Expectancy)'),
        ('Population, total', 'Population', 'Year (Population)'),
        ('GDP (current US$)', 'GDP (Current US$)', 'Year (GDP)'),
        ('GDP per capita (current US$)', 'GDP Per Capita (Current US$)', 'Year (GDP Per Capita)'),
        ('Access to electricity (% of population)', 'Access to Electricity (% Of Population)', 'Year (Access Electricity)')
    ]

    # Loop through the list of indicators and extract the relevant data
    for indicator_name, value_key, year_key in indicators:
        try:
            # Find the section containing the indicator data
            section = soup.find('a', text=indicator_name).find_parent('div', class_='indicator-item__inner')
            
            # Extract the value and year for each indicator
            data[value_key] = section.find('div', class_='indicator-item__data-info').text.strip()
            data[year_key] = section.find('p', class_='indicator-item__data-info-year').text.strip().replace('(', '').replace(')', '')
        except AttributeError:
            # If the indicator is not found, print a message and continue
            print(f'Indicator {indicator_name} was not found for {country_name}')
            continue

    return data

# Function to normalize the GDP and Population columns of the countries
def normalize_gdp_and_population(row):
    '''Function to normalize GDP and population values by cleaning and converting them to float values
        This function cleans and transforms the GDP and population values by removing commas and converting them to appropriate numeric values. It also accounts for the magnitude (e.g., billion, trillion, million) based on the provided year value.
        Parameters:
        - row: A row of data (typically a pandas DataFrame row) that contains the GDP, GDP year, population, and population year.
        The function returns the normalized GDP and population values as float.'''
    
    # Extract GDP and population values from the row
    gdp_value = row['GDP (Current US$)']
    year_value_gdp = row['Year (GDP)']
    population_value = row['Population']
    year_value_population = row['Year (Population)']
    
    # Clean and transform GDP
    try:
        # Remove commas and convert GDP to float
        gdp_value = float(str(gdp_value).replace(',', '').strip())
    except ValueError:
        # If conversion fails, set GDP to 0.0
        gdp_value = 0.0
        
    # Check if the GDP year value is valid and adjust the GDP value based on its magnitude
    if pd.notna(year_value_gdp):
        year_value_gdp = str(year_value_gdp)  # Ensure it's a string for comparison
        if 'billion' in year_value_gdp:
            gdp_value = gdp_value * 1e9
        elif 'trillion' in year_value_gdp:
            gdp_value = gdp_value * 1e12
        elif 'million' in year_value_gdp:
            gdp_value = gdp_value * 1e6
    
    # Clean and transform Population
    try:
        # Remove commas and convert population to float
        population_value = float(str(population_value).replace(',', '').strip())
    except ValueError:
        # If conversion fails, set population to 0.0
        population_value = 0.0
        
    # Check if the population year value is valid and adjust the population value based on its magnitude
    if pd.notna(year_value_population):
        year_value_population = str(year_value_population)  # Ensure it's a string for comparison
        if 'billion' in year_value_population:
            population_value = population_value * 1e9
        elif 'trillion' in year_value_population:
            population_value = population_value * 1e12
        elif 'million' in year_value_population:
            population_value = population_value * 1e6
    
    return gdp_value, population_value

# Function to process data and columns
def process_columns(df):
    
    '''Function to process and normalize the columns of the DataFrame
        This function ensures that the year columns ('Year (GDP)', 'Year (Population)') are strings,
        normalizes the GDP and population values, removes the original GDP and population columns,
    cleans the keywords ('billion', 'trillion', 'million') from the year columns,
    and converts the columns to the appropriate data types.
    Parameters:
    - df: DataFrame containing the data to be processed.
    The function returns a processed DataFrame with normalized columns and converted to the appropriate types.'''
    
    # Ensure that 'Year (GDP)' and 'Year (Population)' columns are of string type
    if 'Year (GDP)' in df.columns:
        df['Year (GDP)'] = df['Year (GDP)'].astype(str)
    if 'Year (Population)' in df.columns:
        df['Year (Population)'] = df['Year (Population)'].astype(str)
    
    # Apply the normalization function to each row of the DataFrame
    df[['GDP Normalized (Current $US)', 'Population Normalized']] = df.apply(
        lambda row: pd.Series(normalize_gdp_and_population(row)), axis=1
    )
    
    # Remove the original 'GDP (Current US$)' and 'Population' columns from the DataFrame
    if 'GDP (Current US$)' in df.columns:
        df.drop(columns=['GDP (Current US$)'], inplace=True)
    if 'Population' in df.columns:
        df.drop(columns=['Population'], inplace=True)

    # Remove the words 'billion', 'trillion', 'million' from the Year columns
    if 'Year (GDP)' in df.columns:
        df['Year (GDP)'] = df['Year (GDP)'].str.replace(r'\s*(billion|trillion|million)\s*', '', regex=True)
    if 'Year (Population)' in df.columns:
        df['Year (Population)'] = df['Year (Population)'].str.replace(r'\s*(billion|trillion|million)\s*', '', regex=True)

    # Define columns for conversion
    columns_int = ['Life Expectancy', 'Year (Life Expectancy)', 'Year (Population)', 'Year (GDP)', 'Year (GDP Per Capita)', 'Year (Access Electricity)', 'GDP Normalized (Current $US)', 'Population Normalized']
    columns_float1 = ['GDP Per Capita (Current US$)']
    columns_float2 = ['Access to Electricity (% Of Population)']

    # Convert the columns to the appropriate data types
    for column in df.columns:
        if column in columns_int and column in df.columns:
            # Convert the columns to integers, filling NaN with 0 before conversion
            df[column] = df[column].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
        if column in columns_float1 and column in df.columns:
            # Convert the GDP per capita columns to floats
            df[column] = pd.to_numeric(df[column].str.replace(',', ''), errors='coerce').fillna(0)
        if column in columns_float2 and column in df.columns:    
            # Convert the access to electricity columns to floats
            df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0)

    # Insert the normalized columns in specific positions
    df.insert(4, 'GDP Normalized (Current $US)', df.pop('GDP Normalized (Current $US)'))
    df.insert(3, 'Population Normalized', df.pop('Population Normalized'))
    
    return df


# The main function
def main():
    '''The main function orchestrates the data extraction, processing, and saving of country data.
        It is divided into two parts:
        1. **Data Extraction**: This part retrieves country links and extracts data for each country.
        2. **Data Processing and Saving**: This part processes the extracted data and saves the cleaned and processed DataFrame to a file.'''
    
    # Part 1: Data Extraction
    try:
        # Retrieve country links using the get_country_links function
        country_links = get_country_links()
        
        # If no country links are retrieved, display an error and return an empty DataFrame
        if not country_links:
            print('Could not get country links')
            return pd.DataFrame()

        country_data = []  # List to store the extracted data for each country

        # Loop through each country link and extract the country data
        for name, url in country_links:
            country_data.append(extract_country_data(name, url))
            # Random sleep between 1 to 3 seconds to avoid overwhelming the server
            time.sleep(random.uniform(1, 3))  

        # Convert the country data into a DataFrame
        df = pd.DataFrame(country_data)
        
        # Create a folder to store the raw data if it doesn't exist
        folder_name = 'Raw_Data_Country'
        
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # Save the raw data to a CSV file
        file_path = os.path.join(folder_name, 'raw_data_country.csv')
        df.to_csv(file_path, index=False)

        print(f'DataFrame saved in: {file_path}')
    
    except Exception as e:
        # Handle any error that occurs during data extraction
        print(f'Error extracting data: {e}')
        return
    
    # Part 2: Data Processing and Saving
    try:
        # Process the extracted data using the process_columns function
        dataframe = process_columns(df)
        
        # Create a folder for the processed data if it doesn't exist
        folder_name_process = 'Process_Data_Country'
        
        if not os.path.exists(folder_name_process):
            os.makedirs(folder_name_process)
        
        # Save the processed data to a CSV file
        file_path_process = os.path.join(folder_name_process, 'process_data_country.csv')
        try:
            dataframe.to_csv(file_path_process, index=False)    
            print(f'Processed data frame saved in: {file_path_process}')
    
        except Exception as e:
            # Handle any error that occurs during saving the processed data
            print(f'Error saving processed data file: {e}')
    
    except Exception as e:
        # Handle any error that occurs during data processing
        print(f'Error processing data: {e}')
        return


# Run the main function and get the data
main()

