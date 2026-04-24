import os
import smtplib
import logging
from email.message import EmailMessage
from email.utils import formatdate
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "")
_port_env = os.getenv("SMTP_PORT", "587")
SMTP_PORT = int(_port_env) if _port_env and _port_env.strip() else 587
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL") or SMTP_USER


def send_epub_email(to_email: str, book_title: str, author: str, epub_path: str) -> bool:
    """Send the EPUB file as an email attachment via SMTP."""

    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        logger.error(
            "SMTP not configured. Set SMTP_HOST, SMTP_USER, SMTP_PASS env vars "
            "(see .env.example). Email was NOT sent."
        )
        return False

    if not os.path.exists(epub_path):
        logger.error(f"EPUB file not found: {epub_path}")
        return False

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = f"📚 Ваша книга: {book_title} - {author}"
    msg.set_content(
        f"Добрий день!\n\nВаша замовлена книга «{book_title}» автора {author} додана як вкладення.\n\nПриємного читання!\n\nBookShelf App"
    )

    with open(epub_path, "rb") as f:
        epub_data = f.read()

    msg.add_attachment(
        epub_data,
        maintype="application",
        subtype="epub+zip",
        filename=f"{book_title}.epub",
    )

    try:
        logger.info(f"Attempting to send email to {to_email} via {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            # server.set_debuglevel(1) # Disabled verbose logging for production
            server.ehlo()
            server.starttls()
            server.ehlo()
            logger.info(f"Logging in as {SMTP_USER}...")
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info(f"✅ Email successfully sent to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(f"❌ SMTP Authentication failed for {SMTP_USER}. Check SMTP_PASS/App Password.")
        return False
    except smtplib.SMTPConnectError:
        logger.error(f"❌ Failed to connect to SMTP server {SMTP_HOST}:{SMTP_HOST}.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {type(e).__name__}: {e}")
        return False

def send_verification_email(to_email: str, token: str) -> bool:
    """Send verification email with a link."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        logger.error("SMTP not configured. Verification email NOT sent.")
        return False

    base_url = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
    verification_url = f"{base_url}/verify.html?token={token}"

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = "🔐 Підтвердите ваш акаунт BookShelf"
    msg.set_content(
        f"Добрий день!\n\nДякуємо вас у BookShelf! Будь ласка, підтвердіть свій акаунт, натиснувши на посилання нижче:\n\n"
        f"{verification_url}\n\n"
        f"Це посилання дійсне протягом 24 годин.\n\nПриємного читання!\nКоманда BookShelf"
    )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info(f"✅ Verification email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {to_email}: {e}")
        return False

def send_reset_email(email: str, token: str):
    base_url = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
    reset_url = f"{base_url}/reset-password.html?token={token}"
    subject = "🔑 Скидання пароля BookShelf"
    body = f'''
    Добрий день!
    
    Ви запитали зміну пароля. Будь ласка, натисніть на посилання нижче, щоб встановити новий пароль:
    {reset_url}
    
    Це посилання дійсне протягом 1 години. Якщо ви не запитували цього, ви можете ігнорувати цей лист.
    
    З повагою,
    Команда BookShelf
    '''
    try:
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}: {e}")
        return False
