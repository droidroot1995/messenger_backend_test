# Generated by Django 2.2.5 on 2019-10-31 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('att_type', models.TextField(max_length=64)),
                ('url', models.TextField(max_length=128)),
            ],
            options={
                'verbose_name': 'Вложение',
                'verbose_name_plural': 'Вложения',
            },
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_group_chat', models.BooleanField()),
                ('topic', models.TextField(max_length=64)),
                ('last_message', models.TextField(max_length=256)),
            ],
            options={
                'verbose_name': 'Чат',
                'verbose_name_plural': 'Чаты',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_messages', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Участник',
                'verbose_name_plural': 'Участники',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=256)),
                ('added_at', models.DateTimeField()),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chats.Chat')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
                'ordering': ['-added_at'],
            },
        ),
    ]
