#pip install psycopg2-binary
#Program/script: C:\path\to\python.exe
#Add arguments: C:\path\to\your_script.py
#CREATE TABLE your_destination_table (
#   column1 datatype,
#  column2 datatype,
#    -- Add other columns as per your source table
#  query_executed_date TIMESTAMP
#);

import psycopg2
from datetime import datetime

# Database connection parameters
db_params = {
    'host': 'your_host',
    'port': 'your_port',
    'database': 'your_database',
    'user': 'your_username',
    'password': 'your_password'
}

# Query to execute
query = """
SELECT * FROM your_source_table;
"""

# Table to insert results
destination_table = "your_destination_table"

# Connect to the PostgreSQL database
try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    # Execute the query
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Get column names
    colnames = [desc[0] for desc in cursor.description]
    
    # Insert data into destination table
    for row in rows:
        insert_query = f"INSERT INTO {destination_table} ({', '.join(colnames)}, query_executed_date) VALUES ({', '.join(['%s'] * len(row))}, %s)"
        cursor.execute(insert_query, row + (datetime.now(),))
    
    # Commit the transaction
    conn.commit()

except Exception as error:
    print(f"Error: {error}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
#############################₹#₹₹₹₹#####################



import psycopg2
from datetime import datetime
import schedule
import time

# Database connection parameters
db_params = {
    'host': 'your_host',
    'port': 'your_port',
    'database': 'your_database',
    'user': 'your_username',
    'password': 'your_password'
}

# Query to fetch data from the source table
query = """
SELECT column1, column2, column3 FROM source_table;
"""

# Destination table name and column names
destination_table = "destination_table"
destination_columns = ['new_column1', 'new_column2', 'new_column3', 'insert_time']

def job():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        rows = cursor.fetchall()

        # Insert data into the destination table
        insert_query = f"""
        INSERT INTO {destination_table} ({', '.join(destination_columns)}) 
        VALUES (%s, %s, %s, %s);
        """

        for row in rows:
            cursor.execute(insert_query, row + (datetime.now(),))

        # Commit the transaction
        conn.commit()
        print("Data inserted successfully")

    except Exception as error:
        print(f"Error: {error}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Schedule the job daily at 9 AM IST
# 9 AM IST is 3:30 AM UTC
schedule.every().day.at("03:30").do(job)

print("Scheduled job to run daily at 9 AM IST")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
