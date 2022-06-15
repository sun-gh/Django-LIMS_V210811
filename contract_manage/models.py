from django.db import models
from project_order.models import ProjectOrder

# Create your models here.


class ProjectContract(models.Model):
    # 定义项目合同模型
    contract_type_choice = (
        (0, "项目合同"),
        (1, "预付款合同"),
        (2, "代开票合同"),
    )
    status_choice = (
        (0, "待使用"),  # yellow
        (1, "已使用"),  # blue
        (2, "已生效"),  # green
        (3, "已作废"),  # red
    )

    contract_num = models.CharField(max_length=64, verbose_name="合同编号", unique=True)
    status = models.SmallIntegerField(choices=status_choice, verbose_name="状态", default=0)
    project_order = models.ManyToManyField(ProjectOrder, verbose_name="关联项目", blank=True)
    unit_name = models.CharField(max_length=128, verbose_name="单位名称")
    linkman = models.CharField(max_length=32, verbose_name="联系人")
    contract_sum = models.DecimalField(verbose_name="合同金额", max_digits=10, decimal_places=2)
    contract_type = models.SmallIntegerField(choices=contract_type_choice, verbose_name="合同类型", default=0)
    contract_file = models.FileField(upload_to='contract_files/', verbose_name="合同附件", max_length=128, null=True,
                                     blank=True)
    callback_date = models.DateField(verbose_name="合同回收日期", blank=True, null=True)
    creator = models.CharField(max_length=32, verbose_name="创建人", default="销售")
    makeout_invoice_sum = models.DecimalField(verbose_name="已开票金额", max_digits=10, decimal_places=2, default=0)
    not_makeout_invoice_sum = models.DecimalField(verbose_name="未开票金额", max_digits=10, decimal_places=2)
    note = models.CharField(max_length=128, verbose_name="备注", blank=True, null=True)
    payment_sum = models.DecimalField(verbose_name="回款金额", max_digits=10, decimal_places=2, default=0)
    # 以下为预付款字段
    used_sum = models.DecimalField(verbose_name="已使用金额", max_digits=10, decimal_places=2, default=0)
    c_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "项目合同"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.contract_num


class ContractAlter(models.Model):
    # 定义合同变更模型
    status_choice = (
        (0, "待审批"),
        (1, "已退回"),
        (2, "已审批"),
    )
    alter_type_choice = (
        ("end", "终止合同"),
        ("edit", "修改合同"),
    )
    serial_number = models.CharField(max_length=32, verbose_name="申请序号", unique=True)
    status = models.SmallIntegerField(choices=status_choice, verbose_name="状态", default=0)
    related_contract = models.ForeignKey(ProjectContract, verbose_name="关联合同", on_delete=models.SET_NULL, null=True)
    alter_type = models.CharField(max_length=32, choices=alter_type_choice, verbose_name="变更类型", default="edit")
    newly_invoice = models.BooleanField(verbose_name="重新开票", null=True, blank=True)
    alter_projects = models.ManyToManyField(ProjectOrder, verbose_name="关联项目", blank=True)
    alter_unit = models.CharField(max_length=128, verbose_name="单位名称", null=True, blank=True)
    alter_sum = models.DecimalField(verbose_name="合同金额", max_digits=10, decimal_places=2, null=True, blank=True)
    alter_contract_file = models.FileField(upload_to='contract_files/', verbose_name="合同附件", max_length=128, null=True,
                                           blank=True)
    alter_reason = models.CharField(max_length=256, verbose_name="变更原因", null=True, blank=True)
    applicant = models.CharField(max_length=32, verbose_name="申请人", default="")
    c_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "合同变更"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.serial_number


class CutPayment(models.Model):
    # 定义预付款扣款
    status_choice = (
        (0, "待审批"),
        (1, "已退回"),
        (2, "已审批"),
    )
    serial_number = models.CharField(max_length=32, verbose_name="申请序号", unique=True)
    link_contract = models.ForeignKey(ProjectContract, verbose_name="关联预付款合同", on_delete=models.SET_NULL, null=True)
    surplus_sum = models.DecimalField(verbose_name="扣款前剩余金额", max_digits=10, decimal_places=2, default=0)
    cut_sum = models.DecimalField(verbose_name="扣款金额", max_digits=10, decimal_places=2)
    cut_date = models.DateField(verbose_name="扣款日期", blank=True, null=True)
    applicant = models.CharField(max_length=32, verbose_name="申请人", default="销售")
    c_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    # 可能是多对多关系
    link_order = models.ManyToManyField(ProjectOrder, verbose_name="关联项目")
    note = models.CharField(max_length=128, verbose_name="备注", blank=True, null=True)
    status = models.SmallIntegerField(choices=status_choice, verbose_name="状态", default=0)

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "预付款扣款"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.serial_number
