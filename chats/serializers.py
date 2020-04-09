from rest_framework import serializers
from chats.models import Chat, Attachment, Member, Message

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'chat', 'user', 'message', 'att_type', 'url')

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('id', 'is_group_chat', 'topic', 'last_message')
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'chat', 'user', 'content', 'added_at')
        
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('id', 'user_id', 'chat_id', 'new_messages', 'last_read_message')
