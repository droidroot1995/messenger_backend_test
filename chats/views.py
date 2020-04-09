from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from django.conf import settings

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http  import require_GET, require_POST
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required

from chats.forms import ChatForm, MemberForm, MessageForm, AttachmentForm
from django.apps import apps
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response
from chats.serializers import ChatSerializer, MemberSerializer, AttachmentSerializer, MessageSerializer
from rest_framework.decorators import action

from rest_framework.authentication import SessionAuthentication, BasicAuthentication 

from chats.tasks import send_email

import requests

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

# Create your views here.
'''@csrf_exempt
@require_GET
@login_required
def index(request):
    return render(request, 'chats_index.html')'''


'''@csrf_exempt
@require_GET
@login_required
def chat_detail(request, pk):
    return JsonResponse({'test' : 'App'})'''


@csrf_exempt
@require_GET
@login_required
def chat_page(request):
    Chat = apps.get_model('chats', 'Chat')
    
    chat = Chat.objects.filter(id=int(request.GET['chat_id'])).values('id', 'is_group_chat', 'topic', 'last_message').first()
    return JsonResponse({'chat': chat})


@cache_page(60*5)
@csrf_exempt
@require_GET
@login_required
def chat_list(request):
    Chat = apps.get_model('chats', 'Chat')
    
    chats = Chat.objects.all().values('id', 'is_group_chat', 'topic', 'last_message')
    return JsonResponse({'chat_list': list(chats)})
    
    
@csrf_exempt
@require_POST
@login_required
def create_personal_chat(request):
    Member = apps.get_model('chats', 'Member')
    Chat = apps.get_model('chats', 'Chat')
    User = apps.get_model('users', 'User')
        
    uid  = request.user.id
    #uid  = int(request.POST['user_id'])
    target_user_id = int(request.POST['target_user_id'])
    
    user1 = User.objects.filter(id=uid).first()
    user2 = User.objects.filter(id=target_user_id).first()
    
    recipients = []
    if user1 != None and user1.email != '':
        recipients.append(user1.email)
        
    if user2 != None and user2.email != '':
        recipients.append(user2.email)
    
    member1_chat_set = set(Member.objects.filter(user_id=uid).values_list('chat_id'))
    member2_chat_set = set(Member.objects.filter(user_id=target_user_id).values_list('chat_id'))
    
    union_chats = list(member1_chat_set & member2_chat_set)
    
    if union_chats:
        for c in union_chats:
            chat = Chat.objects.filter(id=c[0]).first()
            
            if not chat.is_group_chat:
                chat_json = {'id': chat.id, 'is_group_chat': chat.is_group_chat, 'topic': chat.topic, 'last_message': chat.last_message}
                return JsonResponse({'chat': chat_json})
        
    chat = Chat.objects.create(is_group_chat=False, topic='', last_message='')
    
    chat_json = {'id': chat.id, 'is_group_chat': chat.is_group_chat, 'topic': chat.topic, 'last_message': chat.last_message }    
    
    member1 = Member.objects.create(user_id=uid, chat_id=chat.id, new_messages=0)            
    member2 = Member.objects.create(user_id=target_user_id, chat_id=chat.id, new_messages=0)
    
    send_email.delay('New chat created', settings.DEFAULT_FROM_EMAIL, recipients, 'New chat was created')
    
    return JsonResponse({'chat': chat_json})
    
# @cache_page(60*5)    
@csrf_exempt
@require_GET
@login_required
def user_chat_list(request):
    Member = apps.get_model('chats', 'Member')
    Chat = apps.get_model('chats', 'Chat')
    
    chat_lst = []
    members = Member.objects.filter(user_id=request.user.id)
    #members = Member.objects.filter(user_id=request.GET['user_id'])
    
    for member in members:
        chat = Chat.objects.filter(id=member.chat_id).first()
        chat_json = {'id': chat.id, 'is_group_chat': chat.is_group_chat, 'topic': chat.topic, 'last_message': chat.last_message}
        chat_lst.append(chat_json)
    
    return JsonResponse({'chats': chat_lst})


