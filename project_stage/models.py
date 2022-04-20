from django.db import models
from customer.models import CustomerInfo
# Create your models here.


class SampleType(models.Model):
    #  定义样本类型model
    type_name = models.CharField(max_length=64, verbose_name="样本类型", unique=True)

    class Meta:
        verbose_name = "样本类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.type_name


class MachineTime(models.Model):
    #  定义机时类型model
    time_type = models.CharField(max_length=64, verbose_name="机时类型", unique=True)

    class Meta:
        verbose_name = "机时类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.time_type


class SampleQuality(models.Model):
    # 定义样本质量
    quality_type = models.CharField(max_length=64, verbose_name="样本质量", unique=True)
    message_template = models.CharField(max_length=64, verbose_name="短信模板名称", blank=True, null=True)
    order = models.PositiveSmallIntegerField(verbose_name="显示顺序", unique=True, blank=True, null=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "样本质量"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.quality_type


class AdditionalItem(models.Model):
    # 定义附加项目类型
    item_type = models.CharField(max_length=64, verbose_name="附加项目", unique=True)

    class Meta:
        verbose_name = "附加项目"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.item_type


class ProjectType(models.Model):
    # 定义项目类型
    project_name = models.CharField(max_length=128, verbose_name="项目类型", unique=True)
    total_cycle = models.PositiveSmallIntegerField(verbose_name="总周期")
    start_deadline = models.PositiveSmallIntegerField(verbose_name="启动预警期", null=True, blank=True)
    pre_experiment_cycle = models.PositiveSmallIntegerField(verbose_name="预实验周期", null=True, blank=True)
    pre_process_cycle = models.PositiveSmallIntegerField(verbose_name="前处理周期", null=True, blank=True)
    test_cycle = models.PositiveSmallIntegerField(verbose_name="检测周期", null=True, blank=True)
    analysis_cycle = models.PositiveSmallIntegerField(verbose_name="数据分析周期", null=True, blank=True)

    class Meta:
        verbose_name = "项目类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.project_name


class FilesRelated(models.Model):
    # 定义项目相关文件
    file = models.FileField(upload_to='project_files/', verbose_name="项目相关文件", max_length=100, blank=True, null=True)
    c_time = models.DateTimeField(verbose_name="上传时间", auto_now_add=True)

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = "项目相关文件"
        verbose_name_plural = verbose_name


class OperatePerson(models.Model):
    # 定义实验操作人员
    operate_person = models.CharField(verbose_name="实验操作人员", max_length=64)
    valid = models.BooleanField(verbose_name="有效", default=True)

    def __str__(self):
        return self.operate_person

    class Meta:
        verbose_name = "实验操作人员"
        verbose_name_plural = verbose_name


class SampleStatus(models.Model):
    # 定义剩余样本状态
    status_type = models.CharField(verbose_name="状态类型", max_length=64)

    def __str__(self):
        return self.status_type

    class Meta:
        verbose_name = "剩余样本状态"
        verbose_name_plural = verbose_name


class ProjectInterrupt(models.Model):
    # 定义项目中断类型
    interrupt_type = models.CharField(verbose_name="中断类型", max_length=64)
    # type_order = models.PositiveSmallIntegerField(verbose_name="类型编号", default=0)

    def __str__(self):
        return self.interrupt_type

    class Meta:
        # ordering = ["type_order"]
        verbose_name = "项目中断类型"
        verbose_name_plural = verbose_name


class Machine(models.Model):
    # 定义上机仪器
    instrument = models.CharField(max_length=64, verbose_name="上机仪器", unique=True)

    class Meta:
        verbose_name = "仪器类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.instrument


class ResponsiblePerson(models.Model):
    # 定义项目负责人
    name = models.CharField(max_length=32, verbose_name="姓名")
    order = models.PositiveSmallIntegerField(verbose_name="显示顺序", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order"]
        verbose_name = "项目负责人"
        verbose_name_plural = verbose_name


class SampleRecord(models.Model):
    # 定义样本登记表
    priority_level = (
        (0, "--------"),
        (1, "加急"),
        (2, "预实验"),
        (3, "优先"),
    )
    status_choices = (
        (11, "待启动"),
        (21, "准备实验"),
        (22, "前处理"),
        (31, "待上机"),
        (32, "检测中"),
        (41, "待分析"),
        (42, "分析中"),
        (71, "完成"),
        (81, "暂停"),
        (82, "终止"),
    )
    project_num = models.CharField(max_length=32, verbose_name="项目编号", unique=True)
    status = models.PositiveSmallIntegerField(verbose_name="状态", choices=status_choices, default=11)
    original_status = models.CharField(max_length=32, verbose_name="原状态编号", null=True, blank=True)
    project_type = models.ForeignKey(ProjectType, verbose_name="项目类型", on_delete=models.SET_NULL, null=True)
    sample_type = models.CharField(max_length=32, verbose_name="样本类型")
    machine_time = models.CharField(max_length=48, verbose_name="机时类型", null=True, blank=True)
    sample_amount = models.PositiveSmallIntegerField(verbose_name="样本数量")
    sample_sender = models.ForeignKey(CustomerInfo, verbose_name="送样人", on_delete=models.SET_NULL, null=True)
    agent_id = models.PositiveIntegerField(verbose_name="代理ID", null=True, blank=True)
    anti_fake_number = models.CharField(max_length=32, verbose_name="防伪编号", null=True, blank=True)
    # 将以下两个字段直接保存到记录
    unit = models.CharField(max_length=128, verbose_name="单位", null=True, blank=True)
    terminal = models.CharField(max_length=32, verbose_name="送样终端", blank=True, null=True)
    # sample_quality = models.ManyToManyField(SampleQuality, verbose_name="样本质量")
    sample_quality = models.ForeignKey(SampleQuality, verbose_name="样本运送条件和质量", on_delete=models.SET_NULL, null=True)
    addition_item = models.ManyToManyField(AdditionalItem, verbose_name="附加项目", blank=True)
    receive_time = models.DateTimeField(verbose_name="收样时间", null=True)
    pro_start_date = models.DateTimeField(verbose_name="项目启动时间", null=True, blank=True)
    pro_start_time = models.DateField(verbose_name="项目启动日期", null=True)  # 添加字段用于备份
    person_record = models.CharField(max_length=32, verbose_name="登记人")
    c_time = models.DateTimeField(verbose_name="登记时间", auto_now_add=True)
    note = models.CharField(max_length=256, verbose_name="备注", blank=True, null=True)
    files = models.ManyToManyField(FilesRelated, verbose_name="相关文件", blank=True)
    # 以下为前处理阶段
    priority = models.SmallIntegerField(choices=priority_level, verbose_name="优先级", default=0)
    start_date = models.DateTimeField(verbose_name="实验开始日期", null=True, blank=True)
    start_time = models.DateField(verbose_name="实验开始日期", null=True)  # 添加字段用于备份
    preexperiment_finish_date = models.DateTimeField(verbose_name="预实验完成时间", null=True, blank=True)
    preexperiment_finish_time = models.DateField(verbose_name="预实验完成时间", null=True)  # 添加字段用于备份
    pretreat_finish_date = models.DateTimeField(verbose_name="前处理完成时间", null=True, blank=True)
    pretreat_finish_time = models.DateField(verbose_name="前处理完成时间", null=True)  # 添加字段用于备份
    first_operate_person = models.ManyToManyField(OperatePerson, verbose_name="步骤一", related_name='exp_first_person',
                                                  blank=True)
    second_operate_person = models.ManyToManyField(OperatePerson, verbose_name="步骤二", related_name='exp_second_person',
                                                   blank=True)
    third_operate_person = models.ManyToManyField(OperatePerson, verbose_name="步骤三", related_name='exp_third_person',
                                                  blank=True)
    fourth_operate_person = models.ManyToManyField(OperatePerson, verbose_name="步骤四", related_name='exp_fourth_person',
                                                   blank=True)
    # 添加电泳操作人
    page_person = models.ManyToManyField(OperatePerson, verbose_name="跑胶", related_name='exp_page_person', blank=True)
    sample_overplus = models.NullBooleanField(verbose_name="样本剩余")
    sample_overplus_status = models.ManyToManyField(SampleStatus, verbose_name="剩余样本状态", blank=True)
    project_interrupt = models.ForeignKey(ProjectInterrupt, verbose_name="项目中断类型", on_delete=models.SET_NULL,
                                          blank=True, null=True)
    start_deadline = models.DateTimeField(verbose_name="实验开始截止日期", null=True, blank=True)
    start_deadline_date = models.DateField(verbose_name="实验开始截止日期", null=True)  # 添加字段用于备份
    preexperiment_deadline = models.DateTimeField(verbose_name="预实验截止日期", null=True, blank=True)
    preexperiment_deadline_date = models.DateField(verbose_name="预实验截止日期", null=True)  # 添加字段用于备份
    pretreat_deadline = models.DateTimeField(verbose_name="制备截止日期", null=True, blank=True)
    pretreat_deadline_date = models.DateField(verbose_name="制备截止日期", null=True)  # 添加字段用于备份
    # 以下为检测-数据分析阶段
    instrument_type = models.ForeignKey(Machine, verbose_name="上机仪器", on_delete=models.SET_NULL, blank=True, null=True)
    date_test = models.DateTimeField(verbose_name="上机日期", blank=True, null=True)
    date_test_time = models.DateField(verbose_name="上机日期", null=True)  # 添加字段用于备份
    test_finish_date = models.DateTimeField(verbose_name="下机日期", blank=True, null=True)
    test_finish_time = models.DateField(verbose_name="下机日期", null=True)  # 添加字段用于备份
    responsible_person = models.ForeignKey(ResponsiblePerson, verbose_name="项目负责人", on_delete=models.SET_NULL,
                                           blank=True, null=True)
    date_searchlib = models.DateTimeField(verbose_name="搜库日期", blank=True, null=True)
    date_searchlib_time = models.DateField(verbose_name="搜库日期", null=True)  # 添加字段用于备份
    date_send_report = models.DateTimeField(verbose_name="报告发送日期", blank=True, null=True)
    date_send_report_time = models.DateField(verbose_name="报告发送日期", null=True)  # 添加字段用于备份
    date_send_rawdata = models.DateTimeField(verbose_name="原始数据发送日期", blank=True, null=True)
    date_send_rawdata_time = models.DateField(verbose_name="原始数据发送日期", null=True)  # 添加字段用于备份
    test_deadline = models.DateTimeField(verbose_name="下机截止日期", blank=True, null=True)
    test_deadline_date = models.DateField(verbose_name="下机截止日期", null=True)  # 添加字段用于备份
    pro_deadline = models.DateTimeField(verbose_name="项目截止日期", blank=True, null=True)
    pro_deadline_date = models.DateField(verbose_name="项目截止日期", null=True)  # 添加字段用于备份

    def __str__(self):
        return self.project_num

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "样本登记表"
        verbose_name_plural = verbose_name
