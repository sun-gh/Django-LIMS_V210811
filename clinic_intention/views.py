from django.shortcuts import render, redirect
from .models import ClinicIntention, FollowUpRecord
from .forms import IntentionForm, FollowUpRecordForm, IntentionSearchForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
from datetime import date
from guardian.shortcuts import get_objects_for_user, assign_perm
import django.dispatch
from django.dispatch import receiver
# from django.core import serializers

# Create your views here.


@login_required()
def intention_page(request, msg="normal_show"):
    # 定义临床意向页
    search_from = IntentionSearchForm()

    return render(request, 'clinic_intention/intention_page.html', {'form': search_from, 'msg': msg})


def intention_table(request):
    # 定义临床意向表格
    if request.method == 'GET':
        intention_get_perm = get_objects_for_user(request.user, 'clinic_intention.view_clinicintention')

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        customer_name = request.GET.get('customer_name')
        unit = request.GET.get('unit')
        project_stage = int(request.GET.get('project_stage'))
        plan_type = int(request.GET.get('plan_type'))
        plan_needed = request.GET.get("plan_needed")

        conditions = {}  # 构造字典存储查询条件
        if customer_name:
            conditions['customer_name__contains'] = customer_name
        if unit:
            conditions['unit__unit_name__contains'] = unit
        if project_stage:
            conditions['project_stage'] = project_stage
        if plan_type:
            conditions['plan_type'] = plan_type
        if plan_needed != 'unknown':
            conditions['plan_needed'] = plan_needed.title()

        # all_intention = ClinicIntention.objects.filter(**conditions)
        all_intention = intention_get_perm.filter(**conditions)
        all_intention_count = all_intention.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_intention, limit)  # 开始做分页

        response_data = {'total': all_intention_count, 'rows': []}  # 必须带有rows和total这2个key
        for intention in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            # 定义联系方式
            contact_info = intention.contact_info
            if contact_info:
                contact_info = contact_info
            else:
                contact_info = "-"
            # 定义科室
            department = intention.department
            if department:
                department = department
            else:
                department = "-"
            # 定义负责人
            leading_official = intention.leading_official
            if leading_official:
                leading_official = leading_official
            else:
                leading_official = "-"
            # 定义疾病种类
            disease_type = intention.disease_type
            if disease_type:
                disease_type = disease_type
            else:
                disease_type = "-"
            # 定义方案类型
            plan_type = intention.plan_type
            if plan_type:
                plan_type = intention.get_plan_type_display()
            else:
                plan_type = "-"
            # 要将date对象转化为字符串，才能进行json转换
            plan_deadline = intention.plan_deadline
            if plan_deadline:
                plan_deadline = plan_deadline.strftime('%Y-%m-%d')
            else:
                plan_deadline = "-"
            # 定义客户预算
            customer_budget = intention.customer_budget
            if customer_budget:
                customer_budget = str(customer_budget)   # decimal类型不能直接转换为json
            else:
                customer_budget = "-"
            # 定义计划样本数
            sample_number = intention.sample_number
            if sample_number:
                sample_number = sample_number
            else:
                sample_number = "-"
            # 计划收样日期
            collect_time = intention.collect_time
            if collect_time:
                collect_time = collect_time.strftime('%Y-%m-%d')
            else:
                collect_time = "-"
            # 计划送样日期
            send_time = intention.send_time
            if send_time:
                send_time = send_time.strftime('%Y-%m-%d')
            else:
                send_time = "-"
            # 样本类型
            sample_type = intention.sample_type
            if sample_type:
                sample_type = sample_type.type_name
            else:
                sample_type = "-"
            # 项目阶段
            project_stage = intention.project_stage
            if project_stage:
                project_stage = intention.get_project_stage_display()
            else:
                project_stage = "-"
            # 需求预估
            demand_estimate = intention.demand_estimate.all()
            if demand_estimate:
                if demand_estimate.count() == 1:
                    demand_estimate = demand_estimate[0].type_name
                else:
                    demand_estimate = demand_estimate.count()
            else:
                demand_estimate = "-"

            response_data['rows'].append({
                "intention_id": intention.id,
                "intention_number": intention.intention_number,
                "customer_name": intention.customer_name,
                "contact_info": contact_info,
                "unit": intention.unit.unit_name,
                "department": department,
                "leading_official": leading_official,
                "disease_type": disease_type,
                "plan_needed": intention.plan_needed,
                "plan_type": plan_type,
                "plan_deadline": plan_deadline,
                "customer_budget": customer_budget,
                "sample_number": sample_number,
                "collect_time": collect_time,
                "send_time": send_time,
                "sample_type": sample_type,
                "project_stage": project_stage,
                "demand_estimate": demand_estimate,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


add_intention_success = django.dispatch.Signal()


@login_required()
def add_intention(request):
    # 定义意向添加功能
    if request.method == 'GET':

        intention_form = IntentionForm()
        return render(request, 'clinic_intention/add_intention.html', {'form': intention_form})
    elif request.method == 'POST':
        intention_instance = ClinicIntention()
        intention_form = IntentionForm(request.POST, instance=intention_instance)
        if intention_form.is_valid():

            intention_form.save(commit=False)
            # 定义意向编号
            date_today = date.today()
            intention_today = ClinicIntention.objects.filter(c_time__contains=date_today).order_by('-c_time')
            if intention_today:
                serial_num = int(intention_today[0].intention_number) + 1
            else:
                serial_num = date_today.strftime('%Y%m%d') + '01'
            intention_instance.intention_number = serial_num

            intention_instance.save()
            intention_form.save_m2m()

            msg = "add_success"
            # 处理对象权限
            add_intention_success.send(add_intention, msg=msg, intention_obj=intention_instance, user=request.user)

            return redirect('clinic_intention:intention_page', msg)
        else:
            form = IntentionForm(request.POST)
            msg = "add_failed"
            return render(request, "clinic_intention/add_intention.html", {'form': form, 'msg': msg})


@receiver(add_intention_success, sender=add_intention)
def assign_intention_perm(sender, **kwargs):
    # 定义意向对象权限添加
    assign_perm('clinic_intention.view_clinicintention', kwargs['user'], kwargs['intention_obj'])

    return None


@login_required()
def del_intention(request):
    # 定义删除意向函数
    if request.method == 'POST':

        intention_id = request.POST.get("intention_id")
        intention_id = json.loads(intention_id)
        intention = ClinicIntention.objects.filter(id=intention_id)
        intention.delete()

        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


@login_required()
def edit_intention(request, intention_id):
    # 定义意向信息编辑页面
    intention_info = ClinicIntention.objects.get(id=intention_id)

    if request.method == 'POST':

        intention_form = IntentionForm(request.POST, instance=intention_info)
        if intention_form.is_valid():

            intention_form.save()

            msg = "edit_success"
            # return render(request, 'clinic_intention/intention_page.html', {'msg': msg})
            return redirect('clinic_intention:intention_page', msg)
        else:
            intention_form = IntentionForm(request.POST)
            msg = 'edit_failed'
            return render(request, 'clinic_intention/edit_intention.html', {'form': intention_form, 'msg': msg,
                                                                            'intention_info': intention_info})
    elif request.method == 'GET':
        intention_form = IntentionForm(instance=intention_info)
        return render(request, 'clinic_intention/edit_intention.html', {'form': intention_form,
                                                                        'intention_info': intention_info})


@login_required()
def intention_detail(request, intention_id):
    # 定义意向详情页
    followup_record_form = FollowUpRecordForm()
    intention = ClinicIntention.objects.get(id=intention_id)

    return render(request, 'clinic_intention/intention_detail.html', {'intention': intention,
                                                                      'form': followup_record_form})


def add_followup_record(request):
    if request.method == "POST":
        intention_id = request.POST.get("intention_id")
        followup_record = FollowUpRecord()
        followup_record_form = FollowUpRecordForm(request.POST, instance=followup_record)
        if followup_record_form.is_valid():
            followup_record_form.save()
            intention = ClinicIntention.objects.get(id=intention_id)
            intention.followup_record.add(followup_record)
            # last_followup = serializers.serialize("json", intention.followup_record.all())
            last_followup = {}
            create_time = followup_record.c_time.strftime('%Y.%m.%d %H:%M')
            communicate_time = followup_record.communicate_time.strftime('%Y.%m.%d')
            last_followup['create_time'] = create_time
            last_followup['communicate_time'] = communicate_time
            last_followup['linkman'] = followup_record.linkman
            last_followup['communicate_content'] = followup_record.communicate_content
            last_followup['recorder'] = followup_record.recorder

            return HttpResponse(json.dumps(last_followup))
