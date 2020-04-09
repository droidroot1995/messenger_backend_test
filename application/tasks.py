from __future__ import absolute_import, unicode_literals
from application.celery import app

@app.task()
def debug_task():
    print('demo')