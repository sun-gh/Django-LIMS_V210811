from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SampleRecord, FilesRelated, ProjectType, SampleType, MachineTime
from .forms import SampleRecordForm, PretreatStageForm, TestStageForm, AnalysisStageForm, EditAnalysisForm, SearchForm
from django.core.paginator import Paginator
from django.http import HttpResponse
import json
from datetime import date, datetime
import django.dispatch
from django.dispatch import receiver
from customer.views import customer_edit, project_add_unit, project_add_terminal
import chinese_calendar
from guardian.shortcuts import get_objects_for_user


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
    sample_records = SampleRecord.objects.filter(sample_sender__id=kwargs['customer_id'])
    for record in sample_records:
        if record.terminal is None:
            record.terminal = kwargs['terminal_name']
            record.save()

    return sample_records


@login_required()
def sample_record(request, msg="normal_show"):
    # 定义样本登记页面
    if request.method == 'GET':
        search_form = SearchForm()

        return render(request, 'project_stage/sample_record.html', {'form': search_form, 'msg': msg})


def sample_record_table(request):
    # 定义样本登记列表数据
    if request.method == 'GET':
        projects_get_perm = get_objects_for_user(request.user, 'project_stage.view_samplerecord')

        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        project_num = request.GET.get('project_num')
        unit_name = request.GET.get('unit')
        sample_sender = request.GET.get('sample_sender')
        note = request.GET.get('note')
        pro_type_id = int(request.GET.get('pro_type_id'))
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        conditions = {}  # 构造字典存储查询条件
        if project_num:
            conditions['project_num__contains'] = project_num
        if unit_name:
            conditions['unit__contains'] = unit_name
        if sample_sender:
            conditions['sample_sender__customer_name__contains'] = sample_sender
        if note:
            conditions['note__contains'] = note
        if pro_type_id:
            conditions['project_type__id'] = pro_type_id
        if start_time and end_time:
            fmt = '%Y-%m-%d'
            start_time = datetime.strptime(start_time, fmt)
            end_time = datetime.strptime(end_time, fmt)
            conditions['receive_time__range'] = (start_time, end_time)

        # all_projects = SampleRecord.objects.filter(**conditions)
        all_projects = projects_get_perm.filter(**conditions)
        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

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
            # 定义代理ID
            agent_num = project.agent_id
            if agent_num:
                agent_id = agent_num
            else:
                agent_id = "-"
            # 定义防伪编号
            anti_fake_number = project.anti_fake_number
            if anti_fake_number:
                anti_fake_number = anti_fake_number
            else:
                anti_fake_number = "-"
            # 定义样本质量
            quality = project.sample_quality
            if quality:
                sample_quality = quality.quality_type
                message_template = quality.message_template
            else:
                sample_quality = "-"
                message_template = "-"
            # addition_item为多对多，显示分多种情况
            all_item = project.addition_item.all()
            if all_item:
                if all_item.count() == 1:
                    addition_item = all_item[0].item_type
                else:
                    addition_item = str(all_item.count()) + "个附加项"
            else:
                addition_item = "-"
            technical_support = project.responsible_person
            if technical_support:
                responsible_person = technical_support.name
            else:
                responsible_person = "-"
            # 定义备注
            if project.note:
                note = project.note
            else:
                note = "-"
            # 要将datetime对象转化为字符串，才能进行json转换
            receive_time = project.receive_time.strftime('%Y-%m-%d %H:%M')
            # 定义文件显示
            files = project.files.all()
            if files:
                if files.count() == 1:
                    file_display = files[0].file.name[14:]
                else:
                    file_display = files.count()
            else:
                file_display = ""

            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                # "status": project.get_status_display(),
                "project_type": project_type,
                "sample_type": project.sample_type,
                "machine_time": machine_time,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": project.sample_sender.customer_name,
                "agent_id": agent_id,
                "anti_fake_number": anti_fake_number,
                "sample_quality": sample_quality,
                "message_template": message_template,
                "addition_item": addition_item,
                "receive_time": receive_time,
                # "pro_start_date": pro_start_date,
                "responsible_person": responsible_person,
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
        sample_rec_form = SampleRecordForm(request.POST, instance=sample_rec)
        if sample_rec_form.is_valid():
            change_list = sample_rec_form.changed_data
            sample_rec_form.save(commit=False)
            # 定义项目号
            date_today = date.today()
            pro_today = SampleRecord.objects.filter(c_time__contains=date_today).order_by('-c_time')
            if pro_today:
                project_num = int(pro_today[0].project_num) + 1
            else:
                project_num = date_today.strftime('%y%m%d') + '01'
            sample_rec.project_num = project_num
            # 定义样本类型
            sample_type = sample_rec_form.cleaned_data.get("sample_type")
            sample_rec.sample_type = sample_type.type_name
            # 定义机时类型
            machine_time = sample_rec_form.cleaned_data.get("machine_time")
            if machine_time:
                sample_rec.machine_time = machine_time.time_type
            # 定义单位和送样终端
            sample_sender = sample_rec_form.cleaned_data.get("sample_sender")
            unit = sample_sender.unit
            if unit:
                sample_rec.unit = unit.unit_name
            terminal = sample_sender.leading_official
            if terminal:
                sample_rec.terminal = terminal
            if 'pro_start_date' in change_list:
                pro_start_date = sample_rec_form.cleaned_data.get("pro_start_date")
                pro_type = ProjectType.objects.get(id=request.POST.get("project_type"))
                # 定义启动截至日期
                start_days = pro_type.start_deadline
                if start_days:
                    sample_rec.start_deadline = chinese_calendar.find_workday(start_days, pro_start_date)
                # 定义预实验截至日期
                preexperiment_days = pro_type.pre_experiment_cycle
                if preexperiment_days:
                    sample_rec.preexperiment_deadline = chinese_calendar.find_workday(preexperiment_days, pro_start_date)
                # 定义前处理截止日期和下机截止日期
                pre_process_days = pro_type.pre_process_cycle
                test_days = pro_type.test_cycle
                if pre_process_days:
                    # 有前处理，肯定有上机检测(暂不考虑只做前处理的项目！！！)
                    sample_rec.pretreat_deadline = chinese_calendar.find_workday(pre_process_days, pro_start_date)
                    sample_rec.test_deadline = chinese_calendar.find_workday(pre_process_days+test_days, pro_start_date)
                elif not pre_process_days and test_days:
                    # 没有前处理，但可能有上机检测（两者周期关系还有：无前处理，无上机检测——数据分析；此时不用处理截止日期）
                    sample_rec.test_deadline = chinese_calendar.find_workday(test_days, pro_start_date)
                # 定义项目截至日期
                sample_rec.pro_deadline = chinese_calendar.find_workday(pro_type.total_cycle, pro_start_date)

            sample_rec.save()
            sample_rec_form.save_m2m()   # 使用commit后要手动保存manytomany

            msg = "add_success"
            # 发送一个信号
            anti_fake_number = sample_rec_form.cleaned_data.get("anti_fake_number")
            add_success.send(sample_record_add, msg=msg, sample_rec_id=sample_rec.id, anti_fake_number=anti_fake_number)
            return redirect('project_stage:sample_record', msg)
        else:
            form = SampleRecordForm(request.POST)
            msg = "info_error"
            return render(request, "project_stage/sample_record_add.html", {'form': form, 'msg': msg})


