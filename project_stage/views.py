from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SampleRecord, FilesRelated, ProjectType, SampleType, MachineTime, SpeciesInfo
from .forms import SampleRecordForm, PretreatStageForm, TestStageForm, AnalysisStageForm, EditAnalysisForm, SearchForm,\
    SpeciesInfoForm
from django.core.paginator import Paginator
from django.http import HttpResponse
import json
from django.db.models import Q
from datetime import date, datetime, time
import django.dispatch
from django.dispatch import receiver
from customer.views import customer_edit, project_add_unit, project_add_terminal
from chinese_calendar import get_workdays, find_workday
from guardian.shortcuts import get_objects_for_user


# 定义样本登记中单位信息修改
@receiver(project_add_unit, sender=customer_edit)
def edit_project_unit(sender, **kwargs):

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
        search_form.fields['status'].widget.choices = ((0, "--------"),)+SampleRecord.status_choices

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
        pro_status = int(request.GET.get('pro_status'))

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
        if pro_status:
            conditions['status'] = pro_status

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
            # 定义项目剩余周期
            pro_remain_days = project.pro_cyc_remain_days
            if pro_remain_days is not None:
                pro_cyc_remain_days = pro_remain_days
            else:
                pro_cyc_remain_days = "-"
            pro_remain_percent = project.pro_cyc_remain_percent
            if pro_remain_percent is not None:
                pro_cyc_remain_percent = pro_remain_percent
            else:
                pro_cyc_remain_percent = "-"

            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                "status": project.get_status_display(),
                "status_code": project.status,
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
                "pro_cyc_remain_days": pro_cyc_remain_days,
                "pro_cyc_remain_percent": pro_cyc_remain_percent,
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
                pro_start_date = sample_rec_form.cleaned_data.get("pro_start_date").date()
                pro_start_time = sample_rec_form.cleaned_data.get("pro_start_date").time()
                pro_type = ProjectType.objects.get(id=request.POST.get("project_type"))
                # 定义启动截至日期
                start_days = pro_type.start_deadline
                if start_days:
                    sample_rec.start_deadline = datetime.combine(find_workday(start_days, pro_start_date),pro_start_time)
                # 定义样本质控截至日期
                preexperiment_days = pro_type.pre_experiment_cycle
                pre_process_days = pro_type.pre_process_cycle
                test_days = pro_type.test_cycle
                if preexperiment_days:  # 有样本质控，一定有前处理和上机检测；
                    sample_rec.preexperiment_deadline = datetime.combine(find_workday(preexperiment_days,
                                                                                      pro_start_date), pro_start_time)

                    sample_rec.pretreat_deadline = datetime.combine(find_workday(preexperiment_days + pre_process_days,
                                                                                 pro_start_date), pro_start_time)
                    sample_rec.test_deadline = datetime.combine(find_workday(preexperiment_days + pre_process_days +
                                                                             test_days, pro_start_date), pro_start_time)
                    # 定义当前阶段剩余周期，及项目状态
                    sample_rec.current_stage_remain_days = preexperiment_days
                    sample_rec.status = 21
                else:
                    if pre_process_days and test_days:
                        # 有前处理，且有上机检测的项目
                        sample_rec.pretreat_deadline = datetime.combine(find_workday(pre_process_days, pro_start_date),
                                                                        pro_start_time)
                        sample_rec.test_deadline = datetime.combine(find_workday(pre_process_days+test_days,
                                                                                 pro_start_date), pro_start_time)
                        # 定义当前阶段的剩余周期，及项目状态
                        sample_rec.current_stage_remain_days = pre_process_days
                        sample_rec.status = 21
                    elif pre_process_days and not test_days:
                        # 只有前处理，一般为研发项目
                        sample_rec.pretreat_deadline = datetime.combine(find_workday(pre_process_days, pro_start_date),
                                                                        pro_start_time)
                        # 定义当前阶段剩余天数，及项目状态
                        sample_rec.current_stage_remain_days = pre_process_days
                        sample_rec.status = 21
                    else:
                        # 此时为数据分析，目前没有“无前处理”且直接上机的项目；此时不用处理截止日期，要处理当前阶段剩余周期，及项目状态
                        sample_rec.current_stage_remain_days = pro_type.analysis_cycle
                        sample_rec.status = 41
                # 定义当前阶段的剩余周期百分比
                sample_rec.current_stage_remain_percent = 100
                # 定义项目截至日期
                sample_rec.pro_deadline = datetime.combine(find_workday(pro_type.total_cycle, pro_start_date),
                                                           pro_start_time)
                # 定义总周期剩余天数及百分比
                sample_rec.pro_cyc_remain_days = pro_type.total_cycle
                sample_rec.pro_cyc_remain_percent = 100

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
        old_anti_fake_number = project_info.anti_fake_number
        old_pro_start_datetime = project_info.pro_start_date
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
            # 以下定义几个截止日期修改(周期以项目启动时间作为起点；时间节点变更条件：添加“项目启动时间”或已启动项目修改“项目类型”；)
            new_pro_start_datetime = project_info_form.cleaned_data.get("pro_start_date")
            if (not old_pro_start_datetime and new_pro_start_datetime) or (old_pro_start_datetime and
                                                                           'project_type' in change_list):
                # 此时项目一定为启动状态；
                new_pro_start_date = new_pro_start_datetime.date()
                new_pro_start_time = new_pro_start_datetime.time()
                pro_type = ProjectType.objects.get(id=request.POST.get("project_type"))
                # 同时修改启动截止日期
                start_days = pro_type.start_deadline
                if start_days:
                    project_info.start_deadline = datetime.combine(find_workday(start_days, new_pro_start_date),
                                                                   new_pro_start_time)
                else:
                    project_info.start_deadline = None
                # 定义样本质控截至日期
                preexperiment_days = pro_type.pre_experiment_cycle
                pre_process_days = pro_type.pre_process_cycle
                test_days = pro_type.test_cycle
                if preexperiment_days:  # 此时一定有前处理和上机检测；
                    project_info.preexperiment_deadline = datetime.combine(
                        find_workday(preexperiment_days, new_pro_start_date), new_pro_start_time)
                    project_info.pretreat_deadline = datetime.combine(find_workday(preexperiment_days+pre_process_days,
                                                                      new_pro_start_date), new_pro_start_time)
                    project_info.test_deadline = datetime.combine(find_workday(preexperiment_days+pre_process_days +
                                                                  test_days, new_pro_start_date), new_pro_start_time)
                    # 定义当前阶段剩余周期，及状态；
                    project_info.current_stage_remain_days = preexperiment_days
                    project_info.status = 21
                else:
                    project_info.preexperiment_deadline = None
                    # 定义前处理截至日期和下机截止日期
                    if pre_process_days and test_days:  # 有前处理，且有质谱上机的项目；
                        project_info.pretreat_deadline = datetime.combine(
                            find_workday(pre_process_days, new_pro_start_date), new_pro_start_time)
                        project_info.test_deadline = datetime.combine(
                            find_workday(pre_process_days+test_days, new_pro_start_date), new_pro_start_time)
                        # 定义当前阶段剩余周期，及状态调整
                        project_info.current_stage_remain_days = pre_process_days
                        project_info.status = 21
                    elif pre_process_days and not test_days:  # 只有样品制备，一般为研发项目；
                        project_info.test_deadline = None
                        project_info.pretreat_deadline = datetime.combine(
                            find_workday(pre_process_days, new_pro_start_date), new_pro_start_time)
                        # 定义当前阶段剩余天数，及状态
                        project_info.current_stage_remain_days = pre_process_days
                        project_info.status = 21
                    else:
                        # 此时为数据分析，暂时没有“无前处理”且有“上机检测”的项目；此时要处理当前阶段剩余周期，及项目状态调整
                        project_info.pretreat_deadline = None
                        project_info.test_deadline = None
                        project_info.current_stage_remain_days = pro_type.analysis_cycle
                        project_info.status = 41
                # 定义项目截至日期
                project_info.pro_deadline = datetime.combine(find_workday(pro_type.total_cycle, new_pro_start_date),
                                                             new_pro_start_time)
                # 定义当前阶段剩余百分比
                project_info.current_stage_remain_percent = 100
                # 定义项目总周期剩余天数及百分比
                project_info.pro_cyc_remain_days = pro_type.total_cycle
                project_info.pro_cyc_remain_percent = 100

            project_info.save()
            project_info_form.save_m2m()  # 使用commit后要手动保存manytomany
            msg = "edit_success"
            # 定义防伪编号修改联动项目结算中结算类型修改
            if 'anti_fake_number' in change_list:
                anti_fake_number = project_info_form.cleaned_data.get("anti_fake_number")
                if not (anti_fake_number and old_anti_fake_number):  # 两者只有一个存在的时候，才需要修改
                    edit_success.send(sample_record_edit,
                                      msg=msg, project_id=project_id, anti_fake_number=anti_fake_number)
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
    # 定义删除项目功能
    if request.method == 'POST':
        project_id = request.POST.get("project_id")
        current_id = json.loads(project_id)
        project = SampleRecord.objects.get(id=current_id)
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
        search_form.fields['status'].widget.choices = ((0, "--------"),) + SampleRecord.status_choices[1:4] +\
                                                      ((91, "全部"),)

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
        pro_status = int(request.GET.get('pro_status'))

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
        if pro_status > 90:  # 此处为全部数据，包括在前处理、质谱检测、分析阶段，及暂停终止项目、已完成项目
            status_filter = Q(status__range=(20, 83)) | Q(original_status__range=(20, 70))
        elif pro_status > 20:  # 此时为某一阶段
            status_filter = Q(status=pro_status)
        else:  # 此时为0或意外情况（为默认情况）
            status_filter = Q(status__range=(20, 30)) | Q(original_status__range=(20, 30)) & Q(status__lt=82)

        all_projects = projects_get_perm.filter(status_filter, **conditions)
        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

        response_data = {'total': all_projects_count, 'rows': []}  # 必须带有rows和total这2个key
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
            # 定义实验开始时间
            if project.start_date:
                start_date = project.start_date.strftime('%Y-%m-%d %H:%M')
            else:
                start_date = "-"
            # 定义预实验完成时间
            if project.preexperiment_finish_date:
                preexperiment_finish_date = project.preexperiment_finish_date.strftime('%Y-%m-%d %H:%M')
            else:
                preexperiment_finish_date = "-"
            # 格式化前处理完成日期，
            if project.pretreat_finish_date:
                pretreat_finish_date = project.pretreat_finish_date.strftime('%Y-%m-%d %H:%M')
            else:
                pretreat_finish_date = "-"
            # 定义当前阶段剩余时间和百分比
            current_remain_days = project.current_stage_remain_days
            if current_remain_days is not None:
                days_left = current_remain_days
            else:
                days_left = "-"
            current_remain_percent = project.current_stage_remain_percent
            if current_remain_percent is not None:
                time_percent = current_remain_percent
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
            # 定义中断类型
            interrupt_type = project.project_interrupt
            if interrupt_type:
                project_interrupt = interrupt_type.interrupt_type
            else:
                project_interrupt = "-"
            # 定义实验开始截止时间
            if project.start_deadline:
                start_deadline = project.start_deadline.strftime('%Y-%m-%d %H:%M')
            else:
                start_deadline = "-"
            # 定义预实验截止时间
            if project.preexperiment_deadline:
                preexperiment_deadline = project.preexperiment_deadline.strftime('%Y-%m-%d %H:%M')
            else:
                preexperiment_deadline = "-"
            # 定义前处理截止时间
            if project.pretreat_deadline:
                pretreat_deadline = project.pretreat_deadline.strftime('%Y-%m-%d %H:%M')
            else:
                pretreat_deadline = "-"

            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                "status": project.get_status_display(),
                "status_code": project.status,
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
                "days_left": days_left,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def pretreat_stage_edit(request, project_id):
    # 定义前处理信息修改功能
    project_info = SampleRecord.objects.get(id=project_id)
    if request.method == 'POST':
        original_start_time = project_info.start_date
        original_preexperiment_finish_time = project_info.preexperiment_finish_date
        original_pretreat_finish_time = project_info.pretreat_finish_date
        pro_type = project_info.project_type
        project_info_form = PretreatStageForm(request.POST, instance=project_info)
        if project_info_form.is_valid():
            project_info_form.save(commit=False)
            date_today = date.today()
            start_time_now = project_info_form.cleaned_data.get('start_date')
            preexperiment_finish_date_now = project_info_form.cleaned_data.get('preexperiment_finish_date')
            pretreat_finish_date_now = project_info_form.cleaned_data.get('pretreat_finish_date')
            if not original_pretreat_finish_time and pretreat_finish_date_now:
                # 此时为添加“前处理完成时间”，要修改状态及当前阶段剩余周期(周期计算要考虑项目按期交付)，要考虑“样本制备”项目；
                if pro_type.test_cycle:
                    project_info.status = 31
                    real_cyc_current_stage = len(get_workdays(project_info.pretreat_deadline,
                                                              project_info.test_deadline))-1
                    if date_today > project_info.test_deadline.date():
                        work_days = -len(get_workdays(project_info.test_deadline.date(), date_today))+1
                    else:  # 此时包括 < 和 =两种情况；
                        work_days = len(get_workdays(date_today, project_info.test_deadline.date()))-1
                    project_info.current_stage_remain_days = work_days
                    project_info.current_stage_remain_percent = work_days * 100 // real_cyc_current_stage
                else:  # 有前处理没有质谱检测，只能是“样本制备”项目；
                    project_info.status = 71
            elif not original_preexperiment_finish_time and preexperiment_finish_date_now and not pretreat_finish_date_now:
                # 此时为添加“预实验完成时间”，要修改状态及当前剩余周期
                project_info.status = 23
                real_cyc_current_stage = len(get_workdays(project_info.preexperiment_deadline,
                                                          project_info.pretreat_deadline))-1
                if date_today > project_info.pretreat_deadline.date():
                    work_days = -len(get_workdays(project_info.pretreat_deadline.date(), date_today))+1
                else:  # 此时包括 < 和 =两种情况；
                    work_days = len(get_workdays(date_today, project_info.pretreat_deadline.date()))-1
                project_info.current_stage_remain_days = work_days
                project_info.current_stage_remain_percent = work_days * 100 // real_cyc_current_stage
            elif not pretreat_finish_date_now and not preexperiment_finish_date_now and not original_start_time and\
                    start_time_now:
                # 此时为添加“实验开始时间”，要修改状态（要考虑项目是否有“样本质控”环节），不用修改周期（周期在样本登记环节已调整）；
                if pro_type.pre_experiment_cycle:
                    project_info.status = 22
                else:
                    project_info.status = 23

            project_info.save()
            project_info_form.save_m2m()
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
        search_form.fields['status'].widget.choices = ((0, "--------"),) + SampleRecord.status_choices[4:6] +\
                                                      ((91, "全部"),)

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
        pro_status = int(request.GET.get('pro_status'))

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
            conditions['test_finish_date__range'] = (start_time, end_time)
        if pro_status > 90:  # 此处为全部数据，包括质谱检测、分析阶段，及暂停终止项目、已完成项目
            status_filter = Q(status__range=(30, 83)) | Q(original_status__range=(30, 70))
        elif pro_status > 30:  # 此时为某一阶段
            status_filter = Q(status=pro_status)
        else:  # 此时为0或意外情况（为默认情况）
            status_filter = Q(status__range=(30, 40)) | Q(original_status__range=(30, 40)) & Q(status__lt=82)

        all_projects = projects_get_perm.filter(status_filter, **conditions)
        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

        response_data = {'total': all_projects_count, 'rows': []}  # 必须带有rows和total这2个key

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
            mass_spectra_engineer = project.ms_engineer
            if mass_spectra_engineer:
                ms_engineer = mass_spectra_engineer
            else:
                ms_engineer = "-"
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
            if project.test_deadline:  # 此时项目已启动；
                editable = True  # 用于该条目能否被修改
                test_deadline = project.test_deadline.strftime('%Y-%m-%d %H:%M')
            else:  # 此时项目未启动，或没有质谱检测阶段；
                test_deadline = "-"
                editable = False
            # 定义当前阶段剩余时间和百分比
            current_remain_days = project.current_stage_remain_days
            if current_remain_days is not None:
                days_left = current_remain_days
            else:
                days_left = "-"
            current_remain_percent = project.current_stage_remain_percent
            if current_remain_percent is not None:
                time_percent = current_remain_percent
            else:
                time_percent = "-"
            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                "status": project.get_status_display(),
                "status_code": project.status,
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
                "ms_engineer": ms_engineer,
                "responsible_person": responsible_person,
                "instrument_type": instrument_type,
                "date_test": date_test,
                "test_finish_date": test_finish_date,   # 新添加字段
                "test_deadline": test_deadline,
                "time_percent": time_percent,
                "days_left": days_left,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def test_stage_edit(request, pro_id):
    # 定义检测阶段编辑功能
    pro_test = SampleRecord.objects.get(id=pro_id)
    if request.method == 'POST':
        mass_spectra_engineer = pro_test.ms_engineer
        pro_test_form = TestStageForm(request.POST, instance=pro_test)
        original_test_finish_date = pro_test.test_finish_date
        original_date_test = pro_test.date_test
        pro_type = pro_test.project_type
        if pro_test_form.is_valid():
            change_list = pro_test_form.changed_data
            pro_test_form.save(commit=False)
            if "date_test" in change_list and not mass_spectra_engineer:
                pro_test.ms_engineer = request.user.first_name
            test_finish_date_now = pro_test_form.cleaned_data.get('test_finish_date')
            date_today = date.today()
            if not original_test_finish_date and test_finish_date_now:
                # 此时为添加“下机时间”，要修改当前阶段周期和状态；要考虑“质谱检测”项目；
                if pro_type.analysis_cycle:
                    pro_test.status = 41
                    real_current_stage_cyc = len(get_workdays(pro_test.test_deadline, pro_test.pro_deadline))-1
                    if date_today > pro_test.pro_deadline.date():
                        remain_days = -len(get_workdays(pro_test.pro_deadline.date(), date_today))+1
                    else:  # 包括 < 和 =两种情况；
                        remain_days = len(get_workdays(date_today, pro_test.pro_deadline.date()))-1
                    pro_test.current_stage_remain_days = remain_days
                    pro_test.current_stage_remain_percent = remain_days * 100 // real_current_stage_cyc
                else:  # 此时无“数据分析”阶段；
                    pro_test.status = 71
            elif not test_finish_date_now and not original_date_test and 'date_test' in change_list:
                # 此时为单独添加“上机日期”，只需更新状态
                pro_test.status = 32

            pro_test.save()
            pro_test_form.save_m2m()
            msg = "edit_success"
            return redirect('project_stage:test_stage', msg)
        else:
            msg = "failed"
            pro_test_form = TestStageForm(request.POST)
            return render(request, 'project_stage/test_stage_edit.html', {'form': pro_test_form, 'pro_test': pro_test,
                                                                          'msg': msg})
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
        search_form.fields['status'].widget.choices = ((0, "--------"),)+SampleRecord.status_choices[-5:-3]+((91, "全部"),)

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
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        time_item = request.GET.get('time_item')
        pro_status = int(request.GET.get('pro_status'))

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
        # 定义时间筛选
        if start_time and end_time:
            fmt = '%Y-%m-%d'
            start_time = datetime.strptime(start_time, fmt)
            end_time = datetime.strptime(end_time, fmt)
            if time_item == 'receive_sample':
                conditions['receive_time__range'] = (start_time, end_time)
            elif time_item == 'report_send':
                conditions['date_send_report__range'] = (start_time, end_time)
        if pro_status > 90:  # 此处为全部数据，包括在分析阶段，及该阶段暂停终止项目、已完成项目
            status_filter = Q(status__range=(20, 80)) | Q(original_status__range=(20, 50))
        elif pro_status > 40:  # 此时为某一阶段
            status_filter = Q(status=pro_status)
        else:  # 此时为0或意外情况（为默认情况）
            status_filter = Q(status__range=(40, 50)) | Q(original_status__range=(40, 50)) & Q(status__lt=82)

        all_projects = projects_get_perm.filter(status_filter, **conditions)
        all_projects_count = all_projects.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_projects, limit)  # 开始做分页

        response_data = {'total': all_projects_count, 'rows': []}  # 必须带有rows和total这2个key

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
            else:
                date_send_report = "-"
            # 定义当前阶段剩余时间和百分比
            current_remain_days = project.current_stage_remain_days
            if current_remain_days is not None:
                days_left = current_remain_days
            else:
                days_left = "-"
            current_remain_percent = project.current_stage_remain_percent
            if current_remain_percent is not None:
                time_percent = current_remain_percent
            else:
                time_percent = "-"
            if project.date_send_rawdata:
                date_send_rawdata = project.date_send_rawdata.strftime('%Y-%m-%d %H:%M')
            else:
                date_send_rawdata = "-"
            species_choice = project.species
            if species_choice:
                species = species_choice.species
            else:
                species = "-"
            protein_count = project.protein_amount
            if protein_count is not None:
                protein_amount = protein_count
            else:
                protein_amount = "-"

            response_data['rows'].append({
                "project_id": project.id,
                "project_num": project.project_num,
                "status": project.get_status_display(),
                "status_code": project.status,
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
                "days_left": days_left,
                "species": species,
                "protein_amount": protein_amount,
            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def analysis_stage_edit(request, project_id):
    # 定义数据分析修改功能
    project_info = SampleRecord.objects.get(id=project_id)
    current_status = project_info.status
    if request.method == 'POST':
        project_info_form = AnalysisStageForm(request.POST, instance=project_info)
        original_report_send_date = project_info.date_send_report
        original_date_searchlib = project_info.date_searchlib

        if project_info_form.is_valid():
            change_list = project_info_form.changed_data
            project_info_form.save(commit=False)
            report_send_date = project_info_form.cleaned_data.get('date_send_report')
            if not original_report_send_date and report_send_date:
                # 此时项目完成，要修改项目状态
                project_info.status = 71
            elif not report_send_date and not original_date_searchlib and 'date_searchlib' in change_list:
                project_info.status = 42
            if "pro_deadline" in change_list:
                # 计算实际周期占比(此处只能修改项目截止日期，不能添加项目截止日期；在页面通过js实现；)
                pro_start_date = project_info.pro_start_date.date()
                pro_start_time = project_info.pro_start_date.time()
                pro_deadline = project_info_form.cleaned_data.get('pro_deadline').date()
                real_pro_cycle = len(get_workdays(pro_start_date, pro_deadline))-1
                real_in_theory = round(real_pro_cycle / project_info.project_type.total_cycle, 2)
                # 修改实际实验开始截止日期
                start_cycle = project_info.project_type.start_deadline
                if start_cycle:
                    real_start_period = int(start_cycle * real_in_theory)  # 实际实验开始周期
                    project_info.start_deadline = datetime.combine(find_workday(real_start_period, pro_start_date),
                                                                   pro_start_time)
                # 修改实际样本质控截止日期
                pre_experiment_cycle = project_info.project_type.pre_experiment_cycle
                pre_process_cycle = project_info.project_type.pre_process_cycle
                test_cycle = project_info.project_type.test_cycle
                if pre_experiment_cycle:  # 此时一定有“前处理”和“质谱检测”；
                    real_preexperiment_period = int(pre_experiment_cycle * real_in_theory)  # 实际预实验周期
                    real_pre_period = int(pre_process_cycle * real_in_theory)
                    real_test_period = int(test_cycle * real_in_theory)  # 实际检测周期
                    project_info.preexperiment_deadline = datetime.combine(find_workday(real_preexperiment_period,
                                                                                        pro_start_date), pro_start_time)
                    # 修改实际前处理截止日期和下机截止日期
                    project_info.pretreat_deadline = datetime.combine(find_workday(real_preexperiment_period +
                                                                      real_pre_period, pro_start_date), pro_start_time)
                    project_info.test_deadline = datetime.combine(find_workday(real_preexperiment_period+real_pre_period
                                                                  + real_test_period, pro_start_date), pro_start_time)
                else:
                    if pre_process_cycle and test_cycle:  # 此时为“定性项目”；“无前处理有上机”的项目暂无；都没有，则为数据分析项目；
                        real_pre_period = int(pre_process_cycle * real_in_theory)  # 实际前处理周期
                        real_test_period = int(test_cycle * real_in_theory)
                        project_info.pretreat_deadline = datetime.combine(find_workday(real_pre_period, pro_start_date),
                                                                          pro_start_time)
                        project_info.test_deadline = datetime.combine(find_workday(real_pre_period+real_test_period,
                                                                                   pro_start_date), pro_start_time)
                    elif pre_process_cycle and not test_cycle:  # 此时为“样本制备”项目
                        real_pre_period = int(pre_process_cycle * real_in_theory)
                        project_info.pretreat_deadline = datetime.combine(find_workday(real_pre_period, pro_start_date),
                                                                          pro_start_time)
            if 'status' in change_list:
                # 此时处理“暂停”或“终止”（分三种情况：1、正常调整为“暂停”或“终止”；2、由“暂停”改为“终止”；3、“暂停”或“终止”恢复为正常）
                pause_choice = project_info_form.cleaned_data.get('status')
                list_status = [11, 21, 22, 23, 31, 32, 41, 42]
                if current_status in list_status and pause_choice not in list_status:  # 情况1 (情况2状态会自动调整)
                    project_info.original_status = current_status
                elif current_status not in list_status and pause_choice in list_status:  # 情况3 ；
                    # 以下为“暂停”或“终止”项目恢复时，各阶段截止日期调整
                    original_status_code = project_info.original_status
                    current_stage_remain_days = project_info.current_stage_remain_days
                    date_today = date.today()
                    original_pro_deadline = project_info.pro_deadline
                    original_test_deadline = project_info.test_deadline
                    original_pretreat_deadline = project_info.pretreat_deadline
                    original_preexperiment_deadline = project_info.preexperiment_deadline
                    if 40 < original_status_code < 50:  # 在数据分析阶段(总周期在后面调整)
                        pause_date = find_workday(current_stage_remain_days, original_pro_deadline)
                        add_days = len(get_workdays(pause_date, date_today))-1  # 起止时间按一天算
                    elif 30 < original_status_code < 40:  # 在质谱检测阶段
                        pause_date = find_workday(current_stage_remain_days, original_test_deadline)
                        add_days = len(get_workdays(pause_date, date_today))-1
                        project_info.test_deadline = datetime.combine(find_workday(add_days, original_test_deadline),
                                                                      original_test_deadline.time())
                    elif 22 < original_status_code < 30:  # 在样本制备阶段
                        pause_date = find_workday(current_stage_remain_days, original_pretreat_deadline)
                        add_days = len(get_workdays(pause_date, date_today))-1
                        project_info.pretreat_deadline = datetime.combine(
                            find_workday(add_days, original_pretreat_deadline), original_pretreat_deadline.time())
                        if original_test_deadline:  # "样本制备"项目没有“质谱检测”阶段；
                            project_info.test_deadline = datetime.combine(
                                find_workday(add_days, original_test_deadline), original_test_deadline.time())
                    elif 20 < original_status_code < 23:  # 在样本质控阶段
                        pause_date = find_workday(current_stage_remain_days, original_preexperiment_deadline)
                        add_days = len(get_workdays(pause_date, date_today))-1
                        project_info.preexperiment_deadline = datetime.combine(
                            find_workday(add_days, original_preexperiment_deadline), original_preexperiment_deadline.time())
                        # 同时调整后面的“样本制备”和“质谱检测”截止日期
                        project_info.pretreat_deadline = datetime.combine(
                            find_workday(add_days, original_pretreat_deadline), original_pretreat_deadline.time())
                        project_info.test_deadline = datetime.combine(find_workday(add_days, original_test_deadline),
                                                                      original_test_deadline.time())
                    # 最后调整总周期，和清空原状态编号
                    project_info.original_status = None
                    project_info.pro_deadline = datetime.combine(find_workday(add_days, original_pro_deadline),
                                                                 original_pro_deadline.time())
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
        # 若项目为“暂停”或“终止”，要初始化到Form
        original_status_code = project_info.original_status
        project_form = AnalysisStageForm(instance=project_info)
        if 80 < current_status < 90:
            status_choices = dict(SampleRecord.status_choices)
            project_form.fields['status'].widget.choices += ((original_status_code, status_choices[original_status_code]),)
        else:
            project_form.fields['status'].widget.choices += ((current_status, project_info.get_status_display()),)

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


@login_required()
def species_info_page(request, msg="normal_show"):
    # 定义物种信息页

    return render(request, 'project_stage/species_info.html', {'msg': msg})


def species_info_table(request):
    # 定义物种信息表
    if request.method == 'GET':
        limit = request.GET.get('pageSize')  # how many items per page
        pageNum = request.GET.get('pageNum')  # how many items in total in the DB
        search = request.GET.get('search')

        if search:  # 判断是否有搜索字
            all_species = SpeciesInfo.objects.filter(species__contains=search)
        else:
            all_species = SpeciesInfo.objects.all()  # must be wirte the line code here

        all_species_count = all_species.count()
        if not pageNum:
            pageNum = 1
        if not limit:
            limit = 50  # 默认是每页10行的内容，与前端默认行数一致
        paginator = Paginator(all_species, limit)  # 开始做分页

        response_data = {'total': all_species_count, 'rows': []}  # 必须带有rows和total这2个key
        for species in paginator.page(pageNum):
            # 下面这些key，都是我们在前端定义好了的，前后端必须一致，前端才能接受到数据并且请求.

            response_data['rows'].append({
                "species_id": species.id,
                "species": species.species,
                "database": species.database,
                "entry_count": species.entry_count,
                "creator": species.creator,
                "add_time": species.c_time.strftime('%Y-%m-%d'),

            })

    return HttpResponse(json.dumps(response_data))  # 需要json处理下数据格式


@login_required()
def species_add(request):
    # 定义物种添加功能
    if request.method == 'POST':
        species_form = SpeciesInfoForm(request.POST)
        if species_form.is_valid():
            species_form.save()
            msg = "add_success"

            return redirect('project_stage:species_info_page', msg)
        else:
            msg = "repeat"
            return render(request, 'project_stage/species_add.html', {'form': species_form, 'msg': msg})
    elif request.method == 'GET':
        species_form = SpeciesInfoForm()

        return render(request, 'project_stage/species_add.html', {'form': species_form, })


@login_required()
def species_edit(request, species_id):
    # 定义物种信息修改
    species = SpeciesInfo.objects.get(id=species_id)
    if request.method == 'POST':
        edit_form = SpeciesInfoForm(request.POST, instance=species)
        if edit_form.is_valid():

            edit_form.save()
            msg = "edit_success"
            return redirect('project_stage:species_info_page', msg)
        else:
            msg = 'edit_failed'
            edit_form = SpeciesInfoForm(request.POST)
            return render(request, 'project_stage/species_edit.html', {'form': edit_form, 'msg': msg, 'species': species})
    elif request.method == 'GET':

        edit_form = SpeciesInfoForm(instance=species)
        return render(request, 'project_stage/species_edit.html', {'form': edit_form, 'species': species})


@login_required()
def species_del(request):
    # 定义物种删除功能
    if request.method == 'POST':

        species_id = request.POST.get("species_id")
        current_id = json.loads(species_id)

        link_project = SampleRecord.objects.filter(species=current_id)
        if link_project:
            return HttpResponse("del_fail")
        else:
            species = SpeciesInfo.objects.get(id=current_id)
            species.delete()
            return HttpResponse("del_success")

    return HttpResponse("非POST请求！")
