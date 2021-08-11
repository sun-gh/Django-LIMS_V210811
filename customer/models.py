from django.db import models

# Create your models here.


class UnitInvoice(models.Model):

    # 定义开票单位
    unit_name = models.CharField(max_length=128, verbose_name="单位名称", default="单位全称", unique=True)
    duty_paragraph = models.CharField(max_length=256, verbose_name="税号", blank=True, null=True)
    bank = models.CharField(max_length=128, verbose_name="开户行", blank=True, null=True)
    account = models.CharField(max_length=128, verbose_name="银行账号", blank=True, null=True)
    address = models.CharField(max_length=256, verbose_name="单位地址", blank=True, null=True)
    phone = models.CharField(max_length=128, verbose_name="联系电话", blank=True, null=True)
    person_add = models.CharField(max_length=128, verbose_name="添加人", default="添加人")
    c_time = models.DateTimeField(verbose_name="添加时间", auto_now_add=True)

    def __str__(self):
        return self.unit_name

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "单位信息"
        verbose_name_plural = verbose_name


class CustomerInfo(models.Model):

    # 定义客户信息
    customer_name = models.CharField(max_length=128, verbose_name="客户姓名", default="姓名")
    contact_info = models.CharField(max_length=128, verbose_name="联系方式", blank=True, null=True)
    # 当关联单位被删除时，unit为null
    unit = models.ForeignKey(UnitInvoice, verbose_name="单位", on_delete=models.SET_NULL, null=True, blank=True)
    department = models.CharField(max_length=128, verbose_name="科室", blank=True, null=True)
    leading_official = models.CharField(max_length=128, verbose_name="负责人", blank=True, null=True)
    note = models.CharField(max_length=256, verbose_name="备注", blank=True, null=True)
    person_add = models.CharField(max_length=128, verbose_name="添加人", default="添加人")
    c_time = models.DateTimeField(verbose_name="添加时间", auto_now_add=True)

    def __str__(self):
        return self.customer_name

    class Meta:
        ordering = ["-c_time"]
        unique_together = ['customer_name', 'unit']
        verbose_name = "客户信息"
        verbose_name_plural = verbose_name