# 定义一个信号
edit_success = django.dispatch.Signal()


@login_required()
def sample_record_edit(request, project_id):
    # 定义样本登记编辑函数
    project_info = SampleRecord.objects.get(id=project_id)
    if request.method == 'POST':
        original_pro_start_date = project_info.pro_start_date
        old_anti_fake_number = project_info.anti_fake_number
        project_info_form = SampleRecordForm(request.POST, instance=project_info)
        if project_info_form.is_valid():
            change_list = project_info_form.changed_data
            project_info_form.save(commit=False)
            # 定义样本类型修改
            sample_type = project_info_form.cleaned_data.get("sample_type")
            project_info.sample_type = sample_type.type_name
            # 定义机时类型修改
            machine_time = project_info_form.cleaned_data.get("machine_time")
            if machine_time:
                project_info.machine_time = machine_time.time_type
            else:
                project_info.machine_time = None
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
            # 以下定义几个截止日期修改(周期以项目启动时间作为起点；时间节点变更条件：“项目类型”或“项目启动时间”发生变化；)
            if 'pro_start_date' in change_list or 'project_type' in change_list:
                pro_start_date = project_info_form.cleaned_data.get("pro_start_date")
                if pro_start_date:
                    pro_type = ProjectType.objects.get(id=request.POST.get("project_type"))
                    # 同时修改启动截止日期
                    start_days = pro_type.start_deadline
                    if start_days:
                        project_info.start_deadline = chinese_calendar.find_workday(start_days, pro_start_date)
                    else:
                        project_info.start_deadline = None
                    # 定义预实验截至日期
                    preexperiment_days = pro_type.pre_experiment_cycle
                    if preexperiment_days:
                        project_info.preexperiment_deadline = chinese_calendar.find_workday(preexperiment_days, pro_start_date)
                    else:
                        project_info.preexperiment_deadline = None
                    # 定义前处理截至日期和下机截止日期
                    pre_process_days = pro_type.pre_process_cycle
                    test_days = pro_type.test_cycle
                    if pre_process_days:  # 暂不考虑只做前处理的项目；
                        project_info.pretreat_deadline = chinese_calendar.find_workday(pre_process_days, pro_start_date)
                        project_info.test_deadline = chinese_calendar.find_workday(pre_process_days+pro_type.test_cycle, pro_start_date)
                    elif not pre_process_days and test_days:
                        project_info.pretreat_deadline = None  # 可能“启动时间”和“项目类型”同时修改；
                        project_info.test_deadline = chinese_calendar.find_workday(pro_type.test_cycle, pro_start_date)
                    # 定义项目截至日期
                    project_info.pro_deadline = chinese_calendar.find_workday(pro_type.total_cycle, pro_start_date)
                elif not pro_start_date and original_pro_start_date:  # 把项目启动时间置空；
                    project_info.start_deadline = None
                    project_info.preexperiment_deadline = None
                    project_info.pretreat_deadline = None
                    project_info.test_deadline = None
                    project_info.pro_deadline = None

            project_info.save()
            project_info_form.save_m2m()  # 使用commit后要手动保存manytomany
            msg = "edit_success"
            # 定义防伪编号修改联动项目结算中结算类型修改
            if 'anti_fake_number' in change_list:
                anti_fake_number = project_info_form.cleaned_data.get("anti_fake_number")
                if not (anti_fake_number and old_anti_fake_number):  # 两者只有一个存在的时候，才需要修改
                    edit_success.send(sample_record_edit, msg=msg, project_id=project_id, anti_fake_number=anti_fake_number)
            return redirect('project_stage:sample_record', msg)
        else:
            project_info_form = SampleRecordForm(request.POST)
            msg = 'failed'
            return render(request, 'project_stage/sample_record_edit.html', {'form': project_info_form, 'msg': msg,
                                                                             'project_info': project_info})
    elif request.method == 'GET':
        sample_type = SampleType.objects.get(type_name=project_info.sample_type)
        machine_time = MachineTime.objects.filter(time_type=project_info.machine_time)
        if machine_time:
            project_form = SampleRecordForm(initial={'sample_type': sample_type, 'machine_time': machine_time[0]},
                                            instance=project_info)
        else:
            project_form = SampleRecordForm(initial={'sample_type': sample_type}, instance=project_info)
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
def pretreat_stage(request, msg="normal_show"):
    # 定义前处理页面
    if request.method == 'GET':
        search_form = SearchForm()

        return render(request, 'project_stage/pretreat_stage.html', {'form': search_form, 'msg': msg})


