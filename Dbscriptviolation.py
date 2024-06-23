import psycopg2

def main():
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

        # Step 1: Fetch names from watches table where active = 1
        cursor.execute("SELECT name FROM watches WHERE active = 1")
        watches = cursor.fetchall()

        for watch in watches:
            watch_name = watch[0]
            print(f"Processing watch: {watch_name}")

            # Step 2: Execute the query on user_issues table
            cursor.execute("""
                SELECT COUNT(*), target, watcher_name
                FROM public.user_issues
                WHERE watcher_name = %s
                GROUP BY target, watcher_name
            """, (watch_name,))
            user_issues_summary = cursor.fetchall()

            for issue_summary in user_issues_summary:
                count, target, watcher_name = issue_summary

                # Step 3: Insert data into user_violation_watch_count
                cursor.execute("""
                    INSERT INTO verizon.user_violation_watch_count (watch_name, count, target, watcher_name)
                    VALUES (%s, %s, %s, %s)
                """, (watch_name, count, target, watcher_name))

                # Step 4: Insert into appropriate details table based on target
                cursor.execute("""
                    SELECT DISTINCT sha256, issue_id as XRAYID, path as RepoFullPath, target as RepoName,
                                    watcher_id, watcher_name, severity
                    FROM public.user_issues
                    WHERE target = %s
                """, (target,))
                issue_details = cursor.fetchall()

                for detail in issue_details:
                    sha256, xrayid, repo_full_path, repo_name, watcher_id, watcher_name, severity = detail

                    if 'cache' not in repo_name:
                        if '-prod' in repo_name:
                            # Insert into user_violation_prod_Details
                            cursor.execute("""
                                INSERT INTO verizon.user_violation_prod_Details
                                (sha256, xrayid, repo_full_path, repo_name, watcher_id, watcher_name, severity)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (sha256, xrayid, repo_full_path, repo_name, watcher_id, watcher_name, severity))
                        else:
                            # Insert into user_violation_Details
                            cursor.execute("""
                                INSERT INTO verizon.user_violation_Details
                                (sha256, xrayid, repo_full_path, repo_name, watcher_id, watcher_name, severity)
                            """, (sha256, xrayid, repo_full_path, repo_name, watcher_id, watcher_name, severity))

        # Commit the transaction
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    main()
