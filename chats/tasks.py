from __future__ import absolute_import, unicode_literals

from django.core.mail import EmailMessage, send_mail, get_connection
from application.celery import app
from celery import shared_task

@app.task()
def send_email(subject, sender, recipients, text):
    # send_mail(subject, text, sender, recipients, auth_user='apikey', auth_password='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', fail_silently=False)
    # connection = get_connection()
    
    message = EmailMessage(
        subject,
        text,
        sender,
        recipients,
    )
    
    message.send()
    
    # connection.send_messages([message])
    # connection.close()