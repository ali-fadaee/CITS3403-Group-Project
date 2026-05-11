from flask import current_app, url_for, render_template
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app.extensions import mail

def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except Exception:
        return None
    return email

def send_verification_email(user):
    token = generate_token(user.email)
    verification_url = url_for('main.verify_email', token=token, _external=True)
    msg = Message(
        subject="Verify your email – debates-app",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email]
    )
    msg.html = render_template(
        "email/verify_email.html",
        username=user.username,
        verify_url=verification_url
    )
    mail.send(msg)