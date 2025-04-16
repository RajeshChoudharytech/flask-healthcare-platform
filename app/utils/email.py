from flask_mail import Message
from app import mail
from flask import current_app
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, body):
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients, body=body)
    Thread(target=send_async_email, args=(app, msg)).start()
