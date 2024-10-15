import zipfile
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import configparser

config = configparser.ConfigParser()
config.read('emailing\config.ini')

def send_email_with_attachment(to_email, subject, body, file_path):
    # Your email credentials
    from_email = config['EMAIL']['sender_email']
    password = config['EMAIL']['sender_password']  # Use App Password if 2FA is enabled

    print("From email: ", from_email)
    print("Password: ", password)

    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    try:
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
            msg.attach(part)
    except Exception as e:
        print(f"Could not attach the file: {e}")
        return

    try:
        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use 465 for SSL
        server.starttls()  # Upgrade the connection to TLS
        server.login(from_email, password)  # Log in to your email account
        server.send_message(msg)  # Send the email
        server.quit()  # Close the connection

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_email_alert_video(config, n_people, n_people_start, timestamp, save_file):
    send_email_with_attachment(
        to_email=config['EMAIL']['recipient_email'],
        subject="Alert: High Number of People Detected in Video",
        body=f"""
        Hello,

        A video captured by the monitoring system has detected {n_people} people, 
        which exceeds the set threshold from {n_people_start} to {timestamp}. 
        Please review the attached video for further details.

        Best regards,
        Stevanus
        """,
        file_path=save_file
    )

def send_email_alert_photo(config, n_people, save_file):
    send_email_with_attachment(
        to_email=config['EMAIL']['recipient_email'],
        subject="Alert: High Number of People Detected in Image",
        body=f"""
        Hello,

        An Image captured by the monitoring system has detected {n_people} people, 
        which exceeds the set threshold of {n_people}. 
        Please review the attached image for further details.

        Best regards,
        Stevanus
        """,
        file_path=save_file
    )
    
def send_email_alert_webcam(config, n_people, save_file, start_time, end_time):
    send_email_with_attachment(
        to_email=config['EMAIL']['recipient_email'],
        subject="Alert: High Number of People Detected in Image",
        body=f"""
        Hello,

        An Image captured by the monitoring system has detected {n_people} people, 
        which exceeds the set threshold of {n_people}. 
        Please review your webcam at {start_time} - {end_time}        

        Best regards,
        Stevanus
        """,
        file_path=save_file
    )