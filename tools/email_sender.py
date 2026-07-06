import smtplib
from email.mime.text import MIMEText
from pydantic import BaseModel, Field
import os


# Define the schema helper at the top of handle_message:
class EmailArgs(BaseModel):
    to_email: str = Field(description="The recipient email address.")
    subject: str = Field(description="The subject line of the email.")
    body: str = Field(description="The main text body content of the email.")


def send_background_email(to_email: str, subject: str, body: str) -> str:
    """Sends an email directly in the background using SMTP."""
    # Pull credentials from environment variables for security
    sender_email = os.environ.get("JARVIS_EMAIL_USER")
    sender_password = os.environ.get("JARVIS_EMAIL_PASSWORD")  # App Password if using Gmail

    if not sender_email or not sender_password:
        return "Email credentials are missing from system configuration, sir."

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email

        # Connect to Gmail SMTP Server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [to_email], msg.as_string())

        return f"Email successfully dispatched to {to_email} in the background, sir."
    except Exception as e:
        return f"Failed to transmit email message payload: {str(e)}"