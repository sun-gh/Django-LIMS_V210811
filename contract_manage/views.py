from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ProjectContract, CutPayment, ContractAlter
from project_order.models import ProjectOrder
from .forms import (AddProjectContractForm, EditProjectContractForm, AdvancepayContractForm, CutPaymentForm,
                    AdvancePayContractAlterForm, ProjectContractAlterForm)
from customer.models import UnitInvoice
from django.core.paginator import Paginator
from django.http import HttpResponse
import json
from datetime import date
import django.dispatch
from django.dispatch import receiver
from invoice_manage.views import (apply_invoice, apply_invoice_success, approve_apply_invoice,
                                  approve_apply_invoice_success, apply_invoice_del, apply_invoice_del_success,
                                  untread_apply_invoice, untread_apply_invoice_success)
from django.db.models import Q, Sum

# Create your views here.


@receiver(apply_invoice_success, sender=apply_invoice)
def contract_status_to_used(sender, **kwargs):
    # 定义开票申请添加后对应合同状态更改
    related_contract = kwargs['related_contract']
    apply_invoice_related = related_contract.applyinvoice_set.all()
    if apply_invoice_related.count() == 1:
        related_contract.status = 1
        related_contract.save()

    return related_contract


@receiver(apply_invoice_del_success, sender=apply_invoice_del)
def contract_status_to_unused(sender, **kwargs):
    # 定义删除开票申请后修改对应合同状态
    related_contract = kwargs['related_contract']
    apply_invoice_related = related_contract.applyinvoice_set.all()
    if apply_invoice_related.count() == 0:
        related_contract.status = 0
        related_contract.save()

    return related_contract


@receiver(approve_apply_invoice_success, sender=approve_apply_invoice)
def contract_status_to_effect(sender, **kwargs):
    # 定义审批开票申请成功后对应合同状态更改
    related_contract = kwargs['related_contract']
    apply_invoice_related = related_contract.applyinvoice_set.all()
    if apply_invoice_related.count() == 1:
        related_contract.status = 2
        related_contract.save()

    return related_contract


@receiver(untread_apply_invoice_success, sender=untread_apply_invoice)
def contract_status_as_untread_apply_invoice(sender, **kwargs):
    # 定义开票申请退回引起的合同状态变更
    related_contract = kwargs['related_contract']
    apply_invoice_related = related_contract.applyinvoice_set.all()
    if apply_invoice_related.count() == 1:
        related_contract.status = 1
        related_contract.save()

    return related_contract


@login_required()
def project_contract_page(request, msg="normal_show"):
    # 定义项目合同列表页

    return render(request, 'contract_manage/project_contract.html', {'msg': msg})


