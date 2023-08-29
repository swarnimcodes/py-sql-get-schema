import json
import pyodbc

# Server Details
server = '172.16.0.28'
database = 'DB_PRMITR_ERP_20230615'
username = 'Swarnim_Intern'
password = 'Swarnim14#'

# Establish connection
conn = pyodbc.connect(f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}")

# Create a cursor
cursor = conn.cursor()

# Query to retrieve relevant information
table_query = """
SELECT
    t.TABLE_SCHEMA,
    t.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.CHARACTER_MAXIMUM_LENGTH,
    c.NUMERIC_PRECISION,
    c.NUMERIC_SCALE
FROM INFORMATION_SCHEMA.TABLES AS t
JOIN INFORMATION_SCHEMA.COLUMNS AS c ON t.TABLE_SCHEMA = c.TABLE_SCHEMA AND t.TABLE_NAME = c.TABLE_NAME
WHERE t.TABLE_TYPE = 'BASE TABLE'
ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
"""

# Execute the query
cursor.execute(table_query)

# Fetch all the results
schema_results = cursor.fetchall()

# Close the cursor and the connection
cursor.close()
conn.close()

# Process the results
schema_info = {}
for row in schema_results:
    schema, table_name, column_name, data_type, max_length, numeric_precision, numeric_scale = row
    if schema not in schema_info:
        schema_info[schema] = {}
    if table_name not in schema_info[schema]:
        schema_info[schema][table_name] = []
    schema_info[schema][table_name].append({
        'column_name': column_name,
        'data_type': data_type,
        'max_length': max_length,
        'numeric_precision': numeric_precision,
        'numeric_scale': numeric_scale
    })

# Save schema information to a JSON file
json_filename = 'schema_information.json'
with open(json_filename, 'w') as json_file:
    json.dump(schema_info, json_file, indent=4)

print(f"Schema information saved to {json_filename}")