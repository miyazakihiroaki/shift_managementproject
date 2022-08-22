from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from accounts.models import Userr
from accounts.forms import UserCreationForm


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'clerkname',
                'email',
                'password',
                'personalimage',
                'introduction_text',
                'admin_only_text',
                'category',
            )
        }),
        (None, {
            'fields': (
                'is_active',
                'is_admin',
            )
        })
    )
    
    list_display = ('clerkname','email', 'is_active')
    list_filter = ()
    ordering = ()
    filter_horizontal = ()
    
    add_fieldsets = (
        (None, {
            'fields': ('clerkname','email', 'personalimage','password',),
        }),
    )
    
    add_form = UserCreationForm
    
admin.site.unregister(Group)
admin.site.register(Userr, CustomUserAdmin)
    



