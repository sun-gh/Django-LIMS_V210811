from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ProjectContract, CutPayment
from .forms import AddProjectContractForm, EditProjectContractForm, AdvancepayContractForm, CutPaymentForm
from customer.models import UnitInvoice
# from project_order.models import ProjectOrder
from django.core.paginator import Paginator
from django.http import HttpResponse
import json
from datetime import date
import django.dispatch
from django.db.models import Q

# Create your views here.


@login_required()
def project_contract_page(request):
    # 定义项目合同列表页

    return render(request, 'contract_manage/project_contract.html')


def project_contract_table(request):
    # 定义项目合同表格数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        search = request.GET.get('search')
        # sort_column = request.GET.get('sort')  # which column need to sort
        # order = request.GET.get('order')  # ascending or descending
        if search:  # 判断是否有搜索字
            all_contracts = ProjectContract.objects.filter(Q(contract_type=0), Q(contract_num__contains=search) |
                                                           Q(linkman__contains=search) | Q(unit_name__contains=search))
        else:
            all_contracts = ProjectContract.objects.filter(contract_type=0)

        all_contract_count = all_contracts.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 10  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_contracts, limit)  # 开始做分页

        # page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_contract_count, 'rows': []}  # 必须带有rows和total这2个key
        for contract in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            all_order = contract.project_order.all()
            order_count = all_order.count()
            if order_count == 1:
                project_order = all_order[0].project_order.project_num
                # 定义项目类型
                if all_order[0].project_order.project_type:
                    project_type = all_order[0].project_order.project_type.project_name
                else:
                    project_type = "-"

            elif order_count > 1:
                project_order = str(order_count) + "个项目"
                project_type = "见详细信息"

            else:
                project_order = "-"
            # 定义文件显示
            file = contract.contract_file
            if file:
                file_display = file.name[15:]
            else:
                file_display = ""
            # 要将date对象转化为字符串，才能进行json转换
            back_date = contract.callback_date
            if back_date:
                call_date = back_date.strftime('%Y-%m-%d')
            else:
                call_date = "-"
            # 定义备注
            note_content = contract.note
            if note_content:
                note = note_content
            else:
                note = "-"

            response_data['rows'].append({
                "contract_id": contract.id,
                "contract_num": contract.contract_num,
                "project_order": project_order,
                "project_type": project_type,
                "unit": contract.unit_name,
                "sample_sender": contract.linkman,

                "contract_sum": str(contract.contract_sum),
                "file_display": file_display,
                "call_date": call_date,
                "creator": contract.creator,
                "makeout_invoice_sum": str(contract.makeout_invoice_sum),
                "not_makeout_invoice_sum": str(contract.not_makeout_invoice_sum),
                "payment_sum": str(contract.payment_sum),
                "note": note,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


# 定义一个信号
contract_add_success = django.dispatch.Signal()


@login_required()
def project_contract_add(request):
    # 定义合同添加函数
    if request.method == 'GET':
        form = AddProjectContractForm()
        return render(request, "contract_manage/project_contract_add.html", {'form': form})
    elif request.method == 'POST':
        # 需要赋值字段：合同编号、合同金额、未开票金额
        project_contract = ProjectContract()
        project_contract_form = AddProjectContractForm(request.POST, request.FILES or None, instance=project_contract)
        if project_contract_form.is_valid():
            # change_list = project_contract_form.changed_data
            project_contract_form.save(commit=False)
            # 定义合同号
            date_today = date.today()
            contract_today = ProjectContract.objects.filter(c_time__contains=date_today,
                                                            contract_type=0).order_by('-c_time')
            project_order = project_contract_form.cleaned_data.get('project_order')
            count_order = project_order.count()
            # return HttpResponse("200 ok")
            if contract_today:
                if count_order == 1:
                    contract_num = '1' + str(int(contract_today[0].contract_num) + 1)[1:]
                    contract_sum = project_order[0].project_sum
                    not_makeout_invoice_sum = contract_sum
                else:
                    contract_num = '2' + str(int(contract_today[0].contract_num) + 1)[1:]
                    contract_sum = 0
                    for order in project_order:
                        contract_sum += order.project_sum
                    not_makeout_invoice_sum = contract_sum
            else:
                if count_order == 1:
                    contract_num = '1' + date_today.strftime('%y%m%d') + '01'
                    contract_sum = project_order[0].project_sum
                    not_makeout_invoice_sum = contract_sum
                else:
                    contract_num = '2' + date_today.strftime('%y%m%d') + '01'
                    contract_sum = 0
                    for order in project_order:
                        contract_sum += order.project_sum
                    not_makeout_invoice_sum = contract_sum
            project_contract.contract_num = contract_num
            project_contract.contract_sum = contract_sum
            project_contract.not_makeout_invoice_sum = not_makeout_invoice_sum
            # 定义单位
            unit = project_contract_form.cleaned_data.get('unit')
            if unit:
                project_contract.unit_name = unit.unit_name
            else:
                project_contract.unit_name = project_order[0].project_order.sample_sender.unit.unit_name
            # 定义联系人
            linkman = project_contract_form.cleaned_data.get('linkman')
            if linkman:
                project_contract.linkman = linkman
            else:
                project_contract.linkman = project_order[0].project_order.sample_sender.customer_name

            project_contract.save()
            project_contract_form.save_m2m()  # 使用commit后要手动保存manytomany

            msg = "add_success"
            # 发送一个信号
            contract_add_success.send(project_contract_add, msg=msg, project_order=project_order)

            return render(request, "contract_manage/project_contract.html", {'msg': msg})
        else:
            form = AdvancepayContractForm(request.POST, request.FILES or None)
            msg = "info_error"
            return render(request, "contract_manage/project_contract_add.html", {'form': form, 'msg': msg})


@login_required()
def project_contract_del(request):
    # 定义删除合同功能
    if request.method == 'POST':

        ids = request.POST.get("ids")
        for contract_id in json.loads(ids):
            contract = ProjectContract.objects.get(id=contract_id)
            project_orders = contract.project_order.all()
            # 归还项目结算中合同记录
            for order in project_orders:
                order.contract_record = False
                order.save()

            contract.delete()

        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


@login_required()
def project_contract_edit(request, contract_id):
    # 定义项目合同修改
    contract = ProjectContract.objects.get(id=contract_id)

    if request.method == 'POST':
        contract_form = EditProjectContractForm(request.POST, request.FILES or None, instance=contract)
        if contract_form.is_valid():
            # change_list = contract_form.changed_data
            contract_form.save(commit=False)
            # 保存单位名称
            unit = contract_form.cleaned_data.get('unit')
            contract.unit_name = unit.unit_name
            # 暂定关联项目不能修改（否则要修改合同编号）

            contract.save()
            contract_form.save_m2m()  # 使用commit后要手动保存manytomany

            msg = "edit_success"
            return render(request, 'contract_manage/project_contract.html', {'msg': msg})
        else:
            contract_form = EditProjectContractForm(request.POST, request.FILES or None)

            msg = 'failed'
            return render(request, 'contract_manage/project_contract_edit.html', {'form': contract_form, 'msg': msg,
                                                                                  'contract': contract})
    elif request.method == 'GET':
        unit = UnitInvoice.objects.get(unit_name=contract.unit_name)
        # project_orders = ProjectOrder.objects.filter(Q(projectcontract__id=contract_id) | Q(contract_record=False))
        # # print(project_orders.count())
        # contract_form = ProjectContractForm(initial={'unit': unit}, instance=contract)
        # contract_form.fields['project_order'].queryset = project_orders
        contract_form = EditProjectContractForm(initial={'unit': unit}, instance=contract)

        return render(request, 'contract_manage/project_contract_edit.html', {'form': contract_form,
                                                                              'contract': contract})


@login_required()
def project_contract_detail(request, contract_id):
    # 定义项目合同详情
    contract = ProjectContract.objects.get(id=contract_id)

    return render(request, 'contract_manage/project_contract_detail.html', {'contract': contract})


@login_required()
def advancepay_contract_page(request):
    # 定义预付款合同列表页

    return render(request, 'contract_manage/advancepay_contract.html')


def advancepay_contract_table(request):
    # 定义预付款合同表格数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        search = request.GET.get('search')
        # sort_column = request.GET.get('sort')  # which column need to sort
        # order = request.GET.get('order')  # ascending or descending
        if search:  # 判断是否有搜索字
            all_contracts = ProjectContract.objects.filter(Q(contract_type__gt=0), Q(contract_num__contains=search) |
                                                           Q(linkman__contains=search) | Q(unit_name__contains=search))
        else:
            all_contracts = ProjectContract.objects.filter(contract_type__gt=0)

        all_contract_count = all_contracts.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 10  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_contracts, limit)  # 开始做分页

        # page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_contract_count, 'rows': []}
        for contract in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            # 定义文件显示
            file = contract.contract_file
            if file:
                file_display = file.name[15:]
            else:
                file_display = ""
            # 要将date对象转化为字符串，才能进行json转换
            back_date = contract.callback_date
            if back_date:
                call_date = back_date.strftime('%Y-%m-%d')
            else:
                call_date = "-"
            # 定义备注
            note_content = contract.note
            if note_content:
                note = note_content
            else:
                note = "-"

            response_data['rows'].append({
                "contract_id": contract.id,
                "contract_num": contract.contract_num,
                "unit": contract.unit_name,
                "sample_sender": contract.linkman,
                "contract_sum": str(contract.contract_sum),
                "file_display": file_display,
                "call_date": call_date,
                "creator": contract.creator,
                "makeout_invoice_sum": str(contract.makeout_invoice_sum),
                "not_makeout_invoice_sum": str(contract.not_makeout_invoice_sum),
                # 预付款合同特有字段
                "payment_sum": str(contract.payment_sum),
                "used_sum": str(contract.used_sum),
                "note": note,
            })

        return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def advancepay_contract_add(request):
    # 定义预付款合同添加函数
    if request.method == 'GET':
        form = AdvancepayContractForm()
        return render(request, "contract_manage/advancepay_contract_add.html", {'form': form})
    elif request.method == 'POST':
        # 需要赋值字段：合同编号、单位、未开票金额
        advancepay_contract = ProjectContract()
        advancepay_contract_form = AdvancepayContractForm(request.POST, request.FILES or None,
                                                          instance=advancepay_contract)
        if advancepay_contract_form.is_valid():
            advancepay_contract_form.save(commit=False)
            # 定义合同号
            date_today = date.today()
            contract_today = ProjectContract.objects.filter(c_time__contains=date_today,
                                                            contract_type__gt=0).order_by('-c_time')
            contract_type = advancepay_contract_form.cleaned_data.get('contract_type')
            if contract_today:
                contract_num = str(contract_type+2) + str(int(contract_today[0].contract_num) + 1)[1:]
            else:
                contract_num = str(contract_type+2) + date_today.strftime('%y%m%d') + '01'
            advancepay_contract.contract_num = contract_num
            # 定义单位
            unit = advancepay_contract_form.cleaned_data.get('unit')
            advancepay_contract.unit_name = unit.unit_name
            # 未开票金额
            not_makeout_invoice_sum = advancepay_contract_form.cleaned_data.get('contract_sum')
            advancepay_contract.not_makeout_invoice_sum = not_makeout_invoice_sum

            advancepay_contract.save()
            advancepay_contract_form.save_m2m()  # 使用commit后要手动保存manytomany

            msg = "add_success"
            # 发送一个信号
            # contract_add_success.send(project_contract_add, msg=msg, project_order=project_order)

            return render(request, "contract_manage/advancepay_contract.html", {'msg': msg})
        else:
            form = AdvancepayContractForm(request.POST, request.FILES or None)
            msg = "info_error"
            return render(request, "contract_manage/advancepay_contract_add.html", {'form': form, 'msg': msg})


@login_required()
def advancepay_contract_del(request):
    # 定义删除合同功能
    if request.method == 'POST':

        ids = request.POST.get("ids")
        for contract_id in json.loads(ids):
            contract = ProjectContract.objects.get(id=contract_id)
            contract.delete()

        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


@login_required()
def advancepay_contract_edit(request, contract_id):
    # 定义预付款合同修改
    contract = ProjectContract.objects.get(id=contract_id)

    if request.method == 'POST':
        contract_form = AdvancepayContractForm(request.POST, request.FILES or None, instance=contract)
        if contract_form.is_valid():

            contract_form.save(commit=False)
            unit = contract_form.cleaned_data.get('unit')
            contract.unit_name = unit.unit_name
            contract.save()
            contract_form.save_m2m()  # 使用commit后要手动保存manytomany
            msg = "edit_success"

            return render(request, 'contract_manage/advancepay_contract.html', {'msg': msg})
        else:
            contract_form = AdvancepayContractForm(request.POST, request.FILES or None)
            msg = 'failed'
            return render(request, 'contract_manage/advancepay_contract_edit.html', {'form': contract_form, 'msg': msg,
                                                                                     'contract': contract})
    elif request.method == 'GET':
        unit = UnitInvoice.objects.get(unit_name=contract.unit_name)
        contract_form = AdvancepayContractForm(initial={'unit': unit}, instance=contract)

        return render(request, 'contract_manage/advancepay_contract_edit.html', {'form': contract_form,
                                                                                 'contract': contract})


@login_required()
def advancepay_contract_detail(request, contract_id):
    # 定义预付款合同详情
    contract = ProjectContract.objects.get(id=contract_id)

    return render(request, 'contract_manage/advancepay_contract_detail.html', {'contract': contract})


@login_required()
def cut_payment_info(request):
    # 定义预付款扣款信息页

    return render(request, 'contract_manage/cut_payment_info.html')


@login_required()
def cut_payment_table(request):
    # 定义预付款扣款表格数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        search = request.GET.get('search')
        # sort_column = request.GET.get('sort')  # which column need to sort
        # order = request.GET.get('order')  # ascending or descending
        if search:  # 判断是否有搜索字
            all_apply = CutPayment.objects.filter(Q(link_order__project_order__project_num__contains=search) |
                                                  Q(link_contract__contract_num__contains=search))
        else:
            all_apply = CutPayment.objects.all()

        all_apply_count = all_apply.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 10  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_apply, limit)  # 开始做分页

        # page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_apply_count, 'rows': []}
        for apply in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            # 定义关联合同
            related_contract = apply.link_contract
            contract_num = related_contract.contract_num
            # 要将date对象转化为字符串，才能进行json转换
            cut_date = apply.cut_date
            if cut_date:
                cut_payment_date = cut_date.strftime('%Y-%m-%d')
            else:
                cut_payment_date = "-"
            apply_date = apply.c_time.strftime('%Y-%m-%d')
            # 定义关联项目
            orders = apply.link_order.all()
            order_str = ""
            for order in orders:
                order_str += str(order.project_order.project_num) + " "
            # 定义备注
            note_content = apply.note
            if note_content:
                note = note_content
            else:
                note = "-"

            response_data['rows'].append({
                "apply_id": apply.id,
                "serial_number": apply.serial_number,
                "link_contract": contract_num,
                "unused_sum": str(apply.surplus_sum),
                "cut_sum": str(apply.cut_sum),
                "cut_date": cut_payment_date,
                "applicant": apply.applicant,
                "apply_date": apply_date,
                "link_order": order_str,
                "note": note,
                "status": apply.status,
            })

        return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def apply_cut_payment(request):
    # 申请扣款
    if request.method == 'GET':

        apply_form = CutPaymentForm()
        return render(request, 'contract_manage/apply_cut_payment.html', {'form': apply_form})
    elif request.method == 'POST':
        apply_instance = CutPayment()
        apply_form = CutPaymentForm(request.POST, instance=apply_instance)
        if apply_form.is_valid():

            apply_form.save(commit=False)
            # 定义申请序号
            date_today = date.today()
            apply_today = CutPayment.objects.filter(c_time__contains=date_today).order_by('-c_time')
            if apply_today:
                serial_num = int(apply_today[0].serial_number) + 1
            else:
                serial_num = date_today.strftime('%Y%m%d') + '01'
            apply_instance.serial_number = serial_num
            # 定义剩余金额
            link_contract = apply_form.cleaned_data.get('link_contract')
            apply_instance.surplus_sum = link_contract.payment_sum - link_contract.used_sum

            apply_instance.save()
            apply_form.save_m2m()

            msg = "add_success"
            # 发送一个信号
            # add_success.send(sample_record_add, msg=msg, sample_rec_id=sample_rec.id)

            return render(request, "contract_manage/cut_payment_info.html", {'msg': msg})
        else:
            form = CutPaymentForm(request.POST)
            msg = "info_error"
            return render(request, "contract_manage/apply_cut_payment.html", {'form': form, 'msg': msg})