def pretreat_stage_table(request):
    # 定义前处理列表数据
    if request.method == 'GET':
        projects_get_perm = get_objects_for_user(request.user, 'project_stage.view_samplerecord')
        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        project_num = request.GET.get('project_num')
        unit_name = request.GET.get('unit')
        sample_sender = request.GET.get('sample_sender')
        pro_type_id = int(request.GET.get('pro_type_id'))
        sample_type_id = request.GET.get('sample_type_id')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        conditions = {}  # 构造字典存储查询条件
        if project_num:
            conditions['project_num__contains'] = project_num
        if unit_name:
            conditions['unit__contains'] = unit_name
        if sample_sender:
            conditions['sample_sender__customer_name__contains'] = sample_sender
        if pro_type_id:
            conditions['project_type__id'] = pro_type_id
        if sample_type_id:
            sample_type = SampleType.objects.get(id=int(sample_type_id))
            conditions['sample_type'] = sample_type.type_name
        if start_time and end_time:
            fmt = '%Y-%m-%d'
            start_time = datetime.strptime(start_time, fmt)
            end_time = datetime.strptime(end_time, fmt)
            conditions['receive_time__range'] = (start_time, end_time)
        # if conditions:
        #     # 查找全部数据 ()
        # else:
        #     # 默认显示这个阶段的数据
        # test_pro = SampleRecord.objects.filter(priority__range=(1, 20))
        # all_projects = SampleRecord.objects.filter(**conditions)
        all_projects = projects_get_perm.filter(**conditions)
        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

        response_data = {'total': all_projects_count, 'rows': []}  # 必须带有rows和total这2个key
        date_now = datetime.now()    # 为后面计算周期做准备
        for project in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致.
            if project.project_type:
                project_type = project.project_type.project_name
            else:
                project_type = "-"
            # 定义机时类型为空的情况
            if project.machine_time:
                machine_time = project.machine_time
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
            technical_support = project.responsible_person
            if technical_support:
                responsible_person = technical_support.name
            else:
                responsible_person = "-"
            # 定义项目启动日期
            pro_start_date = project.pro_start_date
            if pro_start_date:
                project_start_date = pro_start_date.strftime('%Y-%m-%d %H:%M')
            else:
                project_start_date = "-"
            if project.start_date:
                start_date = project.start_date.strftime('%Y-%m-%d %H:%M')
            else:
                start_date = "-"
            if project.preexperiment_finish_date:
                preexperiment_finish_date = project.preexperiment_finish_date.strftime('%Y-%m-%d %H:%M')
            else:
                preexperiment_finish_date = "-"
            # 格式化前处理完成日期，同时计算前处理剩余周期
            if project.pretreat_finish_date:
                pretreat_finish_date = project.pretreat_finish_date.strftime('%Y-%m-%d %H:%M')
                time_percent = "-"
            else:
                pretreat_finish_date = "-"
                pro_start_date = project.pro_start_date
                if project.project_type.pre_process_cycle and pro_start_date:
                    real_pretreat_cycle = chinese_calendar.get_workdays(pro_start_date, project.pretreat_deadline)
                    if date_now == project.pretreat_deadline:
                        time_percent = 0
                    elif date_now < project.pretreat_deadline:
                        remain_time = chinese_calendar.get_workdays(date_now, project.pretreat_deadline)
                        time_percent = len(remain_time) * 100 // len(real_pretreat_cycle)
                    else:
                        remain_time = chinese_calendar.get_workdays(project.pretreat_deadline, date_now)
                        time_percent = -len(remain_time) * 100 // len(real_pretreat_cycle)
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
                start_deadline = project.start_deadline.strftime('%Y-%m-%d %H:%M')
            else:
                start_deadline = "-"
            if project.preexperiment_deadline:
                preexperiment_deadline = project.preexperiment_deadline.strftime('%Y-%m-%d %H:%M')
            else:
                preexperiment_deadline = "-"
            if project.pretreat_deadline:
                pretreat_deadline = project.pretreat_deadline.strftime('%Y-%m-%d %H:%M')
            else:
                pretreat_deadline = "-"

            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                "project_type": project_type,
                "sample_type": project.sample_type,
                "machine_time": machine_time,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": project.sample_sender.customer_name,
                # 以下为前处理阶段新添加字段
                "priority": project.priority,
                "responsible_person": responsible_person,
                "pro_start_date": project_start_date,
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
            project_info_form.save()
            msg = "edit_success"
            return redirect('project_stage:pretreat_stage', msg)
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
def test_stage(request, msg="normal_show"):
    # 定义质谱检测页面
    if request.method == 'GET':
        search_form = SearchForm()

        return render(request, 'project_stage/test_stage.html', {'form': search_form, 'msg': msg})


