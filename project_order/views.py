from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ProjectOrder, SalePerson, PayType
from project_stage.models import SampleRecord
from contract_manage.models import ProjectContract
from .forms import ProjectOrderForm
from django.core.paginator import Paginator
from django.http import HttpResponse
import json
from django.dispatch import receiver
from project_stage.views import sample_record_add, add_success, sample_record_edit, edit_success
from contract_manage.views import project_contract_add, contract_add_success
from datetime import datetime
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm

# Create your views here.


@receiver(add_success, sender=sample_record_add)
def add_project_order(sender, **kwargs):
    # 使用信号接收器，添加项目订单
    # print(kwargs['sample_rec'])
    sample_record = SampleRecord.objects.get(id=kwargs['sample_rec_id'])
    anti_fake_number = kwargs['anti_fake_number']
    if anti_fake_number:
        project_order = ProjectOrder.objects.create(project_order=sample_record, pay_type="预付单结算")
    else:
        project_order = ProjectOrder.objects.create(project_order=sample_record)

    return project_order


@receiver(edit_success, sender=sample_record_edit)
def edit_project_order(sender, **kwargs):
    # 使用信号接收器，修改项目结算中结算方式
    project_order = ProjectOrder.objects.filter(project_order=kwargs['project_id'])
    anti_fake_number = kwargs['anti_fake_number']
    if anti_fake_number:
        project_order.update(pay_type="预付单结算")
    else:
        project_order.update(pay_type="")

    return project_order


@receiver(contract_add_success, sender=project_contract_add)
def edit_order_record(sender, **kwargs):
    # 使用信号接收器，修改合同记录
    orders = kwargs['project_order']
    for order in orders:
        order.contract_record = True
        order.save()

    return orders


@login_required()
def project_order_page(request, msg="normal_show"):
    # 定义项目结算列表页

    return render(request, 'project_order/project_order.html', {'msg': msg})