@login_required()
def cut_payment_edit(request, apply_id):
    # 修改预付款扣款申请
    apply_info = CutPayment.objects.get(id=apply_id)

    if request.method == 'POST':
        apply_form = CutPaymentForm(request.POST, instance=apply_info)
        if apply_form.is_valid():
            change_list = apply_form.changed_data
            apply_form.save(commit=False)
            if "link_contract" in change_list:
                # 定义修改剩余金额
                link_contract = apply_form.cleaned_data.get('link_contract')
                apply_info.surplus_sum = link_contract.payment_sum - link_contract.used_sum
            # 修改状态
            apply_info.status = 0
            apply_info.save()
            apply_form.save_m2m()  # 使用commit后要手动保存manytomany

            msg = "edit_success"
            return render(request, 'contract_manage/cut_payment_info.html', {'msg': msg})
        else:
            apply_form = CutPaymentForm(request.POST)
            msg = 'failed'
            return render(request, 'contract_manage/edit_cut_payment.html', {'form': apply_form, 'msg': msg,
                                                                             'apply_info': apply_info})
    elif request.method == 'GET':
        apply_form = CutPaymentForm(instance=apply_info)
        return render(request, 'contract_manage/edit_cut_payment.html', {'form': apply_form, 'apply_info': apply_info})


