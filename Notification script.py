#pip install psycopg2-binary
#pip install pandas
#pip install smtplib


import psycopg2
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib

# Database connection parameters for the first and second databases
DB1_PARAMS = {
    'dbname': 'first_dbname',
    'user': 'first_user',
    'password': 'first_password',
    'host': 'first_host',
    'port': 'first_port'
}

DB2_PARAMS = {
    'dbname': 'second_dbname',
    'user': 'second_user',
    'password': 'second_password',
    'host': 'second_host',
    'port': 'second_port'
}

# SMTP server configuration
SMTP_SERVER = 'smtp.your-email-server.com'
SMTP_PORT = 587
SMTP_USER = 'your-email@example.com'
SMTP_PASSWORD = 'your-email-password'
EMAIL_SUBJECT = 'Repository Size Notification'
EMAIL_BODY = 'Please find attached the list of repositories exceeding 1000GB.'

def get_large_repos():
    conn = psycopg2.connect(**DB1_PARAMS)
    query = "SELECT repo_name, size_bytes FROM repos WHERE size_bytes > 1000 * 1024 * 1024 * 1024"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def store_notification(df):
    conn = psycopg2.connect(**DB2_PARAMS)
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute("INSERT INTO notification (repo_name, size_bytes, status) VALUES (%s, %s, %s)",
                       (row['repo_name'], row['size_bytes'], 'active'))
    conn.commit()
    cursor.close()
    conn.close()

def get_emails():
    conn = psycopg2.connect(**DB2_PARAMS)
    query = """
    SELECT DISTINCT e.email
    FROM email e
    JOIN notification n ON e.repo_name = n.repo_name
    WHERE n.status = 'active' AND e.email IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df['email'].tolist()

def send_email(recipients, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = EMAIL_SUBJECT
    msg.attach(MIMEText(EMAIL_BODY, 'plain'))

    attachment = MIMEBase('application', 'octet-stream')
    with open(attachment_path, 'rb') as f:
        attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename='notification.csv')
    msg.attach(attachment)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SMTP_USER, recipients, msg.as_string())
    server.close()

def update_notification_status():
    conn = psycopg2.connect(**DB2_PARAMS)
    cursor = conn.cursor()
    cursor.execute("UPDATE notification SET status = 'inactive' WHERE status = 'active'")
    conn.commit()
    cursor.close()
    conn.close()

def main():
    large_repos = get_large_repos()
    if not large_repos.empty:
        store_notification(large_repos)
        emails = get_emails()
        if emails:
            attachment_path = '/tmp/notification.csv'
            large_repos.to_csv(attachment_path, index=False)
            send_email(emails, attachment_path)
        update_notification_status()

if __name__ == '__main__':
    main()
