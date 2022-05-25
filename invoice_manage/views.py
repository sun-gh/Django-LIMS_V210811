from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import forms
from .models import ApplyInvoice, ReimburseFile, InvoiceInfo, VoidRedInfo
from datetime import date
from django.core.paginator import Paginator
from django.http import HttpResponse
import json
from customer.models import UnitInvoice
from django.db.models import Q
# from django.dispatch import receiver
# from contract_manage.views import advancepay_edit_success, advancepay_contract_edit

# Create your views here.


# @receiver(advancepay_edit_success, sender=advancepay_contract_edit)
# def edit_invoice_type(sender, **kwargs):
#     apply_query = kwargs['apply_query']
#     contract = kwargs['contract']
#     apply_query.update(invoice_type=contract.contract_type)


@login_required()
def apply_invoice(request):
    # 定义申请开票函数
    if request.method == 'GET':

        apply_form = forms.ApplyInvoiceForm()
        return render(request, 'invoice_manage/apply_invoice.html', {'form': apply_form})
    elif request.method == 'POST':
        apply_instance = ApplyInvoice()
        apply_form = forms.ApplyInvoiceForm(request.POST, request.FILES or None, instance=apply_instance)
        if apply_form.is_valid():

            apply_form.save(commit=False)
            # 定义申请序号
            date_today = date.today()
            apply_today = ApplyInvoice.objects.filter(c_time__contains=date_today).order_by('-c_time')
            if apply_today:
                serial_num = int(apply_today[0].serial_number) + 1
            else:
                serial_num = date_today.strftime('%Y%m%d') + '01'
            apply_instance.serial_number = serial_num
            # 处理单位内容
            unit = apply_form.cleaned_data.get("unit_name")
            apply_instance.unit = unit.unit_name
            # 处理开票类型
            related_contract = apply_form.cleaned_data.get("related_contract")
            apply_instance.invoice_type = related_contract.contract_type

            apply_instance.save()
            apply_form.save_m2m()
            # 定义文件添加
            file_list = request.FILES.getlist('file_input')  # 获取上传的多个文件的列表
            file_obj = []
            for file in file_list:
                file_instance = ReimburseFile.objects.create(file=file)
                file_obj.append(file_instance)
            for file in file_obj:
                apply_instance.reimburse_file.add(file)

            msg = "add_success"
            # 发送一个信号
            # add_success.send(sample_record_add, msg=msg, sample_rec_id=sample_rec.id)

            return redirect("invoice_manage:apply_invoice_record", msg)
        else:
            form = forms.ApplyInvoiceForm(request.POST, request.FILES or None)
            msg = "info_error"
            return render(request, "invoice_manage/apply_invoice.html", {'form': form, 'msg': msg})


@login_required()
def apply_invoice_record(request, msg="normal_show"):
    # 定义开票申请记录页

    return render(request, 'invoice_manage/apply_invoice_record.html', {'msg': msg})


