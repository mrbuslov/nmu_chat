from django.contrib import admin
from account.models import Account
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import redirect
from django.http.response import HttpResponseRedirect

class HidePassword(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Account
        fields = ('password',)


class AccountAdmin(UserAdmin): 
    form = HidePassword # скрываем пароль

    list_display = ('email', 'username')
    search_fields = ('email','username')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('image', 'username', 'phone_number', 'first_name', 'last_name', 'date_joined','last_login', 'online', 'last_online', 'left_handed')}),
        ('Разрешения', {'fields': ('is_admin','is_active', 'is_blocked', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)}),
    )
    
    # если захотим добавить аккаунт со страницы admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password',),
        }),
    )

    readonly_fields = ('date_joined','last_login', 'last_online')

    class Meta:
        model = Account

admin.site.register(Account, AccountAdmin)
from django.contrib.auth.models import Group
admin.site.unregister(Group)