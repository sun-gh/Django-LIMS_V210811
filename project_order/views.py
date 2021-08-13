from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ProjectOrder
from project_stage.models import SampleRecord
from contract_manage.models import ProjectContract
from .forms import ProjectOrderForm
from django.core.paginator import Paginator
from django.http import HttpResponse
import json
from django.dispatch import receiver
from project_stage.views import sample_record_add, add_success
from contract_manage.views import project_contract_add, contract_add_success
from django.db.models import Q

# Create your views here.


@receiver(add_success, sender=sample_record_add)
def add_project_order(sender, **kwargs):

    # 使用信号接收器，添加项目订单
    # print(kwargs['sample_rec'])
    sample_record = SampleRecord.objects.get(id=kwargs['sample_rec_id'])
    project_order = ProjectOrder.objects.create(project_order=sample_record)

    return project_order


@receiver(contract_add_success, sender=project_contract_add)
def edit_order_record(sender, **kwargs):

    # 使用信号接收器，修改合同记录
    # print(kwargs['msg'])
    orders = kwargs['project_order']
    for order in orders:
        order.contract_record = True
        order.save()

    return orders


@login_required()
def project_order_page(request):
    # 定义项目结算列表页

    return render(request, 'project_order/project_order.html')


def project_order_table(request):
    # 定义项目结算表格数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        search = request.GET.get('search')
        # sort_column = request.GET.get('sort')  # which column need to sort
        # order = request.GET.get('order')  # ascending or descending
        if search:  # 判断是否有搜索字
            all_projects = SampleRecord.objects.filter(Q(project_num=search) | Q(sample_sender__customer_name=search) |
                                                       Q(sample_sender__unit__unit_name__contains=search))
        else:
            all_projects = SampleRecord.objects.all()

        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 10  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

        # page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_projects_count, 'rows': []}  # 必须带有rows和total这2个key
        for project in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            if project.project_type:
                project_type = project.project_type.project_name
            else:
                project_type = "-"
            if project.sample_type:
                sample_type = project.sample_type.type_name
            else:
                sample_type = "-"
            if project.machine_time:
                machine_time = project.machine_time.time_type
            else:
                machine_time = "-"
            # 以下为送样人信息
            if project.sample_sender:
                sample_sender = project.sample_sender.customer_name
                unit = project.sample_sender.unit
                if unit:
                    unit_name = unit.unit_name
                else:
                    unit_name = "-"
                person = project.sample_sender.leading_official
                if person:
                    leading_official = person
                else:
                    leading_official = "-"
            else:
                sample_sender = "-"
                unit_name = "-"
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
            # 定义项目结算特有字段（OneToOne反向关联只用模型小写名称）
            project_bill = project.projectorder.project_sum
            if project_bill:
                project_sum = project_bill
            else:
                project_sum = "-"
            saler = project.projectorder.sale_person
            if saler:
                sale_person = saler.name_person
            else:
                sale_person = "-"
            pay = project.projectorder.pay_type
            if pay:
                pay_type = pay.type_name
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
                "sample_type": sample_type,
                "machine_time": machine_time,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": sample_sender,
                "addition_item": addition_item,
                "project_sum": project_sum,
                "sale_person": sale_person,
                "pay_type": pay_type,
                "note": note,
                "contract_record": contract_record,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def project_order_detail(request, pro_id):
    # 定义项目结算详情
    project_order = ProjectOrder.objects.get(id=pro_id)

    return render(request, 'project_order/project_order_detail.html', {'record': project_order})


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
            return render(request, 'project_order/project_order.html', {'msg': msg})
        else:
            project_order_form = ProjectOrderForm(request.POST)
            msg = 'failed'
            return render(request, 'project_order/project_order_edit.html', {'form': project_order_form, 'msg': msg,
                                                                             'project_order': project_order})
    elif request.method == 'GET':
        project_order_form = ProjectOrderForm(instance=project_order)
        return render(request, 'project_order/project_order_edit.html', {'form': project_order_form,
                                                                         'project_order': project_order})