def apply_invoice_table(request):
    # 定义开票申请表数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        # search = request.GET.get('search')
        contract_number = request.GET.get('contract_number')
        unit = request.GET.get('unit')
        linkman = request.GET.get('linkman')

        conditions = {}  # 构造字典存储查询条件

        if contract_number:
            conditions['related_contract__contract_num__contains'] = contract_number
        if unit:
            conditions['unit__contains'] = unit
        if linkman:
            conditions['linkman__contains'] = linkman
        all_apply = ApplyInvoice.objects.filter(**conditions)

        all_apply_count = all_apply.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_apply, limit)  # 开始做分页

        # page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_apply_count, 'rows': []}
        for apply in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            # 定义合同编号（可能存在合同被删除的情况）
            related_contract = apply.related_contract
            if related_contract:
                contract = related_contract.contract_num
            else:
                contract = "-"
            # 开票要求处理
            all_require = apply.invoice_require.all()
            if all_require:
                if all_require.count() == 1:
                    invoice_require = all_require[0].require_content
                else:
                    invoice_require = str(all_require.count()) + "项要求"
            else:
                invoice_require = "-"
            # 定义文件显示
            files = apply.reimburse_file.all()
            if files:
                if files.count() == 1:
                    file_display = files[0].file.name[16:]
                else:
                    file_display = files.count()
            else:
                file_display = ""
            # 定义联系人相关
            linkman = apply.linkman
            if linkman:
                linkman = linkman
            else:
                linkman = "-"
            phone = apply.phone
            if phone:
                phone = phone
            else:
                phone = "-"
            address = apply.address_linkman
            if address:
                address_linkman = address
            else:
                address_linkman = "-"
            # 定义备注
            note_content = apply.note
            if note_content:
                note = note_content
            else:
                note = "-"
            # 要将date对象转化为字符串，才能进行json转换
            apply_date = apply.c_time.strftime('%Y-%m-%d')
            post_date = apply.post_date
            if post_date:
                post = post_date.strftime('%Y-%m-%d')
            else:
                post = "-"
            # 定义快递单号
            express = apply.express_num
            if express:
                express_num = express
            else:
                express_num = "-"

            response_data['rows'].append({
                "apply_id": apply.id,
                "serial_number": apply.serial_number,
                "status": apply.status,
                # "related_contract": apply.related_contract.contract_num,
                "related_contract": contract,
                "unit": apply.unit,
                "invoice_sum": str(apply.invoice_sum),
                "sheet_num": apply.sheet_num,
                "invoice_require": invoice_require,
                "invoice_type": apply.get_invoice_type_display(),
                "reimburse_file": file_display,
                # 联系人信息
                "linkman": linkman,
                "phone": phone,
                "address_linkman": address_linkman,
                "note": note,
                "applicant": apply.applicant,
                "a_time": apply_date,
                "post_date": post,
                "express_num": express_num,
            })

        return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def apply_invoice_detail(request, apply_id):
    # 定义开票申请详情

    apply_detail = ApplyInvoice.objects.get(id=apply_id)

    return render(request, 'invoice_manage/apply_invoice_detail.html', {'apply': apply_detail})


@login_required()
def apply_invoice_edit(request, apply_id):
    # 定义开票申请修改
    apply_info = ApplyInvoice.objects.get(id=apply_id)

    if request.method == 'POST':
        apply_form = forms.ApplyInvoiceForm(request.POST, request.FILES or None, instance=apply_info)
        if apply_form.is_valid():
            change_list = apply_form.changed_data
            apply_form.save(commit=False)
            if "unit_name" in change_list:
                # 保存单位名称
                unit = apply_form.cleaned_data.get('unit_name')
                apply_info.unit = unit.unit_name
            if "related_contract" in change_list:
                # 处理开票类型
                related_contract = apply_form.cleaned_data.get("related_contract")
                apply_info.invoice_type = related_contract.contract_type
            apply_info.status = 0

            apply_info.save()
            apply_form.save_m2m()  # 使用commit后要手动保存manytomany

            # 对另外添加的文件单独处理
            file_list = request.FILES.getlist('file_input')  # 获取上传的多个文件的列表
            file_obj = []
            for file in file_list:
                file_instance = ReimburseFile.objects.create(file=file)
                file_obj.append(file_instance)
            for file in file_obj:
                apply_info.reimburse_file.add(file)
            msg = "edit_success"

            return redirect("invoice_manage:apply_invoice_record", msg)
        else:
            apply_form = forms.ApplyInvoiceForm(request.POST, request.FILES or None)
            msg = 'failed'
            return render(request, 'invoice_manage/apply_invoice_edit.html', {'form': apply_form, 'msg': msg,
                                                                              'apply_info': apply_info})
    elif request.method == 'GET':
        unit = UnitInvoice.objects.get(unit_name=apply_info.unit)
        apply_form = forms.ApplyInvoiceForm(initial={'unit_name': unit}, instance=apply_info)
        return render(request, 'invoice_manage/apply_invoice_edit.html', {'form': apply_form, 'apply_info': apply_info})


@login_required()
def apply_invoice_del(request):
    # 定义删除开票申请
    if request.method == 'POST':

        apply_id = request.POST.get("ids")
        apply = ApplyInvoice.objects.get(id=apply_id)
        apply.delete()

        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


