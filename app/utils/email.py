from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME="your-email@example.com",
    MAIL_PASSWORD="your-email-password",
    MAIL_FROM="your-email@example.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,      # Use this instead of MAIL_TLS
    MAIL_SSL_TLS=False,      # Use this instead of MAIL_SSL
    USE_CREDENTIALS=True,
    # TEMPLATE_FOLDER="app/templates/email"  # Comment out if not using templates
)

fm = FastMail(conf)

async def send_email(subject: str, recipients: list[EmailStr], body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="html"
    )
    await fm.send_message(message)
