from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .forms import PermissionForm


# Create your views here.


def login(request):
    if request.method == "GET":
        return render(request, "users/login.html")
    else:
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        user_obj = auth.authenticate(username=username, password=password)
    if not user_obj:
        message = "error"

        return render(request, "users/login.html", {'message': message})
    else:
        request.session['is_login'] = True  # session是request自带属性，其中的键值对可任意设置
        request.session['user_name'] = user_obj.first_name
        request.session['nickname'] = user_obj.username

        auth.login(request, user_obj)
        return render(request, 'customer/index.html')


@login_required()   # 如果未登录，也就没有登出一说
def logout(request):

    auth.logout(request)  # 会自动清除session
    return redirect('/user/login/')


def change_pwd(request):
    # 定义密码修改
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            # messages.success(request, 'Your password was successfully updated!')
            return render(request, 'account/password_change_done.html')
        else:
            # messages.error(request, 'Please correct the error below.')
            msg = "error"
            return render(request, 'account/password_change_form.html', {'form': form, 'msg': msg})
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'account/password_change_form.html', {'form': form})


def add_permission(request):
    # 定义权限添加
    if request.method == 'GET':
        per_form = PermissionForm()
        return render(request, 'users/add_permission.html', {'form': per_form})
    elif request.method == 'POST':
        per_form = PermissionForm(request.POST)
        if per_form.is_valid():
            type_obj = per_form.cleaned_data.get("model_name")  # 获取某个model的contenttype实例
            content_type = ContentType.objects.get_for_model(type_obj.model_class())  # 再转换为模型类
            permission = Permission.objects.create(
                codename=per_form.cleaned_data.get('permission_name'),   # 'can_publish'
                name=per_form.cleaned_data.get('permission_describe'),  # 'Can Publish Posts'
                content_type=content_type,
            )
            msg = "add_success"
            return render(request, 'users/test.html', {'msg': msg})
        else:
            per_form = PermissionForm()
            msg = "add_failed"
            return render(request, 'users/add_permission.html', {'form': per_form, 'msg': msg})