def test_stage_table(request):
    # 定义质谱检测表格数据
    if request.method == 'GET':
        projects_get_perm = get_objects_for_user(request.user, 'project_stage.view_samplerecord')
        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        project_num = request.GET.get('project_num')
        unit_name = request.GET.get('unit')
        sample_sender = request.GET.get('sample_sender')
        pro_type_id = int(request.GET.get('pro_type_id'))
        sample_type_id = request.GET.get('sample_type_id')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        conditions = {}  # 构造字典存储查询条件
        if project_num:
            conditions['project_num__contains'] = project_num
        if unit_name:
            conditions['unit__contains'] = unit_name
        if sample_sender:
            conditions['sample_sender__customer_name__contains'] = sample_sender
        if pro_type_id:
            conditions['project_type__id'] = pro_type_id
        if sample_type_id:
            sample_type = SampleType.objects.get(id=int(sample_type_id))
            conditions['sample_type'] = sample_type.type_name
        if start_time and end_time:
            fmt = '%Y-%m-%d'
            start_time = datetime.strptime(start_time, fmt)
            end_time = datetime.strptime(end_time, fmt)
            conditions['receive_time__range'] = (start_time, end_time)

        # all_projects = SampleRecord.objects.filter(**conditions)
        all_projects = projects_get_perm.filter(**conditions)
        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

        response_data = {'total': all_projects_count, 'rows': []}  # 必须带有rows和total这2个key
        date_now = datetime.now()  # 为后面计算剩余周期需要
        for project in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，
            if project.project_type:
                project_type = project.project_type.project_name
            else:
                project_type = "-"
            # 定义机时类型为空的情况
            if project.machine_time:
                machine_time = project.machine_time
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
            # 以下为质谱检测阶段新添加字段
            # 项目负责人
            technical_support = project.responsible_person
            if technical_support:
                responsible_person = technical_support.name
            else:
                responsible_person = "-"
            # 定义检测仪器
            if project.instrument_type:
                instrument_type = project.instrument_type.instrument
            else:
                instrument_type = "-"
            # 上机日期
            if project.date_test:
                date_test = project.date_test.strftime('%Y-%m-%d %H:%M')
            else:
                date_test = "-"
            # 下机日期
            if project.test_finish_date:
                test_finish_date = project.test_finish_date.strftime('%Y-%m-%d %H:%M')
            else:
                test_finish_date = "-"
            # 下机截止日期（同时定义剩余周期）
            if project.test_deadline:  # 此时有两种情况：1、检测阶段已完成；2、检测阶段未完成；
                editable = True  # 用于该条目能否被修改
                test_deadline = project.test_deadline.strftime('%Y-%m-%d %H:%M')
                if project.test_finish_date:  # 此时已下机
                    time_percent = "-"
                else:  # 此时未下机
                    pro_start_date = project.pro_start_date
                    real_test_cycle = chinese_calendar.get_workdays(pro_start_date, project.test_deadline)
                    if date_now == project.test_deadline:
                        time_percent = 0
                    elif date_now < project.test_deadline:
                        remain_time = chinese_calendar.get_workdays(date_now, project.test_deadline)
                        time_percent = len(remain_time) * 100 // len(real_test_cycle)
                    else:
                        remain_time = chinese_calendar.get_workdays(project.test_deadline, date_now)
                        time_percent = -len(remain_time) * 100 // len(real_test_cycle)
            else:  # 此时有两种情况：1、该项目无检测阶段；2、项目未启动；此时无需计算剩余周期
                test_deadline = "-"
                time_percent = "-"
                editable = False

            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                "project_type": project_type,
                "sample_type": project.sample_type,
                "machine_time": machine_time,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": project.sample_sender.customer_name,
                "editable": editable,
                # 以下为检测分析阶段新添加字段
                "priority": project.priority,
                "responsible_person": responsible_person,
                "instrument_type": instrument_type,
                "date_test": date_test,
                "test_finish_date": test_finish_date,   # 新添加字段
                "test_deadline": test_deadline,
                "time_percent": time_percent,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def test_stage_edit(request, pro_id):
    # 定义检测阶段编辑功能
    pro_test = SampleRecord.objects.get(id=pro_id)
    if request.method == 'POST':
        pro_test_form = TestStageForm(request.POST, instance=pro_test)
        if pro_test_form.is_valid():
            pro_test_form.save()
            msg = "edit_success"
            return redirect('project_stage:test_stage', msg)
        else:
            msg = "failed"
            pro_test_form = TestStageForm(request.POST)
            return render(request, 'project_stage/test_stage_edit.html', {'form': pro_test_form, 'pro_test': pro_test, 'msg': msg})
    elif request.method == 'GET':
        pro_test_form = TestStageForm(instance=pro_test)
        return render(request, 'project_stage/test_stage_edit.html', {'form': pro_test_form, 'pro_test': pro_test})


