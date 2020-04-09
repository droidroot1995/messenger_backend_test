from django.urls import path, re_path
from django.urls import include
from chats.views import (chat_page, chat_list, user_chat_list, 
                         create_personal_chat, send_message, chat_messages_list, 
                         read_message, upload_file, protected_file)

from chats.views import AttachmentsViewSet, ChatsViewSet, MessagesViewSet # MembersViewSet, 
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'attachments', AttachmentsViewSet)
router.register(r'chats', ChatsViewSet) 
#router.register(r'members', MembersViewSet, basename='member') 
router.register(r'messages', MessagesViewSet) 

urlpatterns = [
    re_path(r'^files/.+$', protected_file, name="protected_file"),
    # path('index', index, name='index'),
    # path('detail/<int:pk>', chat_detail, name='chat_detail'),
    # path('chat/<int:chat_id>', chat_page, name='chat_page'),
    path('chat', chat_page, name='chat_page'),
    path('list', chat_list, name='chat_list'),
    path('list_chats', user_chat_list, name='user_chat_list'),
    path('create_pers_chat', create_personal_chat, name='create_personal_chat'),
    path('send_msg', send_message, name='send_message'),
    path('chat_msg_list', chat_messages_list, name='chat_messages_list'),
    path('read_msg', read_message, name="read_message"),
    path('upload', upload_file, name="upload_file")
] + router.urls