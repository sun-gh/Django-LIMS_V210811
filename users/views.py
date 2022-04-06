from django.shortcuts import render, redirect
from django.contrib import auth
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .forms import PermissionForm
from django.db.models.functions import ExtractMonth, ExtractYear
from project_stage.models import SampleRecord, ProjectType
from django.db.models import Count, Sum
import json
from django.http import HttpResponse

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


@login_required()
def data_show_page(request):
    # 定义数据可视化页面
    if request.method == 'GET':

        return render(request, 'data_show/data_show_page.html')


def project_and_sample_statistics(request):
    # 首先定义项目数量统计函数
    today = date.today()
    last_year = today.year - 1
    last_today = date(last_year, today.month, today.day)
    # 查询近一年的项目
    project_one_year = SampleRecord.objects.filter(receive_date__gte=last_today)
    # 计算项目总数、样本总数
    all_projects = project_one_year.count()
    all_samples = project_one_year.aggregate(sample_amount=Sum('sample_amount'))['sample_amount']
    # 项目统计和样本统计同时注解
    project_statistics = project_one_year.annotate(
        year=ExtractYear('receive_date'), month=ExtractMonth('receive_date')
    ).values('year', 'month').order_by('year', 'month').annotate(project_num=Count('id')).annotate(
        sample_num=Sum('sample_amount'))
    # 将结果保存到列表中
    month_list = []
    project_amount = []
    sample_amount = []
    data = {}
    for month_data in project_statistics:
        month_list.append(str(month_data['year'])+"年"+str(month_data['month'])+"月")
        project_amount.append(month_data['project_num'])
        sample_amount.append(month_data['sample_num'])
    data['all_projects'] = all_projects
    data['all_samples'] = all_samples
    data['month_list'] = month_list
    data['project_amount'] = project_amount
    data['sample_amount'] = sample_amount

    return HttpResponse(json.dumps(data))


def project_type_statistics(request):
    # 按项目类型进行统计
    today = date.today()
    last_year = today.year - 1
    last_today = date(last_year, today.month, today.day)
    project_type_statistics = ProjectType.objects.filter(samplerecord__receive_date__gte=last_today).annotate(
        pro_num=Count('samplerecord')).order_by('-pro_num').values('project_name', 'pro_num')[:10]
    type_list = []
    project_num = []
    data = {}
    for project_type in project_type_statistics:
        type_list.append(project_type['project_name'])
        project_num.append(project_type['pro_num'])
    data['type_list'] = type_list
    data['project_num'] = project_num

    return HttpResponse(json.dumps(data))