@login_required()
def cut_payment_detail(request, apply_id):
    # 定义预付款扣款详情

    apply_detail = CutPayment.objects.get(id=apply_id)

    return render(request, 'contract_manage/cut_payment_detail.html', {'apply_detail': apply_detail})


@login_required()
def cut_payment_del(request):
    # 定义预付款扣款申请删除
    if request.method == 'POST':

        apply_id = request.POST.get("ids")
        apply = CutPayment.objects.get(id=apply_id)
        apply.delete()

        return HttpResponse("del_success")
    return HttpResponse("非POST请求！")


@login_required()
def approve_cut_payment(request, apply_id):
    # 审批扣款申请
    apply_detail = CutPayment.objects.get(id=apply_id)

    link_contract = apply_detail.link_contract

    # 修改发票对应合同的使用
    contract_sum = link_contract.contract_sum
    old_used_sum = link_contract.used_sum
    link_contract.used_sum = old_used_sum + apply_detail.cut_sum
    # link_contract.unused_sum = contract_sum - old_used_sum - apply_detail.cut_sum
    link_contract.save()

    # 修改作废申请状态及扣款日期
    date_today = date.today()
    apply_detail.status = 2
    apply_detail.cut_date = date_today
    apply_detail.save()
    msg = "approve_success"
    return render(request, 'contract_manage/cut_payment_info.html', {'msg': msg})


@login_required()
def untread_cut_payment(request, apply_id):
    # 退回扣款申请
    apply_obj = CutPayment.objects.get(id=apply_id)
    status_val = apply_obj.status
    if status_val == 2:
        # 修改合同使用金额、剩余金额及申请状态
        link_contract = apply_obj.link_contract

        link_contract.used_sum -= apply_obj.cut_sum
        # link_contract.unused_sum += apply_obj.cut_sum
        link_contract.save()

        apply_obj.status = 1
        apply_obj.cut_date = None
        apply_obj.save()
    else:
        # 修改作废申请状态
        apply_obj.status = 1
        apply_obj.save()

    msg = "untread_success"
    return render(request, 'contract_manage/cut_payment_info.html', {'msg': msg})