@login_required()
def test_stage_detail(request, pro_id):
    # 定义质谱检测详情页
    test_detail = SampleRecord.objects.get(id=pro_id)

    return render(request, 'project_stage/test_stage_detail.html', {'record': test_detail})


@login_required()
def analysis_stage(request, msg="normal_show"):
    # 定义数据分析列表页面
    if request.method == 'GET':
        search_form = SearchForm()

        return render(request, 'project_stage/analysis_stage.html', {'form': search_form, 'msg': msg})


def analysis_stage_table(request):
    # 定义数据分析表格数据
    if request.method == 'GET':
        projects_get_perm = get_objects_for_user(request.user, 'project_stage.view_samplerecord')
        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        project_num = request.GET.get('project_num')
        unit_name = request.GET.get('unit')
        sample_sender = request.GET.get('sample_sender')
        note = request.GET.get('note')
        pro_type_id = int(request.GET.get('pro_type_id'))
        start_time1 = request.GET.get('start_time1')
        end_time1 = request.GET.get('end_time1')
        start_time2 = request.GET.get('start_time2')
        end_time2 = request.GET.get('end_time2')

        conditions = {}  # 构造字典存储查询条件
        if project_num:
            conditions['project_num__contains'] = project_num
        if unit_name:
            conditions['unit__contains'] = unit_name
        if sample_sender:
            conditions['sample_sender__customer_name__contains'] = sample_sender
        if note:
            conditions['note__contains'] = note
        if pro_type_id:
            conditions['project_type__id'] = pro_type_id
        # 定义收样时间筛选
        if start_time1 and end_time1:
            fmt = '%Y-%m-%d'
            start_time1 = datetime.strptime(start_time1, fmt)
            end_time1 = datetime.strptime(end_time1, fmt)
            conditions['receive_time__range'] = (start_time1, end_time1)
        # 定义报告发送时间筛选
        if start_time2 and end_time2:
            fmt = '%Y-%m-%d'
            start_time2 = datetime.strptime(start_time2, fmt)
            end_time2 = datetime.strptime(end_time2, fmt)
            conditions['date_send_report__range'] = (start_time2, end_time2)

        # all_projects = SampleRecord.objects.filter(**conditions)
        all_projects = projects_get_perm.filter(**conditions)
        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

        response_data = {'total': all_projects_count, 'rows': []}  # 必须带有rows和total这2个key
        date_now = datetime.now()  # 为后面计算剩余周期需要
        for project in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，
            if project.project_type:
                project_type = project.project_type.project_name
            else:
                project_type = "-"
            # 定义机时类型为空的情况
            if project.machine_time:
                machine_time = project.machine_time
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
            # 定义备注
            if project.note:
                note = project.note
            else:
                note = "-"
            # 以下为数据分析阶段新添加字段
            # 定义项目来源
            project_source = project.projectorder.get_project_source_display()
            # 定义客户来源
            customer_source = project.projectorder.customer_source
            if customer_source:
                customer_source_choice = project.projectorder.get_customer_source_display()
            else:
                customer_source_choice = "-"
            # 定义文件显示
            files = project.files.all()
            if files:
                if files.count() == 1:
                    file_display = files[0].file.name[14:]
                else:
                    file_display = files.count()
            else:
                file_display = ""
            if project.instrument_type:
                instrument_type = project.instrument_type.instrument
            else:
                instrument_type = "-"
            # 项目截止日期
            if project.pro_deadline:
                pro_deadline = project.pro_deadline.strftime('%Y-%m-%d %H:%M')
                item_editable = True  # 定义item是否可编辑
            else:
                pro_deadline = "-"
                item_editable = False
            # 项目负责人
            technical_support = project.responsible_person
            if technical_support:
                responsible_person = technical_support.name
            else:
                responsible_person = "-"
            if project.date_searchlib:
                date_searchlib = project.date_searchlib.strftime('%Y-%m-%d %H:%M')
            else:
                date_searchlib = "-"
            # 定义报告发送日期，同时处理项目剩余周期
            if project.date_send_report:
                date_send_report = project.date_send_report.strftime('%Y-%m-%d %H:%M')
                time_percent = "-"
            else:
                date_send_report = "-"
                pro_start_date = project.pro_start_date
                if pro_start_date:
                    real_period = chinese_calendar.get_workdays(pro_start_date, project.pro_deadline)
                    if date_now == project.pro_deadline:
                        time_percent = 0
                    elif date_now < project.pro_deadline:
                        remain_time = chinese_calendar.get_workdays(date_now, project.pro_deadline)
                        time_percent = len(remain_time) * 100 // len(real_period)
                    else:
                        remain_time = chinese_calendar.get_workdays(project.pro_deadline, date_now)
                        time_percent = -len(remain_time) * 100 // len(real_period)
                else:
                    # item_editable = False
                    time_percent = "-"
            if project.date_send_rawdata:
                date_send_rawdata = project.date_send_rawdata.strftime('%Y-%m-%d %H:%M')
            else:
                date_send_rawdata = "-"

            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                "project_type": project_type,
                "sample_type": project.sample_type,
                "machine_time": machine_time,
                "sample_amount": project.sample_amount,
                "leading_official": leading_official,
                "unit": unit_name,
                "sample_sender": project.sample_sender.customer_name,
                "note": note,
                # 以下为检测分析阶段新添加字段
                "priority": project.priority,
                "project_source": project_source,
                "customer_source": customer_source_choice,
                "files": file_display,
                "instrument_type": instrument_type,
                "responsible_person": responsible_person,
                "date_searchlib": date_searchlib,
                "date_send_report": date_send_report,
                "editable": item_editable,
                "date_send_rawdata": date_send_rawdata,
                "pro_deadline": pro_deadline,
                "time_percent": time_percent,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def analysis_stage_edit(request, project_id):
    # 定义数据分析修改功能
    project_info = SampleRecord.objects.get(id=project_id)
    if request.method == 'POST':
        project_info_form = AnalysisStageForm(request.POST, instance=project_info)
        if project_info_form.is_valid():
            change_list = project_info_form.changed_data
            project_info_form.save(commit=False)
            if "pro_deadline" in change_list:
                # 计算实际周期占比(此处只能修改项目截止日期，不能添加项目截止日期；在页面通过js实现；)
                pro_start_date = project_info.pro_start_date
                pro_deadline = project_info_form.cleaned_data.get('pro_deadline')
                real_pro_cycle = chinese_calendar.get_workdays(pro_start_date, pro_deadline)
                real_in_theory = round(len(real_pro_cycle) / project_info.project_type.total_cycle, 2)
                # 修改实际实验开始截止日期
                start_cycle = project_info.project_type.start_deadline
                if start_cycle:
                    real_start_period = int(start_cycle * real_in_theory)  # 实际实验开始周期
                    project_info.start_deadline = chinese_calendar.find_workday(real_start_period, pro_start_date)
                # 修改实际预实验截止日期
                pre_experiment_cycle = project_info.project_type.pre_experiment_cycle
                if pre_experiment_cycle:
                    real_preexperiment_period = int(pre_experiment_cycle * real_in_theory)  # 实际预实验周期
                    project_info.preexperiment_deadline = chinese_calendar.find_workday(real_preexperiment_period,
                                                                                        pro_start_date)
                # 修改实际前处理截止日期和下机截止日期
                pre_process_cycle = project_info.project_type.pre_process_cycle
                test_cycle = project_info.project_type.test_cycle
                real_test_period = int(test_cycle * real_in_theory)  # 实际检测周期
                if pre_process_cycle:
                    real_pre_period = int(pre_process_cycle * real_in_theory)  # 实际前处理周期
                    project_info.pretreat_deadline = chinese_calendar.find_workday(real_pre_period, pro_start_date)
                    project_info.test_deadline = chinese_calendar.find_workday(real_pre_period+real_test_period, pro_start_date)
                elif not pre_process_cycle and test_cycle:
                    project_info.test_deadline = chinese_calendar.find_workday(real_test_period, pro_start_date)

            project_info.save()
            project_info_form.save_m2m()
            msg = "edit_success"
            return redirect('project_stage:analysis_stage', msg)
        else:
            project_info_form = AnalysisStageForm(request.POST)
            msg = 'failed'
            return render(request, 'project_stage/analysis_stage_edit.html', {'form': project_info_form, 'msg': msg,
                                                                              'project_info': project_info})
    elif request.method == 'GET':
        project_form = AnalysisStageForm(instance=project_info)
        return render(request, 'project_stage/analysis_stage_edit.html', {'form': project_form,
                                                                          'project_info': project_info})


