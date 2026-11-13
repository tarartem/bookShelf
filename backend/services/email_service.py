import os
import smtplib
import logging
import base64
import json
import urllib.request
import ssl
from email.message import EmailMessage
from email.utils import formatdate
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
_port_env = os.getenv("SMTP_PORT", "587")
SMTP_PORT = int(_port_env) if _port_env and _port_env.strip() else 587
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL") or SMTP_USER


def _send_brevo_api(to_email: str, subject: str, text_content: str, attachment: dict = None) -> bool:
    """Send an email via Brevo HTTPS REST API (Port 443 - never blocked by cloud firewalls)."""
    if not BREVO_API_KEY:
        return False

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "sender": {"name": "BookShelf", "email": SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_content
    }
    if attachment:
        payload["attachment"] = [attachment]

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    ctx = ssl.create_default_context()

    try:
        logger.info(f"Dispatching email to {to_email} via Brevo HTTPS API...")
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            logger.info(f"✅ Brevo API email sent successfully to {to_email} (status {resp.status})")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        logger.error(f"❌ Brevo API HTTP error ({e.code}): {error_body}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send via Brevo API: {type(e).__name__}: {e}")
        return False


def send_epub_email(to_email: str, book_title: str, author: str, epub_path: str) -> bool:
    """Send the EPUB file as an email attachment via Brevo HTTPS API or SMTP."""
    if not os.path.exists(epub_path):
        logger.error(f"EPUB file not found: {epub_path}")
        return False

    subject = f"📚 Ваша книга: {book_title} - {author}"
    body = (
        f"Добрий день!\n\n"
        f"Ваша замовлена книга «{book_title}» автора {author} додана як вкладення.\n\n"
        f"Приємного читання!\n\nBookShelf App"
    )

    # 1. Prefer Brevo HTTPS API (Port 443) if configured
    if BREVO_API_KEY:
        try:
            with open(epub_path, "rb") as f:
                b64_content = base64.b64encode(f.read()).decode("utf-8")
            attachment = {
                "name": f"{book_title}.epub",
                "content": b64_content
            }
            return _send_brevo_api(to_email, subject, body, attachment=attachment)
        except Exception as e:
            logger.error(f"Failed to prepare EPUB for Brevo API: {e}")
            return False

    # 2. Fallback to standard SMTP
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        logger.error("Neither BREVO_API_KEY nor SMTP configured. Email was NOT sent.")
        return False

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = subject
    msg.set_content(body)

    with open(epub_path, "rb") as f:
        epub_data = f.read()

    msg.add_attachment(
        epub_data,
        maintype="application",
        subtype="epub+zip",
        filename=f"{book_title}.epub",
    )

    try:
        logger.info(f"Attempting to send email to {to_email} via SMTP {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info(f"✅ Email successfully sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send SMTP email to {to_email}: {type(e).__name__}: {e}")
        return False


def send_verification_email(to_email: str, token: str) -> bool:
    """Send verification email with a link."""
    base_url = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
    verification_url = f"{base_url}/verify.html?token={token}"
    subject = "🔐 Підтвердите ваш акаунт BookShelf"
    body = (
        f"Добрий день!\n\n"
        f"Дякуємо вас у BookShelf! Будь ласка, підтвердіть свій акаунт, натиснувши на посилання нижче:\n\n"
        f"{verification_url}\n\n"
        f"Це посилання дійсне протягом 24 годин.\n\n"
        f"Приємного читання!\nКоманда BookShelf"
    )

    if BREVO_API_KEY:
        return _send_brevo_api(to_email, subject, body)

    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        logger.error("SMTP not configured. Verification email NOT sent.")
        return False

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = subject
    msg.set_content(body)

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


def send_reset_email(email: str, token: str) -> bool:
    """Send password reset email with a link."""
    base_url = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
    reset_url = f"{base_url}/reset-password.html?token={token}"
    subject = "🔑 Скидання пароля BookShelf"
    body = (
        f"Добрий день!\n\n"
        f"Ви запитали зміну пароля. Будь ласка, натисніть на посилання нижче, щоб встановити новий пароль:\n"
        f"{reset_url}\n\n"
        f"Це посилання дійсне протягом 1 години. Якщо ви не запитували цього, ви можете ігнорувати цей лист.\n\n"
        f"З повагою,\nКоманда BookShelf"
    )

    if BREVO_API_KEY:
        return _send_brevo_api(email, subject, body)

    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        logger.error("SMTP not configured. Reset email NOT sent.")
        return False

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
        return True
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}: {e}")
        return False