@login_required()
def approve_apply_invoice(request, apply_id):
    # 定义开票申请审批
    apply_detail = ApplyInvoice.objects.get(id=apply_id)

    sheet_number = apply_detail.sheet_num
    # 若只开一张票，直接赋值开票金额为发票金额
    if sheet_number == 1:
        invoice_info = InvoiceInfo.objects.create(link_apply=apply_detail, unit_invoice=apply_detail.unit,
                                                  linkman=apply_detail.related_contract.linkman,
                                                  applicant=apply_detail.applicant, invoice_sum=apply_detail.invoice_sum)
    else:
        start_num = 1
        while start_num <= sheet_number:
            invoice_info = InvoiceInfo.objects.create(link_apply=apply_detail, unit_invoice=apply_detail.unit,
                                                      linkman=apply_detail.related_contract.linkman,
                                                      applicant=apply_detail.applicant)
            start_num += 1
    # 修改开票申请状态
    apply_detail.status = 1
    apply_detail.save()
    msg = "approve_success"

    return redirect("invoice_manage:apply_invoice_record", msg)


@login_required()
def untread_apply_invoice(request, apply_id):
    # 定义开票申请退回
    apply_obj = ApplyInvoice.objects.get(id=apply_id)
    status_val = apply_obj.status
    if status_val < 2:
        # 若已开票，无法退回
        invoice_info = InvoiceInfo.objects.filter(link_apply_id=apply_id)
        invoice_num = invoice_info.filter(invoice_num__isnull=False).count()
        if invoice_num:
            msg = "untread_forbid"
            return render(request, 'invoice_manage/apply_invoice_detail.html', {'apply': apply_obj, 'msg': msg})
        else:
            for invoice in invoice_info:
                invoice.delete()
            # 修改开票申请状态
            apply_obj.status = 2
            apply_obj.save()

            msg = "untread_success"

            return redirect("invoice_manage:apply_invoice_record", msg)
    else:
        msg = "untread_failed"
        return render(request, 'invoice_manage/apply_invoice_detail.html', {'apply': apply_obj, 'msg': msg})


@login_required()
def file_apply_invoice(request, apply_id):
    # 定义开票申请归档
    apply_obj = ApplyInvoice.objects.get(id=apply_id)
    if request.method == 'POST':
        file_form = forms.FileApplyInvoiceForm(request.POST, instance=apply_obj)
        if file_form.is_valid():
            # change_list = project_info_form.changed_data
            file_form.save(commit=False)
            # 修改开票申请状态
            apply_obj.status = 3
            apply_obj.save()

            file_form.save_m2m()  # 使用commit后要手动保存manytomany

            msg = "file_success"

            return redirect("invoice_manage:apply_invoice_record", msg)
        else:
            file_form = forms.FileApplyInvoiceForm(request.POST)
            msg = 'failed'
            return render(request, 'invoice_manage/file_apply_invoice.html', {'form': file_form, 'msg': msg,
                                                                              'apply_info': apply_obj})
    elif request.method == 'GET':
        file_form = forms.FileApplyInvoiceForm()
        return render(request, 'invoice_manage/file_apply_invoice.html', {'form': file_form, 'apply_info': apply_obj})


@login_required()
def invoice_info(request, msg="normal_show"):
    # 定义已开发票信息页

    return render(request, 'invoice_manage/invoice_info.html', {'msg': msg})