@login_required()
def analysis_stage_detail(request, pro_id):
    # 定义数据分析详情页
    sample_record = SampleRecord.objects.get(id=pro_id)

    return render(request, 'project_stage/analysis_stage_detail.html', {'record': sample_record})


@login_required()
def edit_analysis_info(request, pro_id):
    # 定义项目相关文件等信息修改（销售专用）
    project_info = SampleRecord.objects.get(id=pro_id)
    if request.method == 'POST':
        project_info_form = EditAnalysisForm(request.POST, instance=project_info)
        if project_info_form.is_valid():
            project_info_form.save()
            # 对另外添加的文件单独处理
            file_list = request.FILES.getlist('file_input')  # 获取上传的多个文件的列表
            file_obj = []
            for file in file_list:
                file_instance = FilesRelated.objects.create(file=file)
                file_obj.append(file_instance)
            for file in file_obj:
                project_info.files.add(file)
            msg = "edit_success"
            return redirect('project_stage:analysis_stage', msg)
        else:
            project_info_form = EditAnalysisForm(request.POST, request.FILES or None)
            msg = 'failed'
            return render(request, 'project_stage/edit_analysis_info.html', {'form': project_info_form, 'msg': msg,
                                                                             'project_info': project_info})
    elif request.method == 'GET':
        project_form = EditAnalysisForm(instance=project_info)
        return render(request, 'project_stage/edit_analysis_info.html', {'form': project_form,
                                                                         'project_info': project_info})
