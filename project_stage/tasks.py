from celery import shared_task
from .models import SampleRecord
from chinese_calendar import get_workdays
from datetime import date


@shared_task()
def project_period_update():
    # 定义项目总周期更新任务(排除未启动，已完成，暂停及终止项目)
    pros_not_finished = SampleRecord.objects.filter(status__gt=20, status__lt=70)
    date_today = date.today()
    for pro in pros_not_finished:
        pro_deadline = pro.pro_deadline.date()  # get_workdays计算时会包括起止日期；
        pro_real_cyc = len(get_workdays(pro.pro_start_date.date(), pro_deadline))-1
        if date_today > pro_deadline:
            pro_remain_days = -len(get_workdays(pro_deadline, date_today))+1
        else:  # 此时包括 < 和 = 两种情况；
            pro_remain_days = len(get_workdays(date_today, pro_deadline))-1

        pro.pro_cyc_remain_days = pro_remain_days
        pro.pro_cyc_remain_percent = pro_remain_days * 100 // pro_real_cyc
        pro.save()
    message = 'Project period update successful!'

    return message


@shared_task()
def current_stage_period_update():
    # 定义当前阶段周期更新(已启动，但未完成的项目；去掉暂停或终止项目)
    pros_not_finished = SampleRecord.objects.filter(status__gt=20, status__lt=70)
    date_today = date.today()
    for pro in pros_not_finished:  # 更新每个项目分阶段的剩余周期天数及百分比
        pro_start_date = pro.pro_start_date.date()
        # 分别计算当前阶段实际周期
        if 40 < pro.status < 70:  # 此时在数据分析阶段
            current_stage_deadline = pro.pro_deadline.date()
            if pro.project_type.test_cycle:
                current_stage_real_cyc = len(get_workdays(pro.test_deadline.date(), current_stage_deadline))-1
            else:
                current_stage_real_cyc = len(get_workdays(pro_start_date, current_stage_deadline))-1
        elif 30 < pro.status < 40:  # 此时在质谱检测阶段
            current_stage_deadline = pro.test_deadline.date()
            if pro.project_type.pre_process_cycle:
                current_stage_real_cyc = len(get_workdays(pro.pretreat_deadline.date(), current_stage_deadline))-1
            else:
                current_stage_real_cyc = len(get_workdays(pro_start_date, current_stage_deadline))-1
        elif 22 < pro.status < 30:  # 此时为“制备中”
            current_stage_deadline = pro.pretreat_deadline.date()  # 质谱上机项目前处理给出1天时间，避免前处理截止日期为空
            if pro.project_type.pre_experiment_cycle:
                current_stage_real_cyc = len(get_workdays(pro.preexperiment_deadline.date(), current_stage_deadline))-1
            else:
                current_stage_real_cyc = len(get_workdays(pro_start_date, current_stage_deadline))-1
        elif 21 < pro.status < 23:  # 此时为“质控中”
            current_stage_deadline = pro.preexperiment_deadline.date()
            current_stage_real_cyc = len(get_workdays(pro_start_date, current_stage_deadline))-1
        else:  # 此时为“待实验”状态
            if pro.project_type.pre_experiment_cycle:  # 有“样本质控”环节；
                current_stage_deadline = pro.preexperiment_deadline.date()
            else:  # 有”样本制备“环节；
                current_stage_deadline = pro.pretreat_deadline.date()
            current_stage_real_cyc = len(get_workdays(pro_start_date, current_stage_deadline))-1
        # 统一计算当前阶段剩余周期天数
        if date_today > current_stage_deadline:
            remain_days = -len(get_workdays(current_stage_deadline, date_today))+1
        else:  # 此时包括 < 和 =两种情况；
            remain_days = len(get_workdays(date_today, current_stage_deadline))-1

        pro.current_stage_remain_days = remain_days
        pro.current_stage_remain_percent = remain_days * 100 // current_stage_real_cyc
        pro.save()
    message = 'Stage period update successful!'

    return message
