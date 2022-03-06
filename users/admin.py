from django.contrib import admin
from .models import Staff, UserGroup
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django import forms
from django.utils.translation import gettext, gettext_lazy as _

# admin.site.register(Staff)
# admin.site.register(UserGroup)


class StaffForm(forms.ModelForm):
    # 定义添加或修改的form
    department = forms.ModelChoiceField(queryset=UserGroup.objects.filter(type__lt=2), label="部门")

    class Meta:
        model = Staff
        fields = [
            'user',
            'department',
          ]


class StaffInline(admin.StackedInline):
    # 定义一个inline admin
    model = Staff
    can_delete = False
    form = StaffForm
    # verbose_name_plural = 'staff'


class UserAdmin(BaseUserAdmin):
    # define a new user admin
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = (StaffInline,)


# 重新注册UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class UserGroupInline(admin.StackedInline):
    # 定义一个inline admin
    model = UserGroup
    can_delete = False
    verbose_name_plural = 'UserGroup'


class GroupAdmin(BaseGroupAdmin):
    # define a new group admin
    inlines = (UserGroupInline,)


# 重新注册GroupAdmin
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
