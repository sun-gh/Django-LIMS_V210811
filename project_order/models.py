from django.db import models
from project_stage.models import SampleRecord
# Create your models here.


class SalePerson(models.Model):
    # 定义销售人员
    name_person = models.CharField(verbose_name="销售人员", max_length=64)
    # 为以后调整顺序用，可手动设置order编号
    order = models.PositiveSmallIntegerField(verbose_name="序号", unique=True, null=True)
    valid = models.BooleanField(verbose_name="有效", default=True)

    def __str__(self):

        return self.name_person

    class Meta:
        ordering = ["order"]
        verbose_name = "销售人员"
        verbose_name_plural = verbose_name


class PayType(models.Model):
    # 定义结算方式
    type_name = models.CharField(max_length=128, verbose_name="结算方式", unique=True)

    class Meta:
        verbose_name = "结算方式"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.type_name


class ProjectOrder(models.Model):
    # 定义项目结算模型
    project_source_choice = (
        (0, "常规项目"),
        (1, "临床项目"),
    )
    customer_source_choice = (
        (1, "终端"),
        (2, "代理商"),
    )
    project_order = models.OneToOneField(SampleRecord, verbose_name="项目编号", on_delete=models.CASCADE)
    project_source = models.SmallIntegerField(choices=project_source_choice, verbose_name="项目来源", default=0)
    customer_source = models.SmallIntegerField(choices=customer_source_choice, verbose_name="客户来源", null=True, blank=True)
    project_sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="项目金额", null=True, blank=True)
    sale_person = models.CharField(max_length=32, verbose_name="销售人员", null=True, blank=True)
    pay_type = models.CharField(max_length=32, verbose_name="结算方式", null=True, blank=True)
    whether_distribute = models.BooleanField(verbose_name="分配与否", default=False)
    contract_record = models.BooleanField(verbose_name="合同记录", default=False)
    note = models.CharField(max_length=256, verbose_name="备注", blank=True, null=True)

    class Meta:
        verbose_name = "项目结算信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.project_order.project_num
