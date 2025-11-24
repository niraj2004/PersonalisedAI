import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ.get("RESEND_API_KEY")

def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends an email using Resend.
    """
    try:
        params = {
            "from": "Personal Learning Assistant <onboarding@resend.dev>", # Default Resend testing domain
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        
        email = resend.Emails.send(params)
        return email
    except Exception as e:
        print(f"Error sending email: {e}")
        raise e