def project_contract_table(request):
    # 定义项目合同表格数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        contract_number = request.GET.get('contract_number')
        unit = request.GET.get('unit')
        linkman = request.GET.get('linkman')
        project_number = request.GET.get('project_number')

        conditions = {"contract_type": 0, }  # 构造字典存储查询条件

        if contract_number:
            conditions['contract_num__contains'] = contract_number
        if unit:
            conditions['unit_name__contains'] = unit
        if linkman:
            conditions['linkman__contains'] = linkman
        if project_number:
            conditions['project_order__project_order__project_num__contains'] = project_number
        all_contracts = ProjectContract.objects.filter(**conditions)

        all_contract_count = all_contracts.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_contracts, limit)  # 开始做分页

        response_data = {'total': all_contract_count, 'rows': []}  # 必须带有rows和total这2个key
        for contract in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            all_order = contract.project_order.all()
            order_count = all_order.count()
            if order_count == 1:
                project_numbers = all_order[0].project_order.project_num
                # 定义项目类型
                if all_order[0].project_order.project_type:
                    project_type = all_order[0].project_order.project_type.project_name
                else:
                    project_type = "-"

            elif order_count > 1:
                project_numbers = ''
                for i in range(order_count-1):
                    project_numbers += all_order[i].project_order.project_num + "、"
                project_numbers += all_order[order_count-1].project_order.project_num

                project_type = "见详细信息"
            else:
                project_numbers = "-"
                project_type = "-"
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
                "status_code": contract.status,
                "status": contract.get_status_display(),
                "project_order": project_numbers,
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

            project_contract_form.save(commit=False)
            # 若单位、项目金额为空，则不能建立合同
            project_order = project_contract_form.cleaned_data.get('project_order')
            queryset1 = project_order.values_list('project_sum', flat=True)
            project_sum_list = list(queryset1)
            queryset2 = project_order.values_list('project_order__unit', flat=True)
            project_unit_list = list(queryset2)
            all_value_list = project_sum_list + project_unit_list
            if None in all_value_list:
                msg = "info_deletion"
                form = AddProjectContractForm(request.POST, request.FILES or None)

                return render(request, "contract_manage/project_contract_add.html", {'form': form, 'msg': msg})
            else:
                # 定义合同号、合同金额、单位、联系人
                date_today = date.today()
                contract_today = ProjectContract.objects.filter(c_time__contains=date_today,
                                                                contract_type=0).order_by('-c_time')
                if contract_today:
                    contract_num = '1' + str(int(contract_today[0].contract_num) + 1)[1:]
                else:
                    contract_num = '1' + date_today.strftime('%y%m%d') + '01'
                # 定义合同金额、未开票金额
                contract_sum = sum(project_sum_list)
                not_makeout_invoice_sum = contract_sum
                project_contract.contract_num = contract_num
                project_contract.contract_sum = contract_sum
                project_contract.not_makeout_invoice_sum = not_makeout_invoice_sum
                # 定义单位
                unit = project_contract_form.cleaned_data.get('unit')
                if unit:
                    project_contract.unit_name = unit.unit_name
                else:
                    project_contract.unit_name = project_order[0].project_order.unit
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

                return redirect('contract_manage:project_contract_page', msg)
        else:
            form = AddProjectContractForm(request.POST, request.FILES or None)
            msg = "info_error"
            return render(request, "contract_manage/project_contract_add.html", {'form': form, 'msg': msg})


@login_required()
def project_contract_del(request):
    # 定义删除合同功能
    if request.method == 'POST':

        str_id = request.POST.get("str_id")
        contract_id = json.loads(str_id)
        contract = ProjectContract.objects.get(id=contract_id)
        project_orders = contract.project_order.all()
        # 归还项目结算中合同记录
        project_orders.update(contract_record=False)

        contract.delete()
        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


@login_required()
def project_contract_edit(request, contract_id):
    # 定义项目合同修改
    contract = ProjectContract.objects.get(id=contract_id)
    related_orders = contract.project_order.all()
    if request.method == 'POST':
        contract_form = EditProjectContractForm(request.POST, request.FILES or None, instance=contract)
        original_makeout_sum = contract.makeout_invoice_sum
        if contract_form.is_valid():
            change_list = contract_form.changed_data
            contract_form.save(commit=False)
            # 保存单位名称
            unit = contract_form.cleaned_data.get('unit')
            contract.unit_name = unit.unit_name
            # 定义关联项目修改（要修改合同金额）
            if "project_order" in change_list:
                related_orders.update(contract_record=False)
                new_orders = contract_form.cleaned_data.get('project_order')
                new_orders.update(contract_record=True)
                sum_aggregate = new_orders.aggregate(all_sum=Sum('project_sum'))
                contract.contract_sum = sum_aggregate['all_sum']
                contract.not_makeout_invoice_sum = sum_aggregate['all_sum'] - original_makeout_sum
            contract.save()
            contract_form.save_m2m()  # 使用commit后要手动保存manytomany

            msg = "edit_success"

            return redirect('contract_manage:project_contract_page', msg)
        else:
            contract_form = EditProjectContractForm(request.POST, request.FILES or None)

            msg = 'failed'
            return render(request, 'contract_manage/project_contract_edit.html', {'form': contract_form, 'msg': msg,
                                                                                  'contract': contract})
    elif request.method == 'GET':
        unit = UnitInvoice.objects.get(unit_name=contract.unit_name)
        orders_no_record = ProjectOrder.objects.filter(whether_distribute=True, contract_record=False)
        orders_candidate = related_orders.union(orders_no_record)
        contract_form = EditProjectContractForm(initial={'unit': unit}, instance=contract)
        contract_form.fields['project_order'].queryset = orders_candidate

        return render(request, 'contract_manage/project_contract_edit.html', {'form': contract_form,
                                                                              'contract': contract})


