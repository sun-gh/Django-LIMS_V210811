from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models.functions import ExtractMonth, ExtractYear
from project_stage.models import SampleRecord, ProjectType, SampleType
from django.db.models import Count, Sum, F, Q
import json
from django.http import HttpResponse
from datetime import date, datetime


@login_required()
def total_data_page(request):
    # 定义数据可视化页面
    if request.method == 'GET':

        return render(request, 'data_visual/total_data_page.html')


def get_today_last_year():
    # 定义去年的今天日期获取函数
    today = date.today()
    today_last_year = today.replace(year=today.year-1)

    return today_last_year


def project_and_sample_statistics(request):
    # 项目数量和样本数量按月份统计函数
    last_today = get_today_last_year()
    # 查询近一年的项目
    project_one_year = SampleRecord.objects.filter(receive_time__gt=last_today)
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
    fmt = '%Y-%m-%d'
    start_time = datetime.strptime(request.POST.get('start_time'), fmt)
    end_time = datetime.strptime(request.POST.get('end_time'), fmt)
    project_type_statistics = ProjectType.objects.filter(samplerecord__receive_time__range=(start_time, end_time)).annotate(
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
    fmt = '%Y-%m-%d'
    start_time = datetime.strptime(request.POST.get('start_time'), fmt)
    end_time = datetime.strptime(request.POST.get('end_time'), fmt)
    sample_type_statistics = SampleRecord.objects.filter(receive_time__range=(start_time, end_time)).values('sample_type')\
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


def delay_rate_page(request):
    # 定义延期率页面
    if request.method == 'GET':
        return render(request, 'data_visual/delay_rate_page.html')


def total_delay_rate(request):
    # 总体延期率统计(超期判断标准：1、当前阶段已完成项目；2、实际日期大于截止日期；)
    current_time = datetime.now()
    data = {}
    date_now = current_time.date()
    last_year = date_now.replace(year=date_now.year-1)
    project_received = SampleRecord.objects.filter(receive_time__gt=last_year)
    # 前处理阶段计算
    pretreat_data = project_received.filter(project_type__pre_process_cycle__isnull=False,
                                            pretreat_finish_date__isnull=False).annotate(
        year=ExtractYear('pretreat_finish_date'), month=ExtractMonth('pretreat_finish_date')).\
        values('year', 'month').order_by('year', 'month').annotate(
        finish_count=Count('id'), delay_count=Count('id', filter=Q(pretreat_finish_date__gt=F('pretreat_deadline'))))
    pretreat_month = []
    pretreat_delay_rate = []
    pretreat_delay_count = []
    for data_per_month in pretreat_data:
        pretreat_month.append(str(data_per_month['year'])+"年"+str(data_per_month['month'])+"月")
        delay_rate = round(data_per_month['delay_count'] * 100 / data_per_month['finish_count'], 1)
        pretreat_delay_rate.append(delay_rate)
        pretreat_delay_count.append(data_per_month['delay_count'])
    # print(pretreat_month, pretreat_delay_rate)
    data['pretreat_month'] = pretreat_month
    data['pretreat_delay_rate'] = pretreat_delay_rate
    data['pretreat_delay_count'] = pretreat_delay_count
    # 质谱检测阶段计算

    # 数据分析阶段

    return HttpResponse(json.dumps(data))