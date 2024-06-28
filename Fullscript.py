#pip install psycopg2 pandas smtplib email

import psycopg2
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Database connection details
DB_CONFIG = {
    'dbname': 'your_db_name',
    'user': 'your_db_user',
    'password': 'your_db_password',
    'host': 'your_db_host',
    'port': 'your_db_port'
}

# Email details
SMTP_CONFIG = {
    'server': 'your_smtp_server',
    'port': 587,  # or your SMTP port
    'sender_email': 'your_email@example.com',
    'sender_password': 'your_email_password'
}

# Connect to the database
def connect_db():
    return psycopg2.connect(**DB_CONFIG)

# Get repos exceeding size and store in Notification table
def get_repos_exceeding_size(conn, size_threshold, table_name, active=True):
    query = f"""
    INSERT INTO {table_name} (repo_name, size, status, date)
    SELECT repo_name, size, {'Active' if active else 'Inactive'}, CURRENT_DATE
    FROM repos
    WHERE size > %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (size_threshold,))
    conn.commit()

# Mark records as inactive
def mark_records_inactive(conn, table_name):
    query = f"""
    UPDATE {table_name}
    SET status = 'Inactive'
    WHERE status = 'Active';
    """
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()

# Get records from Notification table to Escalation table
def escalate_repos(conn, notification_table, escalation_table):
    query = f"""
    INSERT INTO {escalation_table} (repo_name, size, status, date)
    SELECT repo_name, size, 'Active', CURRENT_DATE
    FROM {notification_table}
    WHERE status = 'Active'
    AND repo_name IN (
        SELECT repo_name FROM {notification_table}
        GROUP BY repo_name
        HAVING COUNT(repo_name) > 1
    );
    """
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()

# Send email with CSV attachment
def send_email(subject, body, recipients, attachment_path=None):
    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['sender_email']
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {attachment_path}")
            msg.attach(part)

    with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port']) as server:
        server.starttls()
        server.login(SMTP_CONFIG['sender_email'], SMTP_CONFIG['sender_password'])
        server.sendmail(SMTP_CONFIG['sender_email'], recipients, msg.as_string())

def main():
    conn = connect_db()
    
    # Get current day of the week
    day_of_week = datetime.today().strftime('%A')
    
    if day_of_week == 'Tuesday':
        # Step 1 & 2
        get_repos_exceeding_size(conn, 1000, 'notification')
        send_email('Warning 1: Storage Utilization Alert', 'Body of the email', ['user1@example.com'])
        mark_records_inactive(conn, 'notification')
    elif day_of_week == 'Thursday':
        # Step 3 & 4
        get_repos_exceeding_size(conn, 1000, 'notification', active=True)
        escalate_repos(conn, 'notification', 'escalation')
        send_email('Warning 2: Storage Utilization Alert', 'Body of the email', ['user1@example.com'])
    elif day_of_week == 'Monday':
        # Step 6 & 7
        mark_records_inactive(conn, 'escalation')
        get_repos_exceeding_size(conn, 1000, 'escalation', active=True)
        send_email('Escalation 1: Storage Utilization Alert', 'Body of the email', ['leadership@example.com'])
    elif day_of_week == 'Saturday':
        # Step 10
        # Implement black out logic and send notification
        send_email('Black Out Notification', 'Body of the email', ['leadership@example.com'])

    conn.close()

if __name__ == "__main__":
    main()
