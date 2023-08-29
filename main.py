import json
import pyodbc
import filecmp

# Server Details
server = '172.16.0.28'
databases = [ 'DB_PRMITR_ERP_20230701', 'DB_PRMITR_ERP_20230615']
username = 'Swarnim_Intern'
password = 'Swarnim14#'

for database in databases:
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
    json_filename = f'schema_information_{database}.json'
    with open(json_filename, 'w') as json_file:
        json.dump(schema_info, json_file, indent=4)

    print(f"Schema information for {database} saved to {json_filename}")

# Compare the two schema JSON files
json_filename_1 = f'schema_information_{databases[0]}.json'
json_filename_2 = f'schema_information_{databases[1]}.json'

are_files_equal = filecmp.cmp(json_filename_1, json_filename_2)
if are_files_equal:
    print("Schemas are identical.")
else:
    print("Schemas are not identical.")


# ###############
# import difflib
# json_source_contents = open(json_filename_1, "r").read()
# json_test_contents = open(json_filename_2, "r").read()

# html_diff = difflib.HtmlDiff(tabsize=4, wrapcolumn=72).make_file(
#     json_source_contents.splitlines(),
#     json_test_contents.splitlines(),
#     context=True,
#     numlines=1,
#     charset='utf-8'
# )

# diff_filename = "schema diff.html"
# with open(diff_filename, "w", encoding="utf-8") as diff_file:
#     diff_file.write(html_diff)

#################


# # Load schema information from JSON files
# with open(json_filename_1, 'r') as json_file:
#     schema_info_1 = json.load(json_file)

# with open(json_filename_2, 'r') as json_file:
#     schema_info_2 = json.load(json_file)

# # Compare schemas and generate HTML report
# html_report = "<html><head><title>Database Schema Comparison</title></head><body>"

# for schema in schema_info_1:
#     schema_diff_found = False

#     for table_name in schema_info_1[schema]:
#         if table_name in schema_info_2.get(schema, {}):
#             columns_1 = schema_info_1[schema][table_name]
#             columns_2 = schema_info_2[schema][table_name]

#             if columns_1 != columns_2:
#                 if not schema_diff_found:
#                     html_report += f"<h2>Schema: {schema}</h2>"
#                     schema_diff_found = True

#                 html_report += f"<h3>Table: {table_name}</h3>"
#                 html_report += "<p style='color: red;'>Columns do not match.</p>"

#                 for col_info_1, col_info_2 in zip(columns_1, columns_2):
#                     if col_info_1 != col_info_2:
#                         html_report += "<p style='color: red;'>Column specifications do not match.</p>"
#                         html_report += f"<p><b>{col_info_1['column_name']}:</b></p>"
#                         html_report += f"<p><b>{schema}.<i>{table_name}</i></b></p>"
#                         html_report += f"<p><b>Specification in First Database:</b> {col_info_1}</p>"
#                         html_report += f"<p><b>Specification in Second Database:</b> {col_info_2}</p>"

#     html_report += "<hr>"

# html_report += "</body></html>"

# # Save HTML report to a file
# html_filename = 'schema_comparison_report.html'
# with open(html_filename, 'w') as html_file:
#     html_file.write(html_report)

# print(f"Schema comparison report saved to {html_filename}")

#########################

import json
import openpyxl

# Load schema information from JSON files
with open(json_filename_1, 'r') as json_file:
    schema_info_1 = json.load(json_file)

with open(json_filename_2, 'r') as json_file:
    schema_info_2 = json.load(json_file)

# Create an Excel workbook and sheet
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Schema Comparison"

# Set headers
sheet["A1"] = "Schema"
sheet["B1"] = "Table Name"
sheet["C1"] = "Type of Error"
sheet["D1"] = "Name of Column"
sheet["E1"] = f"Source DB: {databases[0]} Specification"
sheet["F1"] = f"Test DB: {databases[1]} Specification"

row = 2  # Start from the second row

for schema in schema_info_1:
    for table_name in schema_info_1[schema]:
        columns_1 = schema_info_1[schema][table_name]
        columns_2 = schema_info_2[schema].get(table_name, [])

        for col_info_1 in columns_1:
            col_name_1 = col_info_1["column_name"]
            col_info_2 = next((col for col in columns_2 if col["column_name"] == col_name_1), None)

            if col_info_2 is None:
                sheet[f"A{row}"] = schema
                sheet[f"B{row}"] = table_name
                sheet[f"C{row}"] = "Missing Column"
                sheet[f"D{row}"] = col_name_1
                sheet[f"E{row}"] = str(col_info_1)
                sheet[f"F{row}"] = ""
                sheet[f"C{row}"].fill = openpyxl.styles.PatternFill(start_color="ffd6ca", end_color="ffd6ca", fill_type="solid")
                row += 1
            elif col_info_1 != col_info_2:
                sheet[f"A{row}"] = schema
                sheet[f"B{row}"] = table_name
                sheet[f"C{row}"] = "Different Specification"
                sheet[f"D{row}"] = col_name_1
                sheet[f"E{row}"] = str(col_info_1)
                sheet[f"F{row}"] = str(col_info_2)
                sheet[f"C{row}"].fill = openpyxl.styles.PatternFill(start_color="e7d4f2", end_color="e7d4f2", fill_type="solid")
                row += 1

        for col_info_2 in columns_2:
            col_name_2 = col_info_2["column_name"]
            col_info_1 = next((col for col in columns_1 if col["column_name"] == col_name_2), None)

            if col_info_1 is None:
                sheet[f"A{row}"] = schema
                sheet[f"B{row}"] = table_name
                sheet[f"C{row}"] = "Missing Column"
                sheet[f"D{row}"] = col_name_2
                sheet[f"E{row}"] = ""
                sheet[f"F{row}"] = str(col_info_2)
                sheet[f"C{row}"].fill = openpyxl.styles.PatternFill(start_color="ffd6ca", end_color="ffd6ca", fill_type="solid")
                row += 1

# Save the Excel file
excel_filename = "schema_comparison_report.xlsx"
workbook.save(excel_filename)

print(f"Schema comparison report saved to {excel_filename}")
