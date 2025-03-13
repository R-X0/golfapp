from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from app import mail
from time import time
import jwt

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(
        target=send_async_email, 
        args=(current_app._get_current_object(), msg)
    ).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        '[Pars.Golf] Reset Your Password',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )

def generate_reset_token(user_id, expires_in=600):
    return jwt.encode(
        {'reset_password': user_id, 'exp': time() + expires_in},
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_reset_token(token):
    try:
        from app.models.user import User
        id = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )['reset_password']
        return User.query.get(id)
    except:
        return None