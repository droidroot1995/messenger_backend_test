# Generated by Django 2.2.5 on 2019-11-19 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0005_auto_20191114_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='url',
            field=models.FileField(upload_to='attachmets'),
        ),
    ]