def project_order_table(request):
    # 定义项目结算表格数据
    if request.method == 'GET':
        projects_get_perm = get_objects_for_user(request.user, 'project_stage.view_samplerecord')

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        # search = request.GET.get('search')
        project_num = request.GET.get('project_num')
        unit_name = request.GET.get('unit')
        sample_sender = request.GET.get('sample_sender')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        time_item = request.GET.get('time_item')

        conditions = {"projectorder__whether_distribute": True, }  # 构造字典存储查询条件

        if project_num:
            conditions['project_num__contains'] = project_num
        if unit_name:
            conditions['unit__contains'] = unit_name
        if sample_sender:
            conditions['sample_sender__customer_name__contains'] = sample_sender
        if start_time and end_time:
            fmt = '%Y-%m-%d'
            start_time = datetime.strptime(start_time, fmt)
            end_time = datetime.strptime(end_time, fmt)
            if time_item == 'receive_sample':
                conditions['receive_time__range'] = (start_time, end_time)
            elif time_item == 'report_send':
                conditions['date_send_report__range'] = (start_time, end_time)
        all_projects = projects_get_perm.filter(**conditions)
        # all_projects = SampleRecord.objects.filter(**conditions)

        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

        # page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_projects_count, 'rows': []}  # 必须带有rows和total这2个key
        for project in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            if project.project_type:
                project_type = project.project_type.project_name
            else:
                project_type = "-"
            # 定义机时类型为空的情况
            if project.machine_time:
                machine_time = project.machine_time
            else:
                machine_time = "-"
            # 以下为单位和负责人不存在的情况
            unit = project.unit
            if unit:
                unit_name = unit
            else:
                unit_name = "-"
            person = project.terminal
            if person:
                leading_official = person
            else:
                leading_official = "-"

            # addition_item为多对多，显示分多种情况
            all_item = project.addition_item.all()
            if all_item:
                if all_item.count() == 1:
                    addition_item = all_item[0].item_type
                else:
                    addition_item = str(all_item.count()) + "个附加项"
            else:
                addition_item = "-"
            # 定义项目负责人和报告发送日期
            responsible_person = project.responsible_person
            if responsible_person:
                project_responsible_person = responsible_person.name
            else:
                project_responsible_person = "-"
            report_date = project.date_send_report
            if report_date:
                report_send_date = report_date.strftime('%Y-%m-%d')
            else:
                report_send_date = "-"
            # 定义项目结算特有字段（OneToOne反向关联只用模型小写名称）
            customer_source = project.projectorder.customer_source
            if customer_source:
                customer_source_choice = project.projectorder.get_customer_source_display()
            else:
                customer_source_choice = "-"
            project_bill = project.projectorder.project_sum
            if project_bill is not None:
                project_sum = project_bill
            else:
                project_sum = "-"
            saler = project.projectorder.sale_person
            if saler:
                sale_person = saler
            else:
                sale_person = "-"
            pay = project.projectorder.pay_type
            if pay:
                pay_type = pay
            else:
                pay_type = "-"
            note_content = project.projectorder.note
            if note_content:
                note = note_content
            else:
                note = "-"
            record = project.projectorder.contract_record
            if record:
                contract_record = "有"
            else:
                contract_record = "无"

            response_data['rows'].append({
                "project_order_id": project.projectorder.id,
                "project_num": project.project_num,
                "project_type": project_type,
                "sample_type": project.sample_type,
                "machine_time": machine_time,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": project.sample_sender.customer_name,
                "addition_item": addition_item,
                "project_source": project.projectorder.get_project_source_display(),
                "customer_source": customer_source_choice,
                "project_sum": str(project_sum),
                "sale_person": sale_person,
                "pay_type": pay_type,
                "note": note,
                "contract_record": contract_record,
                "responsible_person": project_responsible_person,
                "report_date": report_send_date,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def project_order_detail(request, pro_id):
    # 定义项目结算详情
    project_order = ProjectOrder.objects.get(id=pro_id)

    return render(request, 'project_order/project_order_detail.html', {'order': project_order})


@login_required()
def project_order_edit(request, pro_id):
    # 定义项目结算信息修改
    project_order = ProjectOrder.objects.get(id=pro_id)

    if request.method == 'POST':
        old_sum = project_order.project_sum
        project_order_form = ProjectOrderForm(request.POST, instance=project_order)
        if project_order_form.is_valid():
            change_list = project_order_form.changed_data
            contract_record = project_order.contract_record

            project_order_form.save(commit=False)
            # 定义销售人员修改（因采用领取项目模式后废弃）
            # 定义结算方式修改
            pay_type = project_order_form.cleaned_data.get("pay_type")
            if pay_type:
                project_order.pay_type = pay_type.type_name
            else:
                project_order.pay_type = None
            if "project_sum" in change_list:
                if contract_record:
                    # 修改项目合同金额，及未开票金额
                    new_sum = project_order_form.cleaned_data.get('project_sum')
                    difference = new_sum - old_sum
                    contract = ProjectContract.objects.get(project_order__id=pro_id)
                    old_contract_sum = contract.contract_sum
                    contract.contract_sum = old_contract_sum + difference
                    contract.not_makeout_invoice_sum = old_contract_sum + difference - contract.makeout_invoice_sum
                    contract.save()

            project_order.save()
            project_order_form.save_m2m()

            msg = "edit_success"
            # return render(request, 'project_order/project_order.html', {'msg': msg})
            return redirect('project_order:project_order_page', msg)
        else:
            project_order_form = ProjectOrderForm(request.POST)
            msg = 'failed'
            return render(request, 'project_order/project_order_edit.html', {'form': project_order_form, 'msg': msg,
                                                                             'project_order': project_order})
    elif request.method == 'GET':
        pay_type = project_order.pay_type
        # sale_person = project_order.sale_person

        if pay_type:
            pay_type = PayType.objects.filter(type_name=pay_type)
            project_order_form = ProjectOrderForm(initial={'pay_type': pay_type[0]}, instance=project_order)
        else:
            project_order_form = ProjectOrderForm(instance=project_order)

        return render(request, 'project_order/project_order_edit.html', {'form': project_order_form,
                                                                         'project_order': project_order})


@login_required()
def order_not_distribute_page(request, msg="normal_show"):
    # 定义未分配项目结算列表页

    return render(request, 'project_order/order_not_distribute.html', {'msg': msg})


def order_not_distribute_table(request):
    # 定义未分配项目的表格数据

    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        # search = request.GET.get('search')
        project_num = request.GET.get('project_num')
        unit_name = request.GET.get('unit')
        sample_sender = request.GET.get('sample_sender')

        conditions = {"projectorder__whether_distribute": False, }  # 构造字典存储查询条件

        if project_num:
            conditions['project_num__contains'] = project_num
        if unit_name:
            conditions['unit__contains'] = unit_name
        if sample_sender:
            conditions['sample_sender__customer_name__contains'] = sample_sender
        all_projects = SampleRecord.objects.filter(**conditions)

        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

        # page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_projects_count, 'rows': []}  # 必须带有rows和total这2个key
        for project in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            if project.project_type:
                project_type = project.project_type.project_name
            else:
                project_type = "-"
            # 以下为单位和负责人不存在的情况
            unit = project.unit
            if unit:
                unit_name = unit
            else:
                unit_name = "-"
            person = project.terminal
            if person:
                leading_official = person
            else:
                leading_official = "-"

            response_data['rows'].append({
                "project_order_id": project.projectorder.id,
                "project_num": project.project_num,
                "project_type": project_type,
                "sample_type": project.sample_type,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": project.sample_sender.customer_name,

            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def distribute_project_order(request, pro_id):
    # 定义项目分配
    project_order = ProjectOrder.objects.get(id=pro_id)

    if request.method == 'GET':

        return render(request, 'project_order/distribute_project_order.html', {'project_order': project_order})


@login_required()
def fetch_project_order(request, pro_id):
    # 定义实际项目分配功能
    if request.method == 'GET':
        project_order = ProjectOrder.objects.get(id=pro_id)
        project_order.whether_distribute = True
        project_order.sale_person = request.user.first_name
        project_order.save()
        # 给领取人分配项目对象权限
        assign_perm('project_stage.view_samplerecord', request.user, project_order.project_order)
        msg = "fetch_success"

        return redirect('project_order:order_not_distribute_page', msg)


@login_required()
def untread_project_order(request, pro_id):
    # 定义项目退回功能
    if request.method == 'GET':
        project_order = ProjectOrder.objects.get(id=pro_id)
        project_order.whether_distribute = False
        project_order.sale_person = None
        # 不清空其它信息，以兼容“交接项目”的情况；
        project_order.save()
        # 给归还人解除对象级权限
        remove_perm('project_stage.view_samplerecord', request.user, project_order.project_order)
        msg = "untread_success"

        return redirect('project_order:project_order_page', msg)