@csrf_exempt
@require_POST
@login_required
def read_message(request):
    Member = apps.get_model('chats', 'Member')
    Message = apps.get_model('chats', 'Message')
    
    message = Message.objects.filter(id=int(request.POST['message_id'])).first()
    
    if message:
        member = Member.objects.filter(user_id=request.user.id, chat_id=message.chat_id).first()
        #member = Member.objects.filter(user_id=request.GET['user_id'], chat_id=message.chat_id).first()
        if member:
            
            if member.last_read_message == None or member.last_read_message_id < int(request.POST['message_id']):
                member.last_read_message_id = int(request.POST['message_id'])
                member.new_messages -= 1
                member.save()            
            
            return JsonResponse({'chat': member.new_messages})
        
        return JsonResponse({'member': 'Member not found'}, status=400)
    
    return JsonResponse({'message': 'Message not found'}, status=400)
           
    

@csrf_exempt
@require_POST
@login_required
def send_message(request):
    Member = apps.get_model('chats', 'Member')
    Chat = apps.get_model('chats', 'Chat')
    Message = apps.get_model('chats', 'Message')
    
    form = MessageForm(request.POST)
    
    if form.is_valid():
        #message = form.save()
        
        message = Message.objects.create(chat_id=form.cleaned_data['chat'].id, user_id=request.user.id, 
                                         content=form.cleaned_data['content']) #, added_at=form.cleaned_data['added_at'])
        
        msg = {'id': message.id, 'chat_id': message.chat.id, 'user_id': message.user.id, 'content': message.content} # , 'added_at': message.added_at}
        
        chat = Chat.objects.filter(id=message.chat.id).first()
        
        if chat:
            chat.last_message = message.content
            chat.save()
        
        members = list(Member.objects.filter(chat_id=message.chat.id).exclude(user_id=message.user.id))
        for member in members:
            member.new_messages += 1
            member.save()
            
        # msg_ws = {'id': message.id, 'chat_id': message.chat.id, 'user_id': message.user.id, 'content': message.content , 'added_at': message.added_at}
        
        requests.post('http://localhost:8080/api', json={
            "method": "publish",
            "params": {
                "channel": "chat" + str(message.chat.id),
                "data": {
                    'message': msg
                }
            }
        }, headers={'Authorization': 'apikey ' + settings.CENTRIFUGE_API})
        return JsonResponse({"result": {'message': msg}})
    
    return JsonResponse({'errors': form.errors}, status=400)


@csrf_exempt
@require_GET
@login_required
def chat_messages_list(request):
    Message = apps.get_model('chats', 'Message')
    
    messages = Message.objects.filter(chat_id=int(request.GET['chat_id'])).values('id', 'chat_id', 'user_id', 'content', 'added_at')
    return JsonResponse({'messages': list(messages)})

@csrf_exempt
@require_POST
@login_required
def upload_file(request):
    Attachment = apps.get_model('chats', 'Attachment')
    
    form = AttachmentForm(request.POST, request.FILES)
    
    if form.is_valid():
        #attachment = form.save()
        
        attachment = Attachment.objects.create(chat_id=form.cleaned_data['chat'], user_id=request.user.id, message_id=form.cleaned_data['message'],
                                               att_type=form.cleaned_data['att_type'], url=form.cleaned_data['url'])
        
        attachment_json = {'id': attachment.id, 
                           'chat_id': attachment.chat.id, 
                           'user_id': attachment.user.id, 
                           'message_id': attachment.message.id, 
                           'att_type': attachment.att_type,
                           'url': attachment.url.url.replace('http://hb.bizmrg.com/track-goryakin/', '/chats/files/')}
        
        return JsonResponse({'attachment': attachment_json})
    
    
    return JsonResponse({'errors': form.errors}, status=400)

