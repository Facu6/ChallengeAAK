# Country Data Extraction and Processing

This project extracts data related to various countries from a specified website, processes it, and stores it in CSV files. The data includes indicators like life expectancy, GDP, population, and access to electricity. The extracted data is then normalized and saved into separate folders for raw and processed data.

Additionally, the project includes an API based on FastAPI that allows querying the processed data in JSON format.
(**http://127.0.0.1:8000/docs**)

## Project Overview

The primary goal of this project is to:
1. **Extract country-specific data** from an online source.
2. **Process the extracted data** by cleaning and normalizing certain values, such as GDP and population.
3. **Save the data** into two separate CSV files: one for raw data and another for processed data.
4. **Provide an API** that allows you to consult country data easily and quickly.

## Data Source

The data is extracted from the following URL:
- **Base URL**: `https://data.worldbank.org/country` (where `BASE_URL` is the base of the website you're scraping data from).

This URL provides a list of country links, each leading to a page containing detailed data about each country. 

### Data Extracted

The extracted data includes the following indicators:
- **Life Expectancy**: The life expectancy of the country's population.
- **Population**: The total population of the country.
- **GDP (Current US$)**: The country's Gross Domestic Product in current US dollars.
- **GDP Per Capita (Current US$)**: The GDP per capita in current US dollars.
- **Access to Electricity (% of Population)**: The percentage of the population with access to electricity.

Each country’s data is linked to its specific page, where the above indicators are retrieved.

## Functions

### `get_country_links()`

- **Purpose**: Extracts a list of countries and their respective URLs from the base country page.
- **Returns**: A list of tuples containing country names and URLs.
  
### `extract_country_data(country_name, country_url)`

- **Purpose**: Extracts specific data (Life Expectancy, Population, GDP, etc.) for a given country.
- **Parameters**:
  - `country_name` (str): The name of the country.
  - `country_url` (str): The URL to the country's data page.
- **Returns**: A dictionary containing the country’s data.
  
### `normalize_gdp_and_population(row)`

- **Purpose**: Normalizes the GDP and Population columns, converting them into appropriate numeric values based on the unit (billion, million, trillion).
- **Parameters**:
  - `row` (pandas.Series): A row of the DataFrame.
- **Returns**: Normalized GDP and Population values.

### `process_columns(df)`

- **Purpose**: Processes the extracted data, including cleaning, normalizing, and converting the data into proper formats (e.g., integers and floats).
- **Parameters**:
  - `df` (pandas.DataFrame): The DataFrame containing the raw country data.
- **Returns**: A processed DataFrame.

### `main()`

- **Purpose**: Orchestrates the entire data extraction, processing, and saving process.
- **Steps**:
  1. Extracts country links using `get_country_links()`.
  2. Extracts specific country data using `extract_country_data()`.
  3. Saves the raw data to a folder named `Raw_Data_Country`.
  4. Processes the data using `process_columns()`.
  5. Saves the processed data to a folder named `Process_Data_Country`.

## Folder Structure/Files

- **challenge.py**: Script corresponding to the ETL

- **main.py**: Script to use a session in FastAPI

- **requirements.txt**: Text file with the dependencies to install

- **Raw_Data_Country**: Folder where the raw data is stored.
  - **raw_data_country.csv**: The file containing the raw data of countries extracted from the website.
  
- **Process_Data_Country**: Folder where the processed data is stored.
  - **process_data_country.csv**: The file containing the processed and cleaned data, including normalized values.

## Data Processing

1. **Normalization**: The `GDP (Current US$)` and `Population` columns are normalized by converting values in millions, billions, or trillions into their respective values in the same base unit.
2. **Cleaning**: Any non-numeric characters are stripped from the relevant columns. For example, the `GDP Per Capita (Current US$)` column is cleaned by removing commas.
3. **Data Types**: 
   - **Columns like 'Life Expectancy', 'Population', etc.** are converted into integers after handling missing or non-numeric values.
   - **Columns like 'GDP (Current US$)' and 'GDP Per Capita (Current US$)' are converted to floating-point numbers.**
   - **Year columns ('Year (Life Expectancy)', 'Year (GDP)', etc.) are converted to string types.**


## API FastAPI

The project includes a FastAPI API that allows querying processed country data in JSON format. This API has an endpoint that receives a list of countries and returns the corresponding filtered data.

API Configuration
In the main.py file, a FastAPI API has been configured to expose the processed data

**Endpoint**
 - GET /data
    - Parameters:
        - COUNTRIES (optional): A list of countries to filter the results.
    - Answer: A JSON with filtered country data, if a list of countries is provided. If no filter is provided, returns all available data.

## Execution Instructions

0. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd <project_directory>
   pip install -r requirements.txt
   python challenge.py
   python main.py


## CONCLUSION

This project serves as a comprehensive tool for extracting, processing, and storing country data, including economic and demographic indicators, from a specified website. The extracted data can be further analyzed or used in other applications, with proper handling and normalization for consistency across various data sources.