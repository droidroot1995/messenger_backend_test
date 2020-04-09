from django.contrib import admin
from users.models import User
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display=('username',)

admin.site.register(User, UserAdmin)
