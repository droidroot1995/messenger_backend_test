from django.urls import path
from django.urls import include
from users.views import profile_details, contacts_list, search_users

from users.views import UsersViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UsersViewSet, basename='user') 

urlpatterns = [
    # path('index', index, name='index'),
    path('profile/', profile_details, name='profile_details'),
    path('list', contacts_list, name='contacts_list'),
    path('search_users', search_users, name='search_users'),
] + router.urls