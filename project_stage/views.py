from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SampleRecord, FilesRelated, ProjectType
from .forms import SampleRecordForm, PretreatStageForm, TestAnalysisForm
from django.core.paginator import Paginator
from django.http import HttpResponse
import json
from datetime import date, timedelta
import django.dispatch
from django.dispatch import receiver
from customer.views import customer_edit, project_add_unit, project_add_terminal
from django.db.models import Q

# Create your views here.


# 定义样本登记中单位信息修改
@receiver(project_add_unit, sender=customer_edit)
def edit_project_unit(sender, **kwargs):
    # print(kwargs['msg'])
    sample_records = SampleRecord.objects.filter(sample_sender__id=kwargs['customer_id'])
    for record in sample_records:
        if record.unit is None:
            record.unit = kwargs['unit_name']
            record.save()

    return sample_records


# 定义样本登记中终端信息修改
@receiver(project_add_terminal, sender=customer_edit)
def edit_project_terminal(sender, **kwargs):
    # print(kwargs['msg'])
    sample_records = SampleRecord.objects.filter(sample_sender__id=kwargs['customer_id'])
    for record in sample_records:
        if record.terminal is None:
            record.terminal = kwargs['terminal_name']
            record.save()

    return sample_records


@login_required()
def sample_record(request):
    # 定义样本登记页面

    if request.method == 'GET':
        return render(request, 'project_stage/sample_record.html')


def sample_record_table(request):
    # 定义ajax方式获取列表数据
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
            # 定义单位和终端
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

            if project.sample_quality:
                sample_quality = project.sample_quality.quality_type
            else:
                sample_quality = "-"
            # addition_item为多对多，显示分多种情况
            all_item = project.addition_item.all()
            if all_item:
                if all_item.count() == 1:
                    addition_item = all_item[0].item_type
                else:
                    addition_item = str(all_item.count()) + "个附加项"
            else:
                addition_item = "-"
            # 定义项目来源
            project_source = project.get_project_source_display()
            if project.note:
                note = project.note
            else:
                note = "-"
            # 要将date对象转化为字符串，才能进行json转换
            receive_date = project.receive_date.strftime('%Y-%m-%d')
            # 定义文件显示
            files = project.files.all()
            if files:
                if files.count() == 1:
                    file_display = files[0].file.name
                else:
                    file_display = files.count()
            else:
                file_display = ""

            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                "project_type": project_type,
                "sample_type": sample_type,
                "machine_time": machine_time,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": project.sample_sender.customer_name,
                "sample_quality": sample_quality,
                "addition_item": addition_item,
                "receive_date": receive_date,
                "project_source": project_source,
                "note": note,
                "files": file_display,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


# 定义一个信号
add_success = django.dispatch.Signal()


