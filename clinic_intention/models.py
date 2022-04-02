from django.db import models
from customer.models import UnitInvoice


class SampleType(models.Model):
    # 定义临床样本类型
    type_name = models.CharField(max_length=32, verbose_name="类型名称", unique=True)
    order = models.PositiveSmallIntegerField(verbose_name="显示顺序", unique=True)

    def __str__(self):
        return self.type_name

    class Meta:
        ordering = ["order"]
        verbose_name = "临床样本类型"
        verbose_name_plural = verbose_name


class DemandType(models.Model):
    # 定义需求预估类型
    type_name = models.CharField(max_length=32, verbose_name="类型名称", unique=True)
    order = models.PositiveSmallIntegerField(verbose_name="显示顺序", unique=True)

    def __str__(self):
        return self.type_name

    class Meta:
        ordering = ["order"]
        verbose_name = "需求预估"
        verbose_name_plural = verbose_name


class FollowUpRecord(models.Model):
    # 定义跟进记录
    communicate_time = models.DateField(verbose_name="沟通时间")
    linkman = models.CharField(max_length=32, verbose_name="对接人")
    communicate_content = models.CharField(max_length=256, verbose_name="沟通内容")
    c_time = models.DateTimeField(verbose_name="记录时间", auto_now_add=True)
    recorder = models.CharField(max_length=32, verbose_name="记录人")

    def __str__(self):
        return self.c_time.strftime("%Y-%m-%d") + "---" + self.recorder

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "跟进记录"
        verbose_name_plural = verbose_name


class ClinicIntention(models.Model):
    # 定义临床意向
    plan_choice = (
        (0, "--------"),
        (1, "方案草案"),
        (2, "详细方案"),
    )
    project_stage_choice = (
        (0, "--------"),
        (1, "洽谈"),
        (2, "潜在"),
        (3, "合同拟定"),
        (4, "合同签订"),
    )

    intention_number = models.CharField(max_length=32, verbose_name="意向编号", unique=True)
    customer_name = models.CharField(max_length=32, verbose_name="客户姓名")
    contact_info = models.CharField(max_length=32, verbose_name="联系方式", blank=True, null=True)
    unit = models.ForeignKey(UnitInvoice, verbose_name="单位", on_delete=models.SET_NULL, null=True)
    department = models.CharField(max_length=64, verbose_name="科室/院系", blank=True, null=True)
    leading_official = models.CharField(max_length=32, verbose_name="负责人", blank=True, null=True)
    disease_type = models.CharField(max_length=32, verbose_name="疾病种类", blank=True, null=True)
    plan_needed = models.NullBooleanField(verbose_name="是否需方案设计")
    plan_type = models.SmallIntegerField(choices=plan_choice, verbose_name="方案类型", blank=True, null=True)
    plan_deadline = models.DateField(verbose_name="方案截止日期", blank=True, null=True)
    customer_budget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="客户预算", null=True, blank=True)
    sample_number = models.PositiveSmallIntegerField(verbose_name="计划样本数量", blank=True, null=True)
    collect_time = models.DateField(verbose_name="计划收样日期", blank=True, null=True)
    send_time = models.DateField(verbose_name="计划送样日期", blank=True, null=True)
    sample_type = models.ForeignKey(SampleType, verbose_name="样本类型", on_delete=models.SET_NULL, null=True, blank=True)
    project_stage = models.SmallIntegerField(choices=project_stage_choice, verbose_name="项目阶段", blank=True, null=True)
    demand_estimate = models.ManyToManyField(DemandType, verbose_name="需求预估", blank=True)
    note = models.CharField(max_length=256, verbose_name="备注", blank=True, null=True)
    followup_record = models.ManyToManyField(FollowUpRecord, verbose_name="跟进记录", blank=True)
    add_person = models.CharField(max_length=16, verbose_name="添加人")
    c_time = models.DateTimeField(verbose_name="添加时间", auto_now_add=True)

    def __str__(self):
        return self.intention_number

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "临床意向信息"
        verbose_name_plural = verbose_name
