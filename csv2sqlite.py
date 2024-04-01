import sqlite3
import pandas as pd

# Specify the CSV file path
csv_path = r"C:\Users\aviel_local\CompAI\Projects - Documents\אקסלנס\Exported results 2024-02-01_14-14-44.csv"

# Specify the SQLite database file path
db_path = r"C:\Users\aviel_local\CompAI\Projects - Documents\אקסלנס\database.db"

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(csv_path)

# Create a connection to the SQLite database
conn = sqlite3.connect(db_path)

# Write the data from the DataFrame to the SQLite database
df.to_sql('table_name', conn, if_exists='replace', index=False)

# Close the connection to the SQLite database
conn.close()