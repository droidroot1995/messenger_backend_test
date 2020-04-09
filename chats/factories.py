import factory
from factory.django import DjangoModelFactory
from chats.models import Message

class ChatMessagesFactory(DjangoModelFactory):
    
    class Meta:
        model = Message
    
    chat_id = 1
    user_id = 1
    content = factory.Faker('first_name')