@login_required()
def project_contract_detail(request, contract_id):
    # 定义项目合同详情
    contract = ProjectContract.objects.get(id=contract_id)

    return render(request, 'contract_manage/project_contract_detail.html', {'contract': contract})


@login_required()
def advancepay_contract_page(request, msg="normal_show"):
    # 定义预付款合同列表页

    return render(request, 'contract_manage/advancepay_contract.html', {'msg': msg})


def advancepay_contract_table(request):
    # 定义预付款合同表格数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        contract_number = request.GET.get('contract_number')
        unit = request.GET.get('unit')
        linkman = request.GET.get('linkman')
        # sort_column = request.GET.get('sort')  # which column need to sort
        # order = request.GET.get('order')  # ascending or descending

        conditions = {"contract_type__gt": 0, }  # 构造字典存储查询条件

        if contract_number:
            conditions['contract_num__contains'] = contract_number
        if unit:
            conditions['unit_name__contains'] = unit
        if linkman:
            conditions['linkman__contains'] = linkman
        all_contracts = ProjectContract.objects.filter(**conditions)

        all_contract_count = all_contracts.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_contracts, limit)  # 开始做分页

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
                "status_code": contract.status,
                "status": contract.get_status_display(),
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

            return redirect('contract_manage:advancepay_contract_page', msg)
        else:
            form = AdvancepayContractForm(request.POST, request.FILES or None)
            msg = "info_error"
            return render(request, "contract_manage/advancepay_contract_add.html", {'form': form, 'msg': msg})


@login_required()
def advancepay_contract_del(request):
    # 定义删除合同功能
    if request.method == 'POST':

        str_id = request.POST.get("str_id")
        contract_id = json.loads(str_id)
        contract = ProjectContract.objects.get(id=contract_id)
        contract.delete()
        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


# 定义一个信号
advancepay_edit_success = django.dispatch.Signal()


@login_required()
def advancepay_contract_edit(request, contract_id):
    # 定义预付款合同修改
    contract = ProjectContract.objects.get(id=contract_id)

    if request.method == 'POST':
        contract_form = AdvancepayContractForm(request.POST, request.FILES or None, instance=contract)
        if contract_form.is_valid():
            change_list = contract_form.changed_data
            contract_form.save(commit=False)
            unit = contract_form.cleaned_data.get('unit')
            contract.unit_name = unit.unit_name
            if "contract_sum" in change_list:
                new_contract_sum = contract_form.cleaned_data.get("contract_sum")
                contract.not_makeout_invoice_sum = new_contract_sum - contract.makeout_invoice_sum
            contract.save()
            contract_form.save_m2m()  # 使用commit后要手动保存manytomany
            msg = "edit_success"

            return redirect('contract_manage:advancepay_contract_page', msg)
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
def cut_payment_info(request, msg="normal_show"):
    # 定义预付款扣款信息页

    return render(request, 'contract_manage/cut_payment_info.html', {'msg': msg})


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
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_apply, limit)  # 开始做分页

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
            order_count = orders.count()
            if order_count == 1:
                order_str = orders[0].project_order.project_num
            elif order_count > 1:
                order_str = ""
                for i in range(order_count-1):
                    order_str += orders[i].project_order.project_num + "、"
                order_str += orders[order_count-1].project_order.project_num
            else:
                order_str = "-"
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

            return redirect('contract_manage:cut_payment_info', msg)
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

            return redirect('contract_manage:cut_payment_info', msg)
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
    old_used_sum = link_contract.used_sum
    link_contract.used_sum = old_used_sum + apply_detail.cut_sum
    link_contract.save()

    # 修改作废申请状态及扣款日期
    date_today = date.today()
    apply_detail.status = 2
    apply_detail.cut_date = date_today
    apply_detail.save()
    msg = "approve_success"

    return redirect('contract_manage:cut_payment_info', msg)


