from django.contrib import admin
from .models import User, UserConfirmation

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'phone_number']

admin.site.register(UserConfirmation)