@login_required()
def invoice_info_table(request):
    # 定义已开发票信息数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        # search = request.GET.get('search')
        contract_number = request.GET.get('contract_number')
        unit = request.GET.get('unit')
        invoice_num = request.GET.get('invoice_num')

        conditions = {}  # 构造字典存储查询条件

        if contract_number:
            conditions['link_apply__related_contract__contract_num__contains'] = contract_number
        if unit:
            conditions['unit_invoice__contains'] = unit
        if invoice_num:
            conditions['invoice_num__contains'] = invoice_num
        all_invoice = InvoiceInfo.objects.filter(**conditions)

        invoice_count = all_invoice.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_invoice, limit)  # 开始做分页

        response_data = {'total': invoice_count, 'rows': []}
        for invoice in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            # 定义发票号
            invoice_num = invoice.invoice_num
            if invoice_num:
                invoice_num = invoice_num
            else:
                invoice_num = "待开票"
            # 定义关联合同(可能会存在合同被删除的情况)
            related_contract = invoice.link_apply.related_contract
            if related_contract:
                contract = related_contract.contract_num
            else:
                contract = "-"
            # 定义发票金额
            invoice_sum = invoice.invoice_sum
            if invoice_sum:
                invoice_sum = str(invoice_sum)
            else:
                invoice_sum = "-"
            # 定义发票是否收回
            if invoice.invoice_callback is None:
                invoice_callback = "未知"
            elif invoice.invoice_callback:
                invoice_callback = "是"
            else:
                invoice_callback = "否"
            # 定义未收回原因
            if invoice.reason:
                reason = invoice.reason
            else:
                reason = "-"
            # 要将date对象转化为字符串，才能进行json转换
            invoice_date = invoice.invoice_date
            if invoice_date:
                invoice_date = invoice_date.strftime('%Y-%m-%d')
            else:
                invoice_date = "-"
            payment_date = invoice.payment_date
            if payment_date:
                payment_date = payment_date.strftime('%Y-%m-%d')
            else:
                payment_date = "-"
            payment_sum = invoice.payment_sum
            if payment_sum:
                payment_sum = str(payment_sum)
            else:
                payment_sum = "-"
            # 定义备注
            note_content = invoice.note
            if note_content:
                note = note_content
            else:
                note = "-"

            response_data['rows'].append({
                "invoice_id": invoice.id,
                "invoice_number": invoice_num,
                "link_contract": contract,
                "unit": invoice.unit_invoice,
                "linkman": invoice.linkman,
                "applicant": invoice.applicant,
                "invoice_sum": invoice_sum,
                "invoice_date": invoice_date,
                "payment_date": payment_date,
                "void_red": invoice.get_void_red_display(),
                "invoice_callback": invoice_callback,
                "reason": reason,
                "payment_sum": payment_sum,
                "note": note,
            })

        return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def edit_invoice_info(request, invoice_id):
    # 定义修改发票信息
    invoice = InvoiceInfo.objects.get(id=invoice_id)

    if request.method == 'POST':
        old_invoice_num = invoice.invoice_num
        old_invoice_sum = invoice.invoice_sum
        invoice_form = forms.EditInvoiceInfoForm(request.POST, instance=invoice)
        if invoice_form.is_valid():
            change_list = invoice_form.changed_data
            new_sum = invoice_form.cleaned_data.get('invoice_sum')
            invoice_form.save(commit=False)
            # 修改相应合同的已开票金额和未开票金额
            if old_invoice_num:
                if "invoice_sum" in change_list:
                    difference = new_sum - old_invoice_sum
                    contract = invoice.link_apply.related_contract
                    old_makeout_sum = contract.makeout_invoice_sum
                    # 修改已开票金额
                    contract.makeout_invoice_sum = old_makeout_sum + difference
                    # 修改未开票金额
                    contract.not_makeout_invoice_sum = contract.contract_sum - old_makeout_sum - difference
                    contract.save()
                    # 若发票金额无变化，对应合同信息不用修改
            else:
                # 此时为首次修改,即添加发票（此处包括了红冲时产生一张金额为负的发票添加，并对相关合同的修改）
                contract = invoice.link_apply.related_contract
                # 要考虑一个合同对应多张票
                old_makeout_sum = contract.makeout_invoice_sum
                contract.makeout_invoice_sum = old_makeout_sum + new_sum
                contract.not_makeout_invoice_sum = contract.contract_sum - new_sum - old_makeout_sum
                contract.save()

            invoice.save()
            invoice_form.save_m2m()

            msg = "edit_invoice_success"

            return redirect('invoice_manage:invoice_info', msg)
        else:
            invoice_form = forms.EditInvoiceInfoForm(request.POST)
            msg = 'failed'
            return render(request, 'invoice_manage/edit_invoice_info.html', {'form': invoice_form, 'msg': msg,
                                                                             'invoice': invoice})
    elif request.method == 'GET':

        invoice_form = forms.EditInvoiceInfoForm(instance=invoice)

        return render(request, 'invoice_manage/edit_invoice_info.html', {'form': invoice_form, 'invoice': invoice})


