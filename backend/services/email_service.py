import os
import smtplib
import logging
from email.message import EmailMessage
from email.utils import formatdate
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USER)


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
    msg["Subject"] = f"📚 Your book: {book_title} - {author}"
    msg.set_content(
        f"Hello,\n\nYour requested book «{book_title}» by {author} is attached.\n\nEnjoy reading!\n\nBookShelf App"
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
        logger.info(f"Connecting to SMTP {SMTP_HOST}:{SMTP_PORT} …")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}")
        return False
