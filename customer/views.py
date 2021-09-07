from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UnitInvoice, CustomerInfo
from django.core.paginator import Paginator
from django.http import HttpResponse
from . import forms
import json
from django.db.models import Q
import django.dispatch

# Create your views here.


@login_required()
def index(request):
    # 定义主页

    return render(request, 'customer/index.html')


@login_required()
def unit_list(request):
    # 定义单位信息页面

    return render(request, 'customer/unit_list.html', )


@login_required()
def unit_list_table(request):
    # 定义ajax方式获取列表数据
    if request.method == 'GET':

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        search = request.GET.get('search')
        # sort_column = request.GET.get('sort')  # which column need to sort
        # order = request.GET.get('order')  # ascending or descending
        if search:  # 判断是否有搜索字
            all_units = UnitInvoice.objects.filter(unit_name__contains=search)
        else:
            all_units = UnitInvoice.objects.all()  # must be wirte the line code here

        all_units_count = all_units.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 10  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_units, limit)  # 开始做分页

        # page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_units_count, 'rows': []}  # 必须带有rows和total这2个key
        for unit in paginator.page(pageNum):

            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            if unit.duty_paragraph:
                duty_paragraph = unit.duty_paragraph
            else:
                duty_paragraph = "-"
            if unit.bank:
                bank = unit.bank
            else:
                bank = "-"
            if unit.account:
                account = unit.account
            else:
                account = "-"
            if unit.address:
                address = unit.address
            else:
                address = "-"
            if unit.phone:
                phone = unit.phone
            else:
                phone = "-"

            response_data['rows'].append({
                "unit_id": unit.id,
                "unit_name": unit.unit_name,
                "duty_paragraph": duty_paragraph,
                "bank": bank,
                "account": account,
                "address": address,
                "phone": phone,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def unit_add(request):
    # 定义添加单位页面

    if request.method == 'POST':
        print("post请求添加单位！")
        unit_form = forms.UnitForm(request.POST)
        if unit_form.is_valid():
            unit_form.save()
            # status = "add_success"
            msg = "add_success"

            return render(request, 'customer/unit_list.html', {'msg': msg})
        else:
            msg = "repeat"
            return render(request, 'customer/unit_add.html', {'form': unit_form, 'msg': msg})
    elif request.method == 'GET':
        unit_form = forms.UnitForm()

        return render(request, 'customer/unit_add.html', {'form': unit_form, })


@login_required()
def unit_del(request):
    # 定义删除功能函数
    if request.method == 'POST':

        # if request.POST.get("type") == "post":
        ids = request.POST.get("ids")
        for unit_id in json.loads(ids):
            unit = UnitInvoice.objects.get(id=unit_id)
            unit.delete()
        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


@login_required()
def unit_edit(request, unit_id):
    # 定义单位编辑页面

    unit = UnitInvoice.objects.get(id=unit_id)
    if request.method == 'POST':
        unit_name = request.POST.get("unit_name")
        if unit_name == unit.unit_name:
            unit_form = forms.UnitForm(request.POST, instance=unit)
            unit_form.save()
            msg = "edit_success"
            return render(request, 'customer/unit_list.html', {'msg': msg})
        else:
            new_unit = UnitInvoice.objects.filter(unit_name=unit_name)
            if new_unit:
                msg = 'repeat'
                unit_form = forms.UnitForm(request.POST)
                return render(request, 'customer/unit_edit.html', {'form': unit_form, 'msg': msg, 'unit': unit})
            else:
                unit_form = forms.UnitForm(request.POST, instance=unit)
                unit_form.save()
                msg = "edit_success"
                return render(request, 'customer/unit_list.html', {'msg': msg})

    elif request.method == 'GET':

        unit_form = forms.UnitForm(instance=unit)
        return render(request, 'customer/unit_edit.html', {'form': unit_form, 'unit': unit})


def unit_import(request):
    # 定义单位导入函数
    if request.method == 'GET':
        excel_path = "D:\\PyProgram\\Spec-ally\\unit_list.txt"
        fin = open(excel_path, 'rt', encoding='UTF-8')
        lines = fin.readlines()  # 返回字符串列表
        fin.close()

        for line in lines:
            str_list = line.rstrip().split()
            unit_name = str_list[0]
            duty_paragraph = str_list[1]
            bank = str_list[2]
            account = str_list[3]
            address = str_list[4]
            phone = str_list[5]
            person_add = "管理员"
            unit_new = UnitInvoice(unit_name=unit_name, duty_paragraph=duty_paragraph, bank=bank, account=account,
                                   address=address, phone=phone, person_add=person_add)
            unit_new.save()
        msg = "import_success"
        # print(str_list)
        return HttpResponse(msg)


@login_required()
def customer_list(request):
    # 定义单位信息页面

    units = UnitInvoice.objects.all()
    unit_dict = {}
    for unit in units:
        unit_dict[unit.id] = unit.unit_name
    # print(unit_dict)
    return render(request, 'customer/customer_list.html', {'unit_dict': unit_dict})


@login_required()
def customer_list_table(request):
    # 定义ajax方式获取列表数据

    if request.method == 'GET':
        # print(request.GET)
        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        search = request.GET.get('search')

        if search:  # 判断是否有搜索字
            all_customers = CustomerInfo.objects.filter(Q(customer_name__contains=search) |
                                                        Q(unit__unit_name__contains=search))
        else:
            all_customers = CustomerInfo.objects.all()

        all_customers_count = all_customers.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 10  # 默认是每页20行的内容，与前端默认行数一致
        paginator = Paginator(all_customers, limit)  # 开始做分页

        # page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_customers_count, 'rows': []}  # 必须带有rows和total这2个key
        for customer in paginator.page(pageNum):

            if customer.unit:
                unit_name = customer.unit.unit_name
                unit_id = customer.unit.id
            else:
                unit_name = "-"
                unit_id = 0  # id从1开始
            if customer.phone:
                phone = customer.phone
            else:
                phone = "-"
            if customer.mail:
                mail = customer.mail
            else:
                mail = "-"
            if customer.department:
                department = customer.department
            else:
                department = "-"
            if customer.leading_official:
                leading_official = customer.leading_official
            else:
                leading_official = "-"
            if customer.note:
                note = customer.note
            else:
                note = "-"

            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.
            response_data['rows'].append({
                # "num": 1,
                "customer_id": customer.id,
                "customer_name": customer.customer_name,
                "phone": phone,
                "mail": mail,
                "unit_id": unit_id,
                "unit_name": unit_name,
                "department": department,
                "leading_official": leading_official,
                "note": note,
                "person_add": customer.person_add,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def customer_add(request):
    # 定义添加单位页面

    if request.method == 'POST':

        customer_info_form = forms.CustomerInfoForm(request.POST)
        if customer_info_form.is_valid():
            customer_info_form.save()
            msg = "add_success"
            return render(request, 'customer/customer_list.html', {'msg': msg})
        else:
            msg = "repeat"
            return render(request, 'customer/customer_add.html', {'form': customer_info_form, 'msg': msg})
    elif request.method == 'GET':
        customer_form = forms.CustomerInfoForm()

    return render(request, 'customer/customer_add.html', {'form': customer_form})


@login_required()
def customer_del(request):
    # 定义删除客户功能函数
    if request.method == 'POST':

        ids = request.POST.get("ids")
        for customer_id in json.loads(ids):
            customer = CustomerInfo.objects.get(id=customer_id)
            customer.delete()
        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


# 定义一个添加单位信号
project_add_unit = django.dispatch.Signal()
# 定义一个添加送样终端信号
project_add_terminal = django.dispatch.Signal()


@login_required()
def customer_edit(request, customer_id):
    # 定义客户编辑页面
    customer_info = CustomerInfo.objects.get(id=customer_id)

    if request.method == 'POST':
        unit = customer_info.unit
        leading_official = customer_info.leading_official
        customer_info_form = forms.CustomerInfoForm(request.POST, instance=customer_info)
        if customer_info_form.is_valid():
            change_list = customer_info_form.changed_data
            customer_info_form.save()
            # 修改关联项目的单位和终端信息
            if unit is None and 'unit' in change_list:
                new_unit = customer_info_form.cleaned_data.get("unit")
                msg = "edit_project_unit"
                project_add_unit.send(customer_edit, msg=msg, customer_id=customer_info.id, unit_name=new_unit.unit_name)
            if not leading_official and 'leading_official' in change_list:
                terminal = customer_info_form.cleaned_data.get("leading_official")
                msg = "edit_project_terminal"
                project_add_terminal.send(customer_edit, msg=msg, customer_id=customer_info.id, terminal_name=terminal)
            msg = "edit_success"
            return render(request, 'customer/customer_list.html', {'msg': msg})
        else:
            customer_info_form = forms.CustomerInfoForm(request.POST)
            msg = 'failed'
            return render(request, 'customer/customer_edit.html', {'form': customer_info_form, 'msg': msg,
                                                                   'customer_info': customer_info})
    elif request.method == 'GET':
        customer_form = forms.CustomerInfoForm(instance=customer_info)
        return render(request, 'customer/customer_edit.html', {'form': customer_form, 'customer_info': customer_info})
