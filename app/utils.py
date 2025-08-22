import smtplib
import base64
from email.mime.text import MIMEText
from flask_dance.contrib.google import google

def send_email_oauth2(to_email: str, subject: str, body: str) -> bool:
    """
    Gửi email thông báo sử dụng Gmail SMTP OAuth2.

    Args:
        to_email (str): Địa chỉ email người nhận.
        subject (str): Tiêu đề email.
        body (str): Nội dung email.

    Returns:
        bool: True nếu gửi thành công, False nếu thất bại.
    """
    if not to_email:
        print("[!] No recipient email provided.")
        return False

    if not google.authorized:
        print("[!] Google OAuth token not available.")
        return False

    try:
        access_token = google.token["access_token"]
        sender_email = "your_email@gmail.com"  # Thay bằng email của bạn

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        # Tạo OAuth2 authentication string
        auth_string = f"user={sender_email}\1auth=Bearer {access_token}\1\1"
        auth_string = base64.b64encode(auth_string.encode()).decode()

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.docmd("AUTH", "XOAUTH2 " + auth_string)
            server.sendmail(sender_email, [to_email], msg.as_string())

        print(f"[+] Email sent to {to_email} successfully.")
        return True

    except Exception as e:
        print(f"[!] Error sending email to {to_email}: {str(e)}")
        return False
