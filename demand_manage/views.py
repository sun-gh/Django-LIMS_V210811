from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import DemandCollect, DemandDesign
from .forms import EditDemandForm, VerifyDemand, EstimateDemandForm, DesignEditForm, DemandSearchForm, DesignSearchForm
from django.core.paginator import Paginator
import json
from datetime import date
from django.http import HttpResponse
from users.models import Staff
# Create your views here.


@login_required()
def demand_page(request, msg):
    # 定义需求管理页
    if request.method == "GET":
        search_form = DemandSearchForm()
        return render(request, "demand_manage/demand_page.html", {'msg': msg, 'form': search_form})


def demand_table(request):
    # 定义需求列表
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        status = int(request.GET.get('status'))
        sponsor = request.GET.get('sponsor')
        demand_describe = request.GET.get('demand_describe')

        conditions = {}  # 构造字典存储查询条件

        if status:
            conditions['status'] = status
        if sponsor:
            conditions['sponsor__contains'] = sponsor
        if demand_describe:
            conditions['demand_describe__contains'] = demand_describe
        all_demands = DemandCollect.objects.filter(**conditions)

        all_demands_count = all_demands.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_demands, limit)  # 开始做分页

        response_data = {'total': all_demands_count, 'rows': []}  # 必须带有rows和total这2个key
        for demand in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            # 定义截图显示
            file = demand.file
            if file:
                file_name = file.name[14:]
            else:
                file_name = ""
            # 定义审核建议
            note_content = demand.note
            if note_content:
                note = note_content
            else:
                note = "-"

            response_data['rows'].append({
                "demand_id": demand.id,
                "demand_number": demand.demand_number,
                "status_code": demand.status,
                "status": demand.get_status_display(),
                "sponsor": demand.sponsor,
                "department": demand.department,
                "create_date": demand.create_time.strftime('%Y-%m-%d'),
                "demand_type": demand.get_demand_type_display(),
                "demand_describe": demand.demand_describe,
                "urgent_degree": demand.urgent_degree,
                "important_degree": demand.important_degree,
                "file_name": file_name,
                "verify_result_code": demand.verify_result,
                "verify_result": demand.get_verify_result_display(),
                "note": note,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def add_demand(request):
    # 定义添加需求功能
    if request.method == 'GET':
        form = EditDemandForm()
        return render(request, 'demand_manage/add_demand.html', {'form': form})
    elif request.method == 'POST':
        demand = DemandCollect()
        form = EditDemandForm(request.POST, request.FILES or None, instance=demand)
        if form.is_valid():

            form.save(commit=False)
            # 定义需求编号
            date_today = date.today()
            demand_today = DemandCollect.objects.filter(create_time__contains=date_today).order_by('-create_time')
            if demand_today:
                serial_num = int(demand_today[0].demand_number) + 1
            else:
                serial_num = date_today.strftime('%Y%m%d') + '01'
            demand.demand_number = serial_num
            # 处理部门
            # username = request.session['nickname']
            # group = Group.objects.filter(user__username=username)
            staff = Staff.objects.get(user=request.user)
            # demand.department = group[0].department.department_name
            demand.department = staff.department.name

            demand.save()
            form.save_m2m()

            msg = "add_success"
            return redirect('demand_manage:demand_page', msg)
        else:
            form = EditDemandForm(request.POST, request.FILES or None)
            msg = "add_failed"
            return render(request, "demand_manage/add_demand.html", {'form': form, 'msg': msg})


@login_required()
def del_demand(request):
    # 定义删除需求函数
    if request.method == 'POST':
        demand_id = request.POST.get("ids")
        demand_id = json.loads(demand_id)
        demand = DemandCollect.objects.filter(id=demand_id)
        demand.delete()

        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


@login_required()
def edit_demand(request, demand_id):
    # 定义需求修改函数
    demand = DemandCollect.objects.get(id=demand_id)
    if request.method == 'POST':
        demand_form = EditDemandForm(request.POST, request.FILES or None, instance=demand)
        if demand_form.is_valid():
            demand_form.save()

            msg = "edit_success"
            return redirect('demand_manage:demand_page', msg)
        else:
            demand_form = EditDemandForm(request.POST, request.FILES or None)
            msg = 'failed'
            return render(request, 'demand_manage/edit_demand.html', {'form': demand_form, 'msg': msg, 'demand': demand})
    elif request.method == 'GET':
        demand_form = EditDemandForm(instance=demand)
        return render(request, 'demand_manage/edit_demand.html', {'form': demand_form, 'demand': demand})


@login_required()
def demand_detail(request, demand_id):
    # 定义需求详情页
    if request.method == 'GET':
        demand = DemandCollect.objects.get(id=demand_id)
        return render(request, 'demand_manage/demand_detail.html', {'demand': demand})


@login_required()
def demand_verify(request, demand_id):
    # 定义需求审核功能
    demand = DemandCollect.objects.get(id=demand_id)
    if request.method == 'POST':
        verify_form = VerifyDemand(request.POST, instance=demand)
        if verify_form.is_valid():
            change_list = verify_form.changed_data
            verify_result = verify_form.cleaned_data.get('verify_result')
            verify_form.save(commit=False)
            if "verify_result" in change_list and verify_result == 4:
                demand.status = 3
            elif "verify_result" in change_list and verify_result != 4:
                demand.status = 2

            demand.save()
            if "verify_result" in change_list and verify_result == 1:
                demand_design = DemandDesign.objects.create(demand=demand)

            msg = "verify_success"
            return redirect('demand_manage:demand_page', msg)
        else:
            verify_form = VerifyDemand(request.POST)
            msg = 'verify_failed'
            return render(request, 'demand_manage/verify_demand.html',
                          {'form': verify_form, 'msg': msg, 'demand': demand})
    elif request.method == 'GET':
        verify_form = VerifyDemand(instance=demand)
        return render(request, 'demand_manage/verify_demand.html', {'form': verify_form, 'demand': demand})


@login_required()
def demand_design_page(request, msg):
    # 定义需求设计页
    if request.method == "GET":
        search_form = DesignSearchForm()
        return render(request, "demand_manage/demand_design_page.html", {'msg': msg, 'form':search_form})


def demand_design_table(request):
    # 定义需求设计列表
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        status = int(request.GET.get('status'))
        sponsor = request.GET.get('sponsor')
        demand_describe = request.GET.get('demand_describe')

        conditions = {}  # 构造字典存储查询条件

        if status:
            conditions['status'] = status
        if sponsor:
            conditions['demand__sponsor__contains'] = sponsor
        if demand_describe:
            conditions['demand__demand_describe__contains'] = demand_describe
        all_design = DemandDesign.objects.filter(**conditions)

        all_design_count = all_design.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_design, limit)  # 开始做分页

        response_data = {'total': all_design_count, 'rows': []}  # 必须带有rows和total这2个key
        for design in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            # 定义评估建议
            note_content = design.note
            if note_content:
                note = note_content
            else:
                note = "-"
            # 定义预计开发周期
            cycle = design.predict_cycle
            if cycle:
                predict_cycle = str(cycle)
            else:
                predict_cycle = "-"
            # 定义开始时间
            start_date = design.start_time
            if start_date:
                start_time = start_date.strftime('%Y-%m-%d')
            else:
                start_time = "-"
            # 定义结束时间
            finish_date = design.finish_time
            if finish_date:
                finish_time = finish_date.strftime('%Y-%m-%d')
            else:
                finish_time = "-"

            response_data['rows'].append({
                "design_id": design.id,
                "demand_number": design.demand.demand_number,
                "status_code": design.status,
                "status": design.get_status_display(),
                "sponsor": design.demand.sponsor,
                "create_date": design.create_time.strftime('%Y-%m-%d'),
                "demand_type": design.demand.get_demand_type_display(),
                "demand_describe": design.demand.demand_describe,
                "urgent_degree": design.demand.urgent_degree,
                "important_degree": design.demand.important_degree,
                "estimate_result_code": design.estimate_result,
                "estimate_result": design.get_estimate_result_display(),
                "note": note,
                "predict_cycle": predict_cycle,
                "start_time": start_time,
                "finish_time": finish_time,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def demand_design_detail(request, design_id):
    # 定义需求设计详情页
    if request.method == 'GET':
        demand_design = DemandDesign.objects.get(id=design_id)
        return render(request, 'demand_manage/demand_design_detail.html', {'design': demand_design})


@login_required()
def demand_design_estimate(request, design_id):
    # 定义需求设计评估
    design = DemandDesign.objects.get(id=design_id)
    if request.method == 'POST':
        estimate_form = EstimateDemandForm(request.POST, instance=design)
        if estimate_form.is_valid():
            change_list = estimate_form.changed_data
            estimate_result = estimate_form.cleaned_data.get('estimate_result')
            estimate_form.save(commit=False)
            if "estimate_result" in change_list and estimate_result == 2:
                design.status = 2
            elif "estimate_result" in change_list and estimate_result != 2:
                design.status = 3

            design.save()

            msg = "estimate_success"
            return redirect('demand_manage:demand_design_page', msg)
        else:
            estimate_form = EstimateDemandForm(request.POST)
            msg = 'estimate_failed'
            return render(request, 'demand_manage/estimate_demand.html',
                          {'form': estimate_form, 'msg': msg, 'design': design})
    elif request.method == 'GET':
        estimate_form = EstimateDemandForm(instance=design)
        return render(request, 'demand_manage/estimate_demand.html', {'form': estimate_form, 'design': design})


@login_required()
def edit_demand_design(request, design_id):
    # 修改需求设计两个时间点
    design = DemandDesign.objects.get(id=design_id)
    if request.method == 'POST':
        old_start_time = design.start_time
        old_finish_time = design.finish_time
        design_form = DesignEditForm(request.POST, instance=design)
        if design_form.is_valid():
            change_list = design_form.changed_data
            design_form.save(commit=False)
            # 设计两个状态的转换（暂未考虑清除时间后状态转换）
            if "start_time" in change_list and not old_start_time:
                design.status = 4
            if "finish_time" in change_list and not old_finish_time:
                design.status = 5
            design.save()

            msg = "edit_success"
            return redirect('demand_manage:demand_design_page', msg)
        else:
            design_form = DesignEditForm(request.POST)
            msg = 'edit_failed'
            return render(request, 'demand_manage/edit_demand_design.html',
                          {'form': design_form, 'msg': msg, 'design': design})
    elif request.method == 'GET':
        design_form = DesignEditForm(instance=design)
        return render(request, 'demand_manage/edit_demand_design.html', {'form': design_form, 'design': design})
