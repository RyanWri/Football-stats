import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def send_contact_form_to_my_email(sender_email, subject, message):
    # Create a multipart message
    msg = MIMEMultipart()
    to = os.environ.get("SMTP_USERNAME")
    msg["From"] = sender_email
    msg["To"] = to
    msg["Subject"] = subject

    # Add the message body
    msg.attach(MIMEText(message, "plain"))

    # Connect to the SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        # Start TLS for security
        server.starttls()

        # Enable debug mode
        server.set_debuglevel(True)

        # Login to your Gmail account
        server.login(to, os.environ.get("SMTP_APP_PASSWORD"))

        # Send the email
        server.send_message(msg)

    print("Email sent successfully!")