@login_required()
def untread_cut_payment(request, apply_id):
    # 退回扣款申请
    apply_obj = CutPayment.objects.get(id=apply_id)
    status_val = apply_obj.status
    if status_val == 2:
        # 修改合同使用金额、剩余金额及申请状态
        link_contract = apply_obj.link_contract
        link_contract.used_sum -= apply_obj.cut_sum

        link_contract.save()

        apply_obj.status = 1
        apply_obj.cut_date = None
        apply_obj.save()
    else:
        # 修改作废申请状态
        apply_obj.status = 1
        apply_obj.save()

    msg = "untread_success"

    return redirect('contract_manage:cut_payment_info', msg)


def contract_alter_page(request, msg="normal_show"):
    # 定义合同变更页
    if request.method == 'GET':

        return render(request, 'contract_manage/contract_alter_info.html', {'msg': msg})


def contract_alter_table(request):
    # 定义合同变更表格数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        search = request.GET.get('search')

        if search:  # 判断是否有搜索字
            all_apply = ContractAlter.objects.filter(Q(link_order__project_order__project_num__contains=search) |
                                                     Q(link_contract__contract_num__contains=search))
        else:
            all_apply = ContractAlter.objects.all()

        all_apply_count = all_apply.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_apply, limit)  # 开始做分页

        response_data = {'total': all_apply_count, 'rows': []}
        for apply in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            # 定义关联合同
            related_contract = apply.related_contract
            contract_num = related_contract.contract_num
            # contract_type = related_contract.get_contract_type_display()
            # 要将date对象转化为字符串，才能进行json转换
            apply_date = apply.c_time.strftime('%Y-%m-%d')
            unit_name = apply.alter_unit
            if unit_name:
                unit = unit_name
            else:
                unit = "-"
            # 项目合同定义变更项目
            alter_projects = apply.alter_projects.all()
            project_count = alter_projects.count()
            if project_count == 1:
                project_numbers = alter_projects[0].project_order.project_num
            elif project_count > 1:
                project_numbers = ''
                for i in range(project_count - 1):
                    project_numbers += alter_projects[i].project_order.project_num + "、"
                project_numbers += alter_projects[project_count - 1].project_order.project_num
            else:
                project_numbers = "-"
            # 预付款合同定义变更金额
            alter_sum = apply.alter_sum
            if alter_sum is not None:
                contract_sum = str(alter_sum)
            else:
                contract_sum = "-"
            # 定义变更原因
            alter_reason = apply.alter_reason
            if alter_reason:
                reason_content = alter_reason
            else:
                reason_content = "-"
            file = apply.alter_contract_file
            if file:
                file_display = file.name[15:]
            else:
                file_display = ""

            response_data['rows'].append({
                "apply_id": apply.id,
                "serial_number": apply.serial_number,
                # "contract_type": contract_type,
                "alter_type": apply.get_alter_type_display(),
                "link_contract": contract_num,
                "unit": unit,
                "project_numbers": project_numbers,
                "sum": contract_sum,
                "apply_date": apply_date,
                "applicant": apply.applicant,
                "alter_reason": reason_content,
                "file_display": file_display,
                "status": apply.status,
            })

        return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def advancepay_contract_alter(request, contract_id):
    # 定义合同变更函数
    contract = ProjectContract.objects.get(id=contract_id)
    data = {}
    if request.method == 'GET':
        alter_form = AdvancePayContractAlterForm()
        data['contract'] = contract
        data['form'] = alter_form

        return render(request, 'contract_manage/advancepay_contract_alter.html', data)
    if request.method == 'POST':
        alter_apply = ContractAlter()
        alter_form = AdvancePayContractAlterForm(request.POST, request.FILES or None, instance=alter_apply)
        if alter_form.is_valid():
            alter_type = alter_form.cleaned_data.get('alter_type')
            newly_invoice = alter_form.cleaned_data.get('newly_invoice')
            alter_reason = alter_form.cleaned_data.get('alter_reason')
            # 处理申请序号、关联合同、变更类型、变更原因、申请人
            date_today = date.today()
            apply_today = ContractAlter.objects.filter(c_time__contains=date_today).order_by('-c_time')
            if apply_today:
                serial_num = int(apply_today[0].serial_number) + 1
            else:
                serial_num = date_today.strftime('%Y%m%d') + '01'
            alter_apply.serial_number = serial_num
            alter_apply.related_contract = contract
            alter_apply.alter_type = alter_type
            alter_apply.alter_reason = alter_reason
            alter_apply.applicant = request.user.first_name
            if alter_type == 'end' or (alter_type == 'edit' and newly_invoice):
                #  此时为终止合同
                alter_apply.save()
                msg = "end_submit_success"

                return redirect('contract_manage:advancepay_contract_page', msg)
            else:
                # 此时为修改合同（要另外处理“单位、合同金额、合同附件”）
                check_unit = request.POST.get('unit_check')
                check_sum = request.POST.get('sum_check')
                check_file = request.POST.get('file_check')
                if check_unit or check_sum or check_file:  # 此时要根据checkbox进行修改
                    if check_unit:
                        alter_unit = alter_form.cleaned_data.get('alter_unit')
                        alter_apply.alter_unit = alter_unit.unit_name
                    if check_sum:
                        alter_sum = alter_form.cleaned_data.get('alter_sum')
                        alter_apply.alter_sum = alter_sum
                    if check_file:
                        alter_contract_file = alter_form.cleaned_data.get('alter_contract_file')
                        alter_apply.alter_contract_file = alter_contract_file

                    alter_apply.save()
                    msg = "alter_submit_success"

                    return redirect('contract_manage:advancepay_contract_page', msg)
                else:
                    data['contract'] = contract
                    data['form'] = alter_form
                    msg = "info_less"
                    data['msg'] = msg

                    return render(request, "contract_manage/advancepay_contract_alter.html", data)
        else:
            data['contract'] = contract
            data['form'] = alter_form
            msg = "verify_fail"
            data['msg'] = msg

            return render(request, "contract_manage/advancepay_contract_alter.html", data)


