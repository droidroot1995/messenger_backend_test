from django.db import models

# Create your models here.


class Chat(models.Model):
    is_group_chat = models.BooleanField()
    topic = models.TextField(max_length=64)
    last_message = models.TextField(max_length=256)
    
    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'
    

class Message(models.Model):
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(to='users.User', on_delete=models.CASCADE)
    content = models.TextField(max_length=256)
    added_at = models.DateTimeField(null=True, auto_now_add=True)
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-added_at']
    

class Attachment(models.Model):
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(to='users.User', on_delete=models.CASCADE)
    message = models.ForeignKey(to=Message, on_delete=models.CASCADE)
    att_type = models.TextField(max_length=64)
    url = models.FileField(upload_to='attachments/')
    
    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
    

class Member(models.Model):
    user = models.ForeignKey(to='users.User', on_delete=models.CASCADE)
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE)
    new_messages = models.IntegerField()
    last_read_message = models.ForeignKey(to=Message, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
