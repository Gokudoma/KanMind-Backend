from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the CustomUser model.
    Extends the default UserAdmin to include the 'fullname' field.
    """
    model = CustomUser
    list_display = ['email', 'username', 'fullname', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('fullname',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('fullname',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)