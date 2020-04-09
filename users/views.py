from django.shortcuts import render
from django.http import JsonResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required

from django.apps import apps

from rest_framework import viewsets
from rest_framework.response import Response
from users.serializers import UserSerializer
from rest_framework.decorators import action
# Create your views here.


'''@csrf_exempt
@require_GET
@login_required
def index(request):
    return render(request, 'users_index.html')'''


@csrf_exempt
@require_GET
@login_required
def profile_details(request):
    User = apps.get_model('users', 'User')
    #user = User.objects.filter(id=request.GET['user_id']).values('id', 'username', 'first_name', 'avatar').first()
    user = User.objects.filter(id=request.user.id).values('id', 'username', 'first_name', 'avatar').first()
    return JsonResponse({'profile': user})

@cache_page(60*15)
@csrf_exempt
@require_GET
@login_required
def contacts_list(request):
    User = apps.get_model('users', 'User')
    
    users = User.objects.all().values('id', 'username', 'first_name', 'avatar')
    return JsonResponse({'contacts': list(users)})
    
    
@csrf_exempt
@require_GET
@login_required
def search_users(request):
    User = apps.get_model('users', 'User')
    
    users = User.objects.filter(username__contains=request.GET['name']).values('id', 'username', 'first_name', 'avatar')[:int(request.GET['limit'])]
    return JsonResponse({'users': list(users)})


class UsersViewSet(viewsets.ModelViewSet):
    
    User = apps.get_model('users', 'User')
    
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    @action(methods=['get'], detail=False)
    def search_users(self, request):
        users = self.get_queryset()
        users = users.filter(username__contains=request.GET['name'])[:int(request.GET['limit'])]
        serializer = self.get_serializer(users, many=True)
        return Response({'users': serializer.data})
    
    @method_decorator(cache_page(60*15))
    @action(methods=['get'], detail=False)
    def contacts(self, request):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response({'contacts': serializer.data})

    @action(methods=['get'], detail=False)
    def profile_details(self, request):
        user = self.get_queryset()
        user = user.filter(id=request.user.id).first()
        serializer = self.get_serializer(user, many=False)
        return Response({'profile': serializer.data})