@login_required()
def contract_alter_detail(request, apply_id):
    # 定义合同变更详情页

    apply_detail = ContractAlter.objects.get(id=apply_id)

    return render(request, 'contract_manage/contract_alter_detail.html', {'apply_detail': apply_detail})


@login_required()
def contract_alter_del(request):
    # 定义合同变更申请删除
    if request.method == 'POST':
        apply_id = request.POST.get("ids")
        apply = ContractAlter.objects.get(id=apply_id)
        apply.delete()

        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


@login_required()
def project_contract_alter(request, contract_id):
    # 定义项目合同变更
    contract = ProjectContract.objects.get(id=contract_id)
    data = {}
    if request.method == 'GET':
        related_projects = contract.project_order.all()
        projects_not_used = ProjectOrder.objects.filter(whether_distribute=True, contract_record=False)
        projects_candidate = related_projects.union(projects_not_used)
        alter_form = ProjectContractAlterForm()
        alter_form.fields['alter_projects'].queryset = projects_candidate

        data['contract'] = contract
        data['form'] = alter_form

        return render(request, 'contract_manage/project_contract_alter.html', data)
    if request.method == 'POST':
        alter_apply = ContractAlter()
        alter_form = ProjectContractAlterForm(request.POST, request.FILES or None, instance=alter_apply)
        if alter_form.is_valid():
            alter_type = alter_form.cleaned_data.get('alter_type')
            newly_invoice = alter_form.cleaned_data.get('newly_invoice')
            alter_reason = alter_form.cleaned_data.get('alter_reason')
            # 处理申请序号、关联合同、变更类型、变更原因、申请人
            date_today = date.today()
            apply_today = ContractAlter.objects.filter(c_time__contains=date_today).order_by('-c_time')
            if apply_today:
                serial_num = int(apply_today[0].serial_number) + 1
            else:
                serial_num = date_today.strftime('%Y%m%d') + '01'
            alter_apply.serial_number = serial_num
            alter_apply.related_contract = contract
            alter_apply.alter_type = alter_type
            alter_apply.alter_reason = alter_reason
            alter_apply.applicant = request.user.first_name
            if alter_type == 'end' or (alter_type == 'edit' and newly_invoice == 'yes'):
                #  此时为终止合同
                alter_apply.save()
                msg = "end_submit_success"

                return redirect('contract_manage:project_contract_page', msg)
            else:
                # 此时为修改合同（要另外处理“单位、关联项目、合同附件”）
                check_unit = request.POST.get('unit_check')
                check_project = request.POST.get('project_check')
                check_file = request.POST.get('file_check')
                if check_unit or check_project or check_file:  # 此时要根据checkbox进行修改
                    if check_unit:
                        alter_unit = alter_form.cleaned_data.get('alter_unit')
                        alter_apply.alter_unit = alter_unit.unit_name
                    if check_file:
                        alter_contract_file = alter_form.cleaned_data.get('alter_contract_file')
                        alter_apply.alter_contract_file = alter_contract_file
                    alter_apply.newly_invoice = False

                    alter_apply.save()
                    if check_project:
                        alter_projects = alter_form.cleaned_data.get('alter_projects')
                        alter_apply.alter_projects.set(alter_projects)
                    msg = "alter_submit_success"

                    return redirect('contract_manage:project_contract_page', msg)
                else:
                    data['contract'] = contract
                    data['form'] = alter_form
                    msg = "info_less"
                    data['msg'] = msg

                    return render(request, "contract_manage/project_contract_alter.html", data)
        else:
            data['contract'] = contract
            data['form'] = alter_form
            msg = "verify_fail"
            data['msg'] = msg
            return render(request, "contract_manage/project_contract_alter.html", data)


