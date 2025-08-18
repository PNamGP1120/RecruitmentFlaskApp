from flask_mail import Message
from app import app, mail

def send_email_notification(to_email, subject, body):
    if not to_email:
        return
    try:
        msg = Message(subject=subject,
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[to_email])
        msg.body = body
        mail.send(msg)
    except Exception as e:
        print(f"[!] Error sending email: {str(e)}")
