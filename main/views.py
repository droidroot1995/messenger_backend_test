from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http  import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from main.forms import LoginForm

from django.conf import settings
import jwt
# Create your views here.

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

def centrifugo_token(request):
    token = jwt.encode({'sub': str(request.user.id)}, settings.CENTRIFUGE_SECRET, algorithm="HS256").decode()
    return JsonResponse({ 'token': token })

def login(request):
    form = LoginForm()
    context = {'form' : form}
    return render(request, 'login.html', context)

def legacy_login(request):
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
        
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect('/')

    return HttpResponseRedirect('/')
        


@login_required
def home(request):
    return render(request, 'home.html')
