import os
import pandas as pd

# Define the directory where the 'all_data' CSV files are located
database_dir = os.path.join(os.getcwd(), 'database')

# List all files that start with 'all_data' and end with '.csv'
all_data_files = [f for f in os.listdir(database_dir) if f.startswith('all_data') and f.endswith('.csv')]

# Initialize a list to store the DataFrames
dataframes = []

# Iterate over the files and read each one into a DataFrame
for file in all_data_files:
    file_path = os.path.join(database_dir, file)
    print(f"Reading file: {file_path}")
    df = pd.read_csv(file_path)
    dataframes.append(df)

# Concatenate all DataFrames into a single DataFrame
consolidated_data = pd.concat(dataframes, ignore_index=True)

# Save the consolidated DataFrame to a new CSV file
consolidated_file = os.path.join(database_dir, 'consolidated_all_data.csv')
consolidated_data.to_csv(consolidated_file, index=False)
print(f"Consolidated database saved to: {consolidated_file}")