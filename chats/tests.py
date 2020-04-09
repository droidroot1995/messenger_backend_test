import json
from django.test import TestCase, Client
from mock import patch
from chats.models import Chat, Message, Member, Attachment
from chats.factories import ChatMessagesFactory
from users.models import User

# Create your tests here.

class TestChatsViews(TestCase):
    
    def setUp(self):
        print("Starting chats tests")
        self.client = Client()
        
        self.user = User.objects.create(username="test_user")
        self.user.set_password("12345")
        self.user.save()
        
        self.user_first = User.objects.create(username="test_user_first")
        self.user_first.set_password("12345")
        self.user_first.save()
        
        self.logged_in = self.client.login(username="test_user", password="12345")
        
        
        self.chat = Chat.objects.create(is_group_chat=False, topic='', last_message='')
        self.chat.save()
        
        self.member_first = Member.objects.create(user_id=1, chat_id=1, new_messages=0)
        self.member_second = Member.objects.create(user_id=2, chat_id=1, new_messages=0)        
        
        
    def test_chat_page(self):
        response = self.client.get('/chats/chat?chat_id=1')
        self.assertJSONEqual(response.content, '{"chat": {"id": 1, "is_group_chat": false, "topic": "", "last_message": ""}}')
        
        
    def test_chat_list(self):
        response = self.client.get('/chats/list')
        self.assertJSONEqual(response.content, '{"chat_list": [{"id": 1, "is_group_chat": false, "topic": "", "last_message": ""}]}')
        
    def test_create_personal_chat(self):
        response = self.client.post('/chats/create_pers_chat', {'target_user_id': 2})
        self.assertJSONEqual(response.content, '{"chat": {"id": 1, "is_group_chat": false, "topic": "", "last_message": ""}}')
    
    def test_user_chat_list(self):
        response = self.client.get('/chats/list_chats')
        self.assertJSONEqual(response.content, '{"chats": [{"id": 1, "is_group_chat": false, "topic": "", "last_message": ""}]}')
    
    def test_read_message(self):
        message = ChatMessagesFactory.create()
        response = self.client.post('/chats/read_msg', { 'message_id': 1})
        self.assertJSONEqual(response.content, '{"chat": -1}')
    
    def test_send_message(self):
        message = ChatMessagesFactory.build()
        response = self.client.post('/chats/send_msg', {'chat': message.chat_id, 'content': message.content})
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
    
    def test_chat_messages_list(self):
        message = ChatMessagesFactory.create()
        response = self.client.get('/chats/chat_msg_list?chat_id=1')
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
    
    
    @patch('chats.views.upload_file')
    def test_upload_file(self, upload_file_mock):
        upload_file_mock()
        upload_file_mock.return_value = {'id': 1, 
                           'chat_id': 1, 
                           'user_id': 1, 
                           'message_id': 1, 
                           'att_type': 'form/multipart',
                           'url': 'sth'}
        
        self.assertTrue(upload_file_mock.called)
        self.assertEqual(upload_file_mock.call_count, 1)
    
    @patch('chats.views.protected_file')
    def test_protected_file(self, protected_file_mock):
        protected_file_mock()
        protected_file_mock.return_value = True
        self.assertTrue(protected_file_mock.called)
        self.assertEqual(protected_file_mock.call_count, 1)
        
    def tearDown(self):
        print("Chats tests ended")