@login_required()
def edit_pay_info(request, invoice_id):
    # 回款信息修改
    invoice = InvoiceInfo.objects.get(id=invoice_id)

    if request.method == 'POST':

        old_payment_sum = invoice.payment_sum
        invoice_form = forms.EditPayInfoForm(request.POST, instance=invoice)
        if invoice_form.is_valid():
            # change_list = invoice_form.changed_data
            # 要修改对应合同回款金额
            link_contract = invoice.link_apply.related_contract
            new_payment_sum = invoice_form.cleaned_data.get('payment_sum')
            if old_payment_sum:   # 则为修改回款信息
                difference = new_payment_sum - old_payment_sum
                link_contract.payment_sum += difference
            else:   # 则为添加回款信息
                link_contract.payment_sum += new_payment_sum
            link_contract.save()
            invoice_form.save()
            msg = "edit_payment_success"

            return redirect('invoice_manage:invoice_info', msg)
        else:
            invoice_form = forms.EditPayInfoForm(request.POST)
            msg = 'failed'
            return render(request, 'invoice_manage/edit_pay_info.html', {'form': invoice_form, 'msg': msg,
                                                                         'invoice': invoice})
    elif request.method == 'GET':

        invoice_form = forms.EditPayInfoForm(instance=invoice)

        return render(request, 'invoice_manage/edit_pay_info.html', {'form': invoice_form, 'invoice': invoice})


@login_required()
def invoice_info_detail(request, invoice_id):
    # 定义发票信息详情
    invoice_detail = InvoiceInfo.objects.get(id=invoice_id)

    return render(request, 'invoice_manage/invoice_info_detail.html', {'invoice': invoice_detail})


@login_required()
def apply_void_red(request):
    # 定义申请作废冲红
    if request.method == 'GET':

        apply_form = forms.ApplyVoidRedForm()
        return render(request, 'invoice_manage/apply_void_red.html', {'form': apply_form})
    elif request.method == 'POST':
        apply_instance = VoidRedInfo()
        apply_form = forms.ApplyVoidRedForm(request.POST, instance=apply_instance)
        if apply_form.is_valid():

            apply_form.save(commit=False)
            # 定义申请序号
            date_today = date.today()
            apply_today = VoidRedInfo.objects.filter(c_time__contains=date_today).order_by('-c_time')
            if apply_today:
                serial_num = int(apply_today[0].serial_number) + 1
            else:
                serial_num = date_today.strftime('%Y%m%d') + '01'
            apply_instance.serial_number = serial_num

            apply_instance.save()
            apply_form.save_m2m()

            msg = "add_success"
            # 发送一个信号
            # add_success.send(sample_record_add, msg=msg, sample_rec_id=sample_rec.id)

            return redirect("invoice_manage:void_red_info", msg)
        else:
            form = forms.ApplyVoidRedForm(request.POST)
            msg = "info_error"
            return render(request, "invoice_manage/apply_void_red.html", {'form': form, 'msg': msg})


@login_required()
def void_red_info(request, msg="normal_show"):
    # 定义发票作废/冲红信息页

    return render(request, 'invoice_manage/void_red_info.html', {'msg': msg})


