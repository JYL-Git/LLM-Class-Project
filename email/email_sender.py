import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

def send_email(subject, body, to_email):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        raise ValueError("❌ 이메일 주소 또는 비밀번호가 환경변수에 설정되지 않았습니다.")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
