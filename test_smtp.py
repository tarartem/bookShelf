import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

def test_smtp():
    load_dotenv()
    
    host = os.getenv("SMTP_HOST")
    port_env = os.getenv("SMTP_PORT", "587")
    port = int(port_env) if port_env and port_env.strip() else 587
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("SENDER_EMAIL") or user
    
    print(f"--- SMTP Test Config ---")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Sender: {sender}")
    print(f"Password set: {'Yes' if password else 'No'}")
    print(f"------------------------")
    
    if not host or not user or not password:
        print("Error: Missing SMTP configuration in .env")
        return

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = user
    msg["Subject"] = "SMTP Test from BookShelf"
    msg.set_content("This is a test email to verify your SMTP settings.")
    
    try:
        print(f"Connecting to {host}:{port}...")
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.set_debuglevel(1)
            print("Sending EHLO...")
            server.ehlo()
            print("Starting TLS...")
            server.starttls()
            print("Sending EHLO after TLS...")
            server.ehlo()
            print(f"Logging in as {user}...")
            server.login(user, password)
            print("Sending message...")
            server.send_message(msg)
        print("\n✅ SMTP Test SUCCESSFUL! Check your inbox.")
    except Exception as e:
        print(f"\n❌ SMTP Test FAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_smtp()