@login_required()
def void_red_info_table(request):
    # 定义发票作废/冲红信息数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        search = request.GET.get('search')
        # sort_column = request.GET.get('sort')  # which column need to sort
        # order = request.GET.get('order')  # ascending or descending
        if search:  # 判断是否有搜索字
            all_apply = VoidRedInfo.objects.filter(Q(serial_number__contains=search) |
                                                   Q(link_invoice__invoice_num__contains=search))
        else:
            all_apply = VoidRedInfo.objects.all()

        apply_count = all_apply.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_apply, limit)  # 开始做分页

        response_data = {'total': apply_count, 'rows': []}
        for apply in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            # 发票号处理
            invoices = apply.link_invoice.all()
            invoice_count = invoices.count()
            if invoice_count == 1:
                invoice_str = invoices[0].invoice_num
            elif invoice_count > 1:
                invoice_str = ""
                for i in range(invoice_count-1):
                    invoice_str += invoices[i].invoice_num+"、"
                invoice_str += invoices[invoice_count-1].invoice_num
            else:
                invoice_str = "-"
            # 定义冲红原因
            reason_content = apply.reason
            if reason_content:
                reason = reason_content
            else:
                reason = "-"
            # 要将date对象转化为字符串，才能进行json转换
            apply_date = apply.c_time.strftime('%Y-%m-%d')

            response_data['rows'].append({
                "apply_id": apply.id,
                "serial_number": apply.serial_number,
                "invoice_num": invoice_str,
                "reason": reason,
                "treat_type": apply.get_treat_type_display(),
                "applicant": apply.applicant,
                "apply_date": apply_date,
                "status": apply.status,
            })

        return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def edit_void_red(request, apply_id):
    # 修改发票红冲申请
    apply_info = VoidRedInfo.objects.get(id=apply_id)

    if request.method == 'POST':
        apply_form = forms.ApplyVoidRedForm(request.POST, instance=apply_info)
        if apply_form.is_valid():
            # change_list = project_info_form.changed_data
            apply_form.save(commit=False)
            # 修改状态
            apply_info.status = 0

            apply_info.save()
            apply_form.save_m2m()  # 使用commit后要手动保存manytomany

            msg = "edit_success"

            return redirect('invoice_manage:void_red_info', msg)
        else:
            apply_form = forms.ApplyVoidRedForm(request.POST)
            msg = 'failed'
            return render(request, 'invoice_manage/edit_void_red.html', {'form': apply_form, 'msg': msg,
                                                                         'apply_info': apply_info})
    elif request.method == 'GET':
        apply_form = forms.ApplyVoidRedForm(instance=apply_info)

        return render(request, 'invoice_manage/edit_void_red.html', {'form': apply_form, 'apply_info': apply_info})


@login_required()
def void_red_detail(request, apply_id):
    # 定义发票作废详情
    apply_detail = VoidRedInfo.objects.get(id=apply_id)

    return render(request, 'invoice_manage/void_red_detail.html', {'apply_detail': apply_detail})


@login_required()
def apply_void_del(request):
    # 定义发票作废申请删除
    if request.method == 'POST':

        apply_id = request.POST.get("ids")
        apply = VoidRedInfo.objects.get(id=apply_id)
        apply.delete()

        return HttpResponse("del_success")
    return HttpResponse("非POST请求！")


@login_required()
def approve_apply_void(request, apply_id):
    # 审批发票作废申请
    apply_detail = VoidRedInfo.objects.get(id=apply_id)
    invoices = apply_detail.link_invoice.all()

    treat_type = apply_detail.treat_type
    if treat_type == 1:  # 此时为冲红处理，要产生金额为负数的发票，申请人与冲红申请保持一致
        for invoice in invoices:
            link_apply = invoice.link_apply
            unit = invoice.unit_invoice
            applicant = apply_detail.applicant
            invoice_sum = - invoice.invoice_sum
            invoice_instance = InvoiceInfo.objects.create(link_apply=link_apply, unit_invoice=unit, applicant=applicant,
                                                          invoice_sum=invoice_sum, void_red=1)
            # 修改发票作废/冲红记录
            invoice.void_red = treat_type
            invoice.save()
    else:  # 此时为作废处理
        for invoice in invoices:
            # 修改发票对应合同的已开票和未开票金额
            invoice_sum = invoice.invoice_sum
            link_contract = invoice.link_apply.related_contract
            link_contract.makeout_invoice_sum -= invoice_sum
            link_contract.not_makeout_invoice_sum += invoice_sum
            link_contract.save()
            # 修改发票作废/冲红记录
            invoice.void_red = treat_type
            invoice.save()

    # 修改作废申请状态
    apply_detail.status = 2
    apply_detail.save()
    msg = "approve_success"

    return redirect('invoice_manage:void_red_info', msg)


@login_required()
def untread_apply_void(request, apply_id):
    # 定义发票作废申请退回
    apply_obj = VoidRedInfo.objects.get(id=apply_id)
    status_val = apply_obj.status
    if status_val < 1:
        # 修改作废申请状态
        apply_obj.status = 1
        apply_obj.save()

        msg = "untread_success"

        return redirect('invoice_manage:void_red_info', msg)
    else:
        msg = "untread_failed"
        return render(request, 'invoice_manage/void_red_detail.html', {'apply': apply_obj, 'msg': msg})
