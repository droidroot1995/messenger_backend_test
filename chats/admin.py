from django.contrib import admin
from chats.models import Chat, Member, Message, Attachment
# Register your models here.


class ChatAdmin(admin.ModelAdmin):
    list_display=('id', 'topic')
    #pass

class MessageAdmin(admin.ModelAdmin):
    list_display=('id', 'chat_id', 'user_id')
    #pass

class AttachmentAdmin(admin.ModelAdmin):
    list_display=('id', 'chat_id', 'message_id', 'user_id')
    #pass

class MemberAdmin(admin.ModelAdmin):
    list_display=('id', 'chat_id', 'user_id')
    #pass
    
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Member, MemberAdmin)