@login_required()
def sample_record_add(request):
    # 定义样本登记添加函数
    if request.method == 'GET':
        form = SampleRecordForm()
        return render(request, "project_stage/sample_record_add.html", {'form': form})
    elif request.method == 'POST':
        sample_rec = SampleRecord()
        sample_rec_form = SampleRecordForm(request.POST, request.FILES or None, instance=sample_rec)
        if sample_rec_form.is_valid():

            sample_rec_form.save(commit=False)
            # 定义项目号
            date_today = date.today()
            pro_today = SampleRecord.objects.filter(c_time__contains=date_today).order_by('-c_time')
            if pro_today:
                project_num = int(pro_today[0].project_num) + 1
            else:
                project_num = date_today.strftime('%y%m%d') + '01'
            sample_rec.project_num = project_num
            # 定义单位和送样终端
            sample_sender = sample_rec_form.cleaned_data.get("sample_sender")
            unit = sample_sender.unit
            if unit:
                sample_rec.unit = unit.unit_name
            terminal = sample_sender.leading_official
            if terminal:
                sample_rec.terminal = terminal
            pro_type = ProjectType.objects.get(id=request.POST.get("project_type"))
            receive_date = sample_rec_form.cleaned_data.get("receive_date")
            # 定义启动截至日期
            start_days = pro_type.start_deadline
            if start_days:
                sample_rec.start_deadline = receive_date + timedelta(days=start_days)
            # 定义预实验截至日期
            preexperiment_days = pro_type.pre_experiment_cycle
            if preexperiment_days:
                sample_rec.preexperiment_deadline = receive_date + timedelta(days=preexperiment_days)
            # 定义前处理截至日期和下机截止日期
            pre_process_days = pro_type.pre_process_cycle
            if pre_process_days:
                sample_rec.pretreat_deadline = receive_date + timedelta(days=pre_process_days)
                sample_rec.test_deadline = receive_date + timedelta(days=pre_process_days + pro_type.test_cycle)
            else:
                sample_rec.test_deadline = receive_date + timedelta(days=pro_type.test_cycle)
            # 定义项目截至日期
            sample_rec.pro_deadline = receive_date + timedelta(days=pro_type.total_cycle)

            sample_rec.save()
            sample_rec_form.save_m2m()   # 使用commit后要手动保存manytomany
            # 定义文件添加
            file_list = request.FILES.getlist('file_input')  # 获取上传的多个文件的列表
            file_obj = []
            for file in file_list:
                file_instance = FilesRelated.objects.create(file=file)
                file_obj.append(file_instance)
            # print(sample_rec.sample_num)
            for file in file_obj:
                sample_rec.files.add(file)
            msg = "add_success"
            # 发送一个信号
            add_success.send(sample_record_add, msg=msg, sample_rec_id=sample_rec.id)

            return render(request, "project_stage/sample_record.html", {'msg': msg})
        else:
            form = SampleRecordForm(request.POST, request.FILES or None)
            msg = "info_error"
            return render(request, "project_stage/sample_record_add.html", {'form': form, 'msg': msg})


@login_required()
def sample_record_edit(request, project_id):
    project_info = SampleRecord.objects.get(id=project_id)

    if request.method == 'POST':
        project_info_form = SampleRecordForm(request.POST, instance=project_info)
        if project_info_form.is_valid():
            # print(project_info_form.has_changed())
            change_list = project_info_form.changed_data
            project_info_form.save(commit=False)
            # 定义修改单位和送样终端
            if 'sample_sender' in change_list:
                sample_sender = project_info_form.cleaned_data.get("sample_sender")
                unit = sample_sender.unit
                if unit:
                    project_info.unit = unit.unit_name
                else:
                    project_info.unit = None
                terminal = sample_sender.leading_official
                if terminal:
                    project_info.terminal = terminal
                else:
                    project_info.terminal = None
            # 以下定义几个截止日期修改
            if 'project_type' in change_list or 'receive_date' in change_list:

                pro_type = ProjectType.objects.get(id=request.POST.get("project_type"))
                receive_date = project_info_form.cleaned_data.get("receive_date")
                # 同时修改启动截止日期
                start_days = pro_type.start_deadline
                if start_days:
                    project_info.start_deadline = receive_date + timedelta(days=start_days)
                # 定义预实验截至日期
                preexperiment_days = pro_type.pre_experiment_cycle
                if preexperiment_days:
                    project_info.preexperiment_deadline = receive_date + timedelta(days=preexperiment_days)
                # 定义前处理截至日期和下机截止日期
                pre_process_days = pro_type.pre_process_cycle
                if pre_process_days:
                    project_info.pretreat_deadline = receive_date + timedelta(days=pre_process_days)
                    project_info.test_deadline = receive_date + timedelta(days=pre_process_days + pro_type.test_cycle)
                else:
                    project_info.test_deadline = receive_date + timedelta(days=pro_type.test_cycle)
                # 定义项目截至日期
                project_info.pro_deadline = receive_date + timedelta(days=pro_type.total_cycle)

            project_info.save()
            project_info_form.save_m2m()  # 使用commit后要手动保存manytomany

            # 对另外添加的文件单独处理
            file_list = request.FILES.getlist('file_input')  # 获取上传的多个文件的列表
            file_obj = []
            for file in file_list:
                file_instance = FilesRelated.objects.create(file=file)
                file_obj.append(file_instance)
            for file in file_obj:
                project_info.files.add(file)
            msg = "edit_success"
            return render(request, 'project_stage/sample_record.html', {'msg': msg})
        else:
            project_info_form = SampleRecordForm(request.POST, request.FILES or None)
            msg = 'failed'
            return render(request, 'project_stage/sample_record_edit.html', {'form': project_info_form, 'msg': msg,
                                                                             'project_info': project_info})
    elif request.method == 'GET':
        project_form = SampleRecordForm(instance=project_info)
        return render(request, 'project_stage/sample_record_edit.html', {'form': project_form,
                                                                         'project_info': project_info})


