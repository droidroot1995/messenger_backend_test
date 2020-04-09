from __future__ import absolute_import, unicode_literals

from django.core.mail import EmailMessage, send_mail
from application.celery import app
from django.apps import apps

@app.task(bind=True)
def users_count():
    
    User = apps.get_model('users', 'User')
    users = len(list(User.objects.all()))
    
    message = EmailMessage(
        'Количество пользователей',
        'На текущий момент в приложении зарегистрировано ' + str(users) + ' пользователей',
        'droidroot.ttfs@gmail.com',
        ['droidroot1995@gmail.com'],
    )
    
    message.send()