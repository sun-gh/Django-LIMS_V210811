from django.shortcuts import render, redirect
from django.contrib import auth
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .forms import PermissionForm
from django.db.models.functions import ExtractMonth, ExtractYear
from project_stage.models import SampleRecord, ProjectType, SampleType
from django.db.models import Count, Sum, F
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


def get_today_last_year():
    # 定义去年的今天日期获取函数
    today = date.today()
    last_year = today.year - 1
    today_last_year = date(last_year, today.month, today.day)

    return today_last_year


def project_and_sample_statistics(request):
    # 项目数量和样本数量按月份统计函数
    last_today = get_today_last_year()
    # 查询近一年的项目
    project_one_year = SampleRecord.objects.filter(receive_time__gte=last_today)
    # 计算项目总数、样本总数
    all_projects = project_one_year.count()
    all_samples = project_one_year.aggregate(sample_amount=Sum('sample_amount'))['sample_amount']
    # 项目统计和样本统计同时注解
    project_statistics = project_one_year.annotate(
        year=ExtractYear('receive_time'), month=ExtractMonth('receive_time')
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
    # 项目类型统计
    last_today = get_today_last_year()
    project_type_statistics = ProjectType.objects.filter(samplerecord__receive_time__gte=last_today).annotate(
        pro_num=Count('samplerecord')).annotate(sample_num=Sum('samplerecord__sample_amount'))
    # 项目数量进行TOP9和剩余部分计算
    project_type_order = project_type_statistics.order_by('-pro_num').values('project_name', 'pro_num')
    project_type_top9 = project_type_order[:9]
    project_type_remain = project_type_order[9:].aggregate(pro_sum=Sum('pro_num'))
    type_list_by_project = []
    project_num = []
    for project_type in project_type_top9:
        type_list_by_project.append(project_type['project_name'])
        project_num.append(project_type['pro_num'])
    type_list_by_project.append("其它")
    project_num.append(project_type_remain['pro_sum'])
    # 样本数量进行TOP9和剩余部分计算
    project_type_order = project_type_statistics.order_by('-sample_num').values('project_name', 'sample_num')
    project_type_top9 = project_type_order[:9]
    project_type_remain = project_type_order[9:].aggregate(sample_sum=Sum('sample_num'))
    type_list_by_sample = []
    sample_num = []
    for project_type in project_type_top9:
        type_list_by_sample.append(project_type['project_name'])
        sample_num.append(project_type['sample_num'])
    type_list_by_sample.append("其它")
    sample_num.append(project_type_remain['sample_sum'])
    # 将结果数据打包
    data = {}
    data['type_list_by_project'] = type_list_by_project
    data['project_num'] = project_num
    data['type_list_by_sample'] = type_list_by_sample
    data['sample_num'] = sample_num

    return HttpResponse(json.dumps(data))


def sample_type_statistics(request):
    # 样本类型统计
    last_today = get_today_last_year()
    sample_type_statistics = SampleRecord.objects.filter(receive_time__gte=last_today).values('sample_type')\
        .order_by('sample_type').annotate(pro_num=Count('id')).annotate(sample_sum=Sum('sample_amount'))
    # 项目数量进行TOP9和剩余部分计算
    sample_type_order = sample_type_statistics.order_by('-pro_num')
    sample_type_top9 = sample_type_order[:9]
    sample_type_remain = sample_type_order[9:].aggregate(pro_sum=Sum('pro_num'))
    type_list_by_project = []
    project_num = []
    for sample_type in sample_type_top9:
        type_list_by_project.append(sample_type['sample_type'])
        project_num.append(sample_type['pro_num'])
    type_list_by_project.append("其它")
    project_num.append(sample_type_remain['pro_sum'])
    # 样本数量进行TOP9和剩余部分计算
    sample_type_order = sample_type_statistics.order_by('-sample_sum')
    sample_type_top9 = sample_type_order[:9]
    sample_type_remain = sample_type_order[9:].aggregate(sample_count=Sum('sample_sum'))
    type_list_by_sample = []
    sample_num = []
    for sample_type in sample_type_top9:
        type_list_by_sample.append(sample_type['sample_type'])
        sample_num.append(sample_type['sample_sum'])
    type_list_by_sample.append("其它")
    sample_num.append(sample_type_remain['sample_count'])
    data = {}
    data['type_list_by_project'] = type_list_by_project
    data['project_num'] = project_num
    data['type_list_by_sample'] = type_list_by_sample
    data['sample_num'] = sample_num

    return HttpResponse(json.dumps(data))


def total_delay_rate(request):
    # 总体延期率统计(超期分为两种情况：1、实际日期大于截止日期；2、实际日期为空，但当前日期已大于截止日期；)
    current_time = datetime.now()
    data = []
    project_started = SampleRecord.objects.filter(pro_start_date__isnull=False)
    # 前处理阶段计算
    pretreat_finished = project_started.filter(pretreat_finish_date__isnull=False)
    pretreat_finish_delay = pretreat_finished.filter(pretreat_finish_date__gt=F('pretreat_deadline'))
    pretreat_not_finish_delay = project_started.filter(pretreat_finish_date__isnull=True, pretreat_deadline__lt=current_time)
    pretreat_projects = pretreat_finished.count() + pretreat_not_finish_delay.count()
    pretreat_delay = pretreat_finish_delay.count() + pretreat_not_finish_delay.count()
    row1 = {'stage': "前处理阶段", 'projects': pretreat_projects, 'delay': pretreat_delay}
    data.append(row1)
    # 质谱检测阶段计算
    test_finished = project_started.filter(test_finish_date__isnull=False)
    test_finish_delay = test_finished.filter(test_finish_date__gt=F('test_deadline'))
    test_not_finish_delay = project_started.filter(test_finish_date__isnull=True, test_deadline__lt=current_time)
    test_projects = test_finished.count() + test_not_finish_delay.count()
    test_delay = test_finish_delay.count() + test_not_finish_delay.count()
    row2 = {'stage': "质谱检测阶段", 'projects': test_projects, 'delay': test_delay}
    data.append(row2)
    # 数据分析阶段
    analysis_finished = project_started.filter(date_send_report__isnull=False)
    analysis_finish_delay = analysis_finished.filter(date_send_report__gt=F('pro_deadline'))
    analysis_not_finish_delay = project_started.filter(date_send_report__isnull=True, pro_deadline__lt=current_time)
    analysis_projects = analysis_finished.count() + analysis_not_finish_delay.count()
    analysis_delay = analysis_finish_delay.count() + analysis_not_finish_delay.count()
    row3 = {'stage': "数据分析阶段", 'projects': analysis_projects, 'delay': analysis_delay}
    data.append(row3)

    return HttpResponse(json.dumps(data))