@login_required()
def sample_record_del(request):
    # 定义删除项目功能函数
    if request.method == 'POST':

        ids = request.POST.get("ids")
        for project_id in json.loads(ids):
            project = SampleRecord.objects.get(id=project_id)
            project.delete()
        return HttpResponse("del_success")

    return HttpResponse("非POST请求！")


@login_required()
def view_sample_detail(request, pro_id):
    # 定义样本登记详情
    sample_record = SampleRecord.objects.get(id=pro_id)

    return render(request, 'project_stage/sample_record_detail.html', {'record': sample_record})


@login_required()
def pretreat_stage(request):
    # 定义前处理页面

    if request.method == 'GET':
        return render(request, 'project_stage/pretreat_stage.html')


def pretreat_stage_table(request):
    # 定义ajax方式获取列表数据
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
        date_now = date.today()    # 为后面计算周期做准备
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
            # 定义单位和负责人不存在的情况
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

            # 以下为前处理阶段新添加字段
            if project.start_date:
                start_date = project.start_date.strftime('%Y-%m-%d')
            else:
                start_date = "-"
            if project.preexperiment_finish_date:
                preexperiment_finish_date = project.preexperiment_finish_date.strftime('%Y-%m-%d')
            else:
                preexperiment_finish_date = "-"
            # 格式化前处理完成日期，同时计算前处理剩余周期
            if project.pretreat_finish_date:
                pretreat_finish_date = project.pretreat_finish_date.strftime('%Y-%m-%d')
                time_percent = "-"
            else:
                pretreat_finish_date = "-"
                if project.project_type.pre_process_cycle:
                    real_remain_time = project.pretreat_deadline - date_now
                    real_pretreat_cycle = project.pretreat_deadline - project.receive_date
                    time_percent = real_remain_time.days * 100 // real_pretreat_cycle.days
                else:
                    time_percent = "-"
            # 定义步骤一操作人
            first_all = project.first_operate_person.all()
            if first_all:
                if first_all.count() == 1:
                    first_operate_person = first_all[0].operate_person
                else:
                    first_operate_person = str(first_all.count()) + "名人员"
            else:
                first_operate_person = "-"
            # 定义步骤二操作人
            second_all = project.second_operate_person.all()
            if second_all:
                if second_all.count() == 1:
                    second_operate_person = second_all[0].operate_person
                else:
                    second_operate_person = str(second_all.count()) + "名人员"
            else:
                second_operate_person = "-"
            # 定义步骤三操作人
            third_all = project.third_operate_person.all()
            if third_all:
                if third_all.count() == 1:
                    third_operate_person = third_all[0].operate_person
                else:
                    third_operate_person = str(third_all.count()) + "名人员"
            else:
                third_operate_person = "-"
            # 定义步骤四操作人
            fourth_all = project.fourth_operate_person.all()
            if fourth_all:
                if fourth_all.count() == 1:
                    fourth_operate_person = fourth_all[0].operate_person
                else:
                    fourth_operate_person = str(fourth_all.count()) + "名人员"
            else:
                fourth_operate_person = "-"
            # 定义跑胶操作人
            person_all = project.page_person.all()
            if person_all:
                if person_all.count() == 1:
                    page_person = person_all[0].operate_person
                else:
                    page_person = str(person_all.count()) + "名人员"
            else:
                page_person = "-"
            # 定义剩余样本有无
            if project.sample_overplus is None:
                sample_overplus = "未知"
            elif project.sample_overplus:
                sample_overplus = "是"
            else:
                sample_overplus = "否"
            # sample_overplus_status为多对多，分情况显示
            status_all = project.sample_overplus_status.all()
            if status_all:
                if status_all.count() == 1:
                    sample_overplus_status = status_all[0].status_type
                else:
                    sample_overplus_status = str(status_all.count()) + "种状态"
            else:
                sample_overplus_status = "-"
            interrupt_type = project.project_interrupt
            if interrupt_type:
                project_interrupt = interrupt_type.interrupt_type
            else:
                project_interrupt = "-"
            if project.start_deadline:
                start_deadline = project.start_deadline.strftime('%Y-%m-%d')
            else:
                start_deadline = "-"
            if project.preexperiment_deadline:
                preexperiment_deadline = project.preexperiment_deadline.strftime('%Y-%m-%d')
            else:
                preexperiment_deadline = "-"
            if project.pretreat_deadline:
                pretreat_deadline = project.pretreat_deadline.strftime('%Y-%m-%d')
            else:
                pretreat_deadline = "-"

            response_data['rows'].append({

                "project_id": project.id,
                "project_num": project.project_num,
                "project_type": project_type,
                "sample_type": sample_type,
                "machine_time": machine_time,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": project.sample_sender.customer_name,
                # 以下为前处理阶段新添加字段
                "priority": project.priority,
                "start_date": start_date,
                "preexperiment_finish_date": preexperiment_finish_date,
                "pretreat_finish_date": pretreat_finish_date,
                "first_operate_person": first_operate_person,
                "second_operate_person": second_operate_person,
                "third_operate_person": third_operate_person,
                "fourth_operate_person": fourth_operate_person,
                "page_person": page_person,
                "sample_overplus": sample_overplus,
                "sample_overplus_status": sample_overplus_status,
                "project_interrupt": project_interrupt,
                "start_deadline": start_deadline,
                "preexperiment_deadline": preexperiment_deadline,
                "pretreat_deadline": pretreat_deadline,
                "time_percent": time_percent,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def pretreat_stage_edit(request, project_id):
    # 定义前处理信息修改功能
    project_info = SampleRecord.objects.get(id=project_id)

    if request.method == 'POST':
        project_info_form = PretreatStageForm(request.POST, instance=project_info)
        if project_info_form.is_valid():
            # change_list = project_info_form.changed_data
            project_info_form.save()

            msg = "edit_success"
            return render(request, 'project_stage/pretreat_stage.html', {'msg': msg})
        else:
            project_info_form = PretreatStageForm(request.POST)
            msg = 'failed'
            return render(request, 'project_stage/pretreat_stage_edit.html', {'form': project_info_form, 'msg': msg,
                                                                              'project_info': project_info})
    elif request.method == 'GET':
        project_form = PretreatStageForm(instance=project_info)
        return render(request, 'project_stage/pretreat_stage_edit.html', {'form': project_form,
                                                                          'project_info': project_info})


@login_required()
def view_pretreat_detail(request, pro_id):
    # 定义前处理详情
    sample_record = SampleRecord.objects.get(id=pro_id)

    return render(request, 'project_stage/pretreat_stage_detail.html', {'record': sample_record})


@login_required()
def test_analysis(request):
    # 定义检测分析列表页面

    return render(request, 'project_stage/test_analysis.html')


def test_analysis_table(request):
    # 定义检测分析表格数据

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
        date_now = date.today()  # 为后面计算剩余周期需要
        for project in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，
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
            # 定义单位和负责人不存在的情况
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

            # 以下为检测分析阶段新添加字段
            if project.instrument_type:
                instrument_type = project.instrument_type.instrument
            else:
                instrument_type = "-"
            # 以下为两个截止日期
            test_deadline = project.test_deadline.strftime('%Y-%m-%d')
            pro_deadline = project.pro_deadline.strftime('%Y-%m-%d')
            # 以下为4个时间节点
            if project.date_test:
                date_test = project.date_test.strftime('%Y-%m-%d')
            else:
                date_test = "-"
            if project.date_searchlib:
                date_searchlib = project.date_searchlib.strftime('%Y-%m-%d')
            else:
                date_searchlib = "-"
            # 定义报告发送日期，同时处理项目剩余周期
            if project.date_send_report:
                date_send_report = project.date_send_report.strftime('%Y-%m-%d')
                time_percent = "-"
            else:
                date_send_report = "-"
                real_remain_time = project.pro_deadline - date_now
                real_period = project.pro_deadline - project.receive_date
                time_percent = real_remain_time.days * 100 // real_period.days
            if project.date_send_rawdata:
                date_send_rawdata = project.date_send_rawdata.strftime('%Y-%m-%d')
            else:
                date_send_rawdata = "-"

            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                "project_type": project_type,
                "sample_type": sample_type,
                "machine_time": machine_time,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": project.sample_sender.customer_name,
                # 以下为检测分析阶段新添加字段
                "priority": project.priority,
                "instrument_type": instrument_type,
                "date_test": date_test,
                "date_searchlib": date_searchlib,
                "date_send_report": date_send_report,
                "date_send_rawdata": date_send_rawdata,
                "test_deadline": test_deadline,
                "pro_deadline": pro_deadline,
                "time_percent": time_percent,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def test_analysis_edit(request, project_id):
    # 定义检测分析修改功能
    project_info = SampleRecord.objects.get(id=project_id)

    if request.method == 'POST':
        project_info_form = TestAnalysisForm(request.POST, instance=project_info)
        if project_info_form.is_valid():
            change_list = project_info_form.changed_data
            project_info_form.save(commit=False)
            if "pro_deadline" in change_list:
                # 计算实际周期占比
                receive_date = project_info.receive_date
                pro_deadline = project_info_form.cleaned_data.get('pro_deadline')
                real_pro_cycle = pro_deadline - receive_date
                real_in_theory = round(real_pro_cycle.days / project_info.project_type.total_cycle, 2)  # 实际周期占比
                # 修改实际前处理截止日期和下机截止日期
                pre_process_cycle = project_info.project_type.pre_process_cycle
                test_cycle = project_info.project_type.test_cycle
                real_test_period = int(test_cycle * real_in_theory)  # 实际检测周期
                if pre_process_cycle:
                    real_pre_period = int(pre_process_cycle * real_in_theory)  # 实际前处理周期
                    project_info.pretreat_deadline = receive_date + timedelta(days=real_pre_period)
                    project_info.test_deadline = receive_date + timedelta(days=real_pre_period + real_test_period)
                else:
                    project_info.test_deadline = receive_date + timedelta(days=real_test_period)
                # 修改实际预实验截止日期
                pre_experiment_cycle = project_info.project_type.pre_experiment_cycle
                if pre_experiment_cycle:
                    real_preexperiment_period = int(pre_experiment_cycle * real_in_theory)  # 实际预实验周期
                    project_info.preexperiment_deadline = receive_date + timedelta(days=real_preexperiment_period)
                # 修改实际启动截止日期
                start_cycle = project_info.project_type.start_deadline
                if start_cycle:
                    real_start_period = int(start_cycle * real_in_theory)  # 实际预实验周期
                    project_info.start_deadline = receive_date + timedelta(days=real_start_period)

            project_info.save()
            project_info_form.save_m2m()
            msg = "edit_success"
            return render(request, 'project_stage/test_analysis.html', {'msg': msg})
        else:
            project_info_form = TestAnalysisForm(request.POST)
            msg = 'failed'
            return render(request, 'project_stage/test_analysis_edit.html', {'form': project_info_form, 'msg': msg,
                                                                             'project_info': project_info})
    elif request.method == 'GET':
        project_form = TestAnalysisForm(instance=project_info)
        return render(request, 'project_stage/test_analysis_edit.html', {'form': project_form,
                                                                         'project_info': project_info})


@login_required()
def test_analysis_detail(request, pro_id):
    # 定义前处理详情
    sample_record = SampleRecord.objects.get(id=pro_id)

    return render(request, 'project_stage/test_analysis_detail.html', {'record': sample_record})
