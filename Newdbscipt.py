#pip install psycopg2

import psycopg2

# Connection details
db_config = {
    'host': 'your_host',
    'database': 'your_database',
    'user': 'your_user',
    'password': 'your_password'
}

# Connect to the PostgreSQL database
conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

# Define the source and target table names
source_table = 'source_table'
target_table = 'target_table'

# Query data from the source table
query = f"SELECT column1, column2, column3, column4 FROM {source_table}"
cursor.execute(query)
rows = cursor.fetchall()

# Insert data into the target table with different column names
for row in rows:
    # Assuming target_table has columns new_column1, new_column2, new_column3, new_column4
    insert_query = f"""
    INSERT INTO {target_table} (new_column1, new_column2, new_column3, new_column4)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(insert_query, row)

# Commit the changes and close the connection
conn.commit()
cursor.close()
conn.close()