@login_required()
def approve_advancepay_contract_alter(request, apply_id):
    # 定义预付款合同变更审批
    if request.method == 'GET':
        alter_apply = ContractAlter.objects.get(id=apply_id)

        original_contract = alter_apply.related_contract
        alter_type = alter_apply.alter_type
        newly_invoice = alter_apply.newly_invoice
        if alter_type == 'end' or (alter_type == 'edit' and newly_invoice):
            #  此时为终止合同
            original_contract.status = 3
        else:
            # 此时为修改合同（要另外处理“单位、合同金额、合同附件”）
            alter_unit = alter_apply.alter_unit
            alter_sum = alter_apply.alter_sum
            alter_file = alter_apply.alter_contract_file
            original_makeout_invoice_sum = original_contract.makeout_invoice_sum
            if alter_unit:
                original_contract.unit_name = alter_unit
            if alter_sum is not None:  # 此时要修改合同金额、未开票金额
                original_contract.contract_sum = alter_sum
                original_contract.not_makeout_invoice_sum = alter_sum - original_makeout_invoice_sum
            if alter_file:
                original_contract.contract_file = alter_file

        original_contract.save()
        alter_apply.status = 2
        alter_apply.save()
        msg = "approve_success"

        return redirect('contract_manage:contract_alter_page', msg)


@login_required()
def approve_project_contract_alter(request, apply_id):
    # 定义项目合同变更审批功能
    if request.method == 'GET':
        alter_apply = ContractAlter.objects.get(id=apply_id)

        original_contract = alter_apply.related_contract
        related_projects = original_contract.project_order.all()
        related_projects.update(contract_record=False)

        alter_type = alter_apply.alter_type
        newly_invoice = alter_apply.newly_invoice
        if alter_type == 'end' or (alter_type == 'edit' and newly_invoice):
            #  此时为终止合同(要释放对应项目)
            original_contract.status = 3
        else:
            # 此时为修改合同（要另外处理“单位、关联项目、合同附件”）
            alter_projects = alter_apply.alter_projects.all()
            alter_file = alter_apply.alter_contract_file
            alter_unit = alter_apply.alter_unit
            if alter_projects:  # 此时要修改合同金额、未开票金额、关联新项目
                original_makeout_invoice_sum = original_contract.makeout_invoice_sum
                alter_projects.update(contract_record=True)
                original_contract.project_order.set(alter_projects)
                current_contract_sum = alter_projects.aggregate(all_sum=Sum('project_sum'))
                original_contract.contract_sum = current_contract_sum['all_sum']
                original_contract.not_makeout_invoice_sum = current_contract_sum['all_sum'] - original_makeout_invoice_sum
            if alter_file:
                original_contract.contract_file = alter_file
            if alter_unit:
                original_contract.unit_name = alter_unit

        original_contract.save()
        alter_apply.status = 2
        alter_apply.save()
        msg = "approve_success"

        return redirect('contract_manage:contract_alter_page', msg)
