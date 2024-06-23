import psycopg2
from psycopg2 import sql
import schedule
import time

def job():
    # Database connection parameters
    conn_params = {
        'dbname': 'your_dbname',
        'user': 'your_user',
        'password': 'your_password',
        'host': 'your_host',
        'port': 'your_port'
    }

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Fetch rows from watches table where active = 1
        cursor.execute("SELECT * FROM watches WHERE active = 1")
        watches = cursor.fetchall()
        
        # Print all active rows from watches table
        for watch in watches:
            print(watch)

            # Run the select query on user-issues table for each watch
            cursor.execute("SELECT * FROM user_issues WHERE watch_id = %s", (watch[0],))
            user_issues = cursor.fetchall()

            # Process each user issue
            for issue in user_issues:
                target = issue['target']
                if 'cache' in target:
                    # Insert into violation1 table
                    cursor.execute(
                        sql.SQL("INSERT INTO violation1 (columns) VALUES (%s)"), 
                        (issue['columns'],)  # Replace with appropriate columns
                    )
                elif '-prod' in target:
                    # Insert into violation2 table
                    cursor.execute(
                        sql.SQL("INSERT INTO violation2 (columns) VALUES (%s)"), 
                        (issue['columns'],)  # Replace with appropriate columns
                    )
                else:
                    # Insert into violation2 table
                    cursor.execute(
                        sql.SQL("INSERT INTO violation2 (columns) VALUES (%s)"), 
                        (issue['columns'],)  # Replace with appropriate columns
                    )
        
        # Commit the transaction
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Schedule the job to run every day at 9 AM
schedule.every().day.at("09:00").do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