@csrf_exempt
@require_GET
@login_required
def protected_file(request):
    if request.user.is_authenticated:
        url = request.path.replace('/chats/files', '/protected')
        print(url)
        response = HttpResponse(status=200)
        response['X-Accel-Redirect'] = url
        print(response.has_header('X-Accel-Redirect'))
        
        if 'Expires' in request.GET.keys():
            response['X-Accel-Expires'] = request.GET['Expires']
        response['Content-type'] = ''
        return response
    else:
        return HttpResponse('<h1>File not found</h1>', status=404)


class AttachmentsViewSet(viewsets.ModelViewSet):
    
    Attachment = apps.get_model('chats', 'Attachment')
    Chat = apps.get_model('chats', 'Chat')
    Member = apps.get_model('chats', 'Member')
    Message = apps.get_model('chats', 'Message')
    User = apps.get_model('users', 'User')
    
    serializer_class = AttachmentSerializer
    queryset = Attachment.objects.all()
    
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    
    @action(methods=['post'], detail=False)
    def upload_file(self, request):
        
        pst = request.POST.copy()
        pst['url'] = request.FILES['url']
    
        attachment = self.get_serializer(data=pst)
        if attachment.is_valid():
            #attachment = form.save()
            attachment.save()
            
            '''attachment = Attachment.objects.create(chat_id=form.cleaned_data['chat'], user_id=request.user.id, message_id=form.cleaned_data['message'],
                                                att_type=form.cleaned_data['att_type'], url=form.cleaned_data['url'])'''
            
            '''attachment_json = {'id': attachment.id, 
                            'chat_id': attachment.chat.id, 
                            'user_id': attachment.user.id, 
                            'message_id': attachment.message.id, 
                            'att_type': attachment.att_type,
                            'url': attachment.url.url.replace('http://hb.bizmrg.com/track-goryakin/', '/chats/files/')}'''
            serialized = attachment.data
            serialized['url'] = serialized['url'].replace('http://hb.bizmrg.com/track-goryakin/', '/chats/attachments/protected_file/')
            
            return Response({'attachment': serialized})
        
        
        return Response({'errors': attachment.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['get'], detail=False, url_path=r'protected_file/.+')
    def protected_file(self, request):
        if request.user.is_authenticated:
            url = request.path.replace('/chats/attachments/protected_file', '/protected')
        response = Response(status=200)
        response['X-Accel-Redirect'] = url
        
        if 'Expires' in request.GET.keys():
            response['X-Accel-Expires'] = request.GET['Expires']
            response['Content-type'] = ''
            return response
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ChatsViewSet(viewsets.ModelViewSet):
    
    Attachment = apps.get_model('chats', 'Attachment')
    Chat = apps.get_model('chats', 'Chat')
    Message = apps.get_model('chats', 'Message')
    User = apps.get_model('users', 'User')
    
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    
    @action(methods=['post'], detail=False)
    def create_personal_chat(self, request):
        chats = self.get_queryset()
        
        Member = apps.get_model('chats', 'Member')
        Chat = apps.get_model('chats', 'Chat')
        User = apps.get_model('users', 'User')
            
        uid  = request.user.id
        target_user_id = int(request.POST['target_user_id'])
        
        user1 = User.objects.filter(user_id=uid).first()
        user2 = User.objects.filter(user_id=target_user_id).first()
        
        recipients = []
        if user1.email != '':
            recipients.append(user1.email)
            
        if user2.email != '':
            recipients.append(user2.email)
        
        member1_chat_set = set(Member.objects.filter(user_id=uid).values_list('chat_id'))
        member2_chat_set = set(Member.objects.filter(user_id=target_user_id).values_list('chat_id'))
        
        union_chats = list(member1_chat_set & member2_chat_set)
        
        if union_chats:
            for c in union_chats:
                chat = chats.filter(id=c[0]).first()
                
                if not chat.is_group_chat:
                    serializer = self.get_serializer(chat, many=False)
                    return Response({'chat': serializer.data})
            
        chat = Chat.objects.create(is_group_chat=False, topic='', last_message='')
        
        serializer = self.get_serializer(chat, many=False)  
        
        member1 = Member.objects.create(user_id=uid, chat_id=chat.id, new_messages=0)            
        member2 = Member.objects.create(user_id=target_user_id, chat_id=chat.id, new_messages=0)
        
        send_email.delay('New chat created', 'droidroot.ttfs@gmail.com', recipients, 'New chat was created')
        
        return Response({'chat': serializer.data})
        
    @action(methods=['get'], detail=False)
    def chat_page(self, request):
        chat = self.get_queryset()
        chat = chat.filter(id=int(request.GET['chat_id'])).first()
        
        serializer = self.get_serializer(chat, many=False)
        return Response({'chat': serializer.data})
    
    @method_decorator(cache_page(5))
    @action(methods=['get'], detail=False)
    def chat_list(self, request):
        chats = self.get_queryset()
        serializer = self.get_serializer(chats, many=True)
        return Response({'chat_list': serializer.data})
    
    @method_decorator(cache_page(5))
    @action(methods=['get'], detail=False)
    def user_chat_list(self, request):
        Member = apps.get_model('chats', 'Member')
        chats = self.get_queryset()
        
        chat_lst = []
        members = Member.objects.filter(user_id=request.user.id)
    
        for member in members:
            chat = chats.filter(id=member.chat_id).first()
            serializer = self.get_serializer(chat, many=False)
            chat_lst.append(serializer.data)
            
        return Response({'chats': chat_lst})
        
        
    
'''class MembersViewSet(viewsets.ModelViewSet):
    
    Attachment = apps.get_model('chats', 'Attachment')
    Chat = apps.get_model('chats', 'Chat')
    Member = apps.get_model('chats', 'Member')
    Message = apps.get_model('chats', 'Message')
    User = apps.get_model('users', 'User')
    
    serializer_class = MemberSerializer
    queryset = Member.objects.all()'''
    
class MessagesViewSet(viewsets.ModelViewSet):
    
    Attachment = apps.get_model('chats', 'Attachment')
    
    
    Message = apps.get_model('chats', 'Message')
    User = apps.get_model('users', 'User')
    
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    
    @action(methods=['get'], detail=False)
    def chat_messages_list(self, request):
        
        messages = self.get_queryset()
    
        messages = messages.filter(chat_id=int(request.GET['chat_id']))
        serializer = self.get_serializer(messages, many=True)
        return Response({'messages': serializer.data})
    
    @action(methods=['post'], detail=False)
    def read_message(self, request):
        Member = apps.get_model('chats', 'Member')
        message = self.get_queryset()
        
        message = message.filter(id=int(request.POST['message_id'])).first()
        
        if message:
            #member = Member.objects.filter(user_id=request.user.id, chat_id=message.chat_id).first()
            member = Member.objects.filter(user_id=request.POST['user_id'], chat_id=message.chat_id).first()
            #member = Member.objects.filter(user_id=request.GET['user_id'], chat_id=message.chat_id).first()
            if member:
                
                if member.last_read_message == None or member.last_read_message_id < int(request.POST['message_id']):
                    member.last_read_message_id = int(request.POST['message_id'])
                    member.new_messages -= 1
                    member.save()            
                
                return Response({'chat': member.new_messages})
            
            return Response({'member': 'Member not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Message not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['post'], detail=False)
    def send_message(self, request):
        Chat = apps.get_model('chats', 'Chat')
        Member = apps.get_model('chats', 'Member')
        
        message = self.get_serializer(data=request.POST, many=False)
    
        if message.is_valid():
            message.save()
            
            chat = Chat.objects.filter(id=message.validated_data['chat'].id).first()
            
            if chat:
                chat.last_message = message.validated_data['content']
                chat.save()
            
            members = list(Member.objects.filter(chat_id=message.validated_data['chat'].id).exclude(user_id=message.validated_data['user'].id))
            for member in members:
                member.new_messages += 1
                member.save()
            
            
            return Response({'message': message.data})
        
        return Response({'errors': message.errors}, status=status.HTTP_400_BAD_REQUEST)