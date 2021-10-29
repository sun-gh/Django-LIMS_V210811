from django.db import models
from contract_manage.models import ProjectContract

# Create your models here.


class InvoiceRequire(models.Model):

    # 定义开票要求
    require_content = models.CharField(max_length=64, verbose_name="开票要求", unique=True)

    def __str__(self):
        return self.require_content

    class Meta:

        verbose_name = "开票要求类型"
        verbose_name_plural = verbose_name


class ReimburseFile(models.Model):

    # 定义报账文件
    file = models.FileField(upload_to='reimburse_files/', verbose_name="报账文件", max_length=100, blank=True, null=True)
    c_time = models.DateTimeField(verbose_name="上传时间", auto_now_add=True)

    def __str__(self):

        return str(self.file)

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "报账文件"
        verbose_name_plural = verbose_name


class ApplyInvoice(models.Model):
    # 定义开票申请模型
    status_choice = (
        (0, "待审批"),
        (1, "已审批"),
        (2, "已退回"),
        (3, "已归档"),
    )
    invoice_type_choice = (
        (0, "项目开票"),
        (1, "预付款开票"),
        (2, "代开票"),
    )

    serial_number = models.CharField(max_length=32, verbose_name="申请序号", unique=True)
    status = models.SmallIntegerField(choices=status_choice, verbose_name="状态", default=0)
    related_contract = models.ForeignKey(ProjectContract, verbose_name="关联合同", on_delete=models.SET_NULL, null=True)
    unit = models.CharField(max_length=128, verbose_name="开票单位")
    invoice_sum = models.DecimalField(verbose_name="开票金额", max_digits=10, decimal_places=2)
    sheet_num = models.PositiveIntegerField(verbose_name="开票张数")
    invoice_require = models.ManyToManyField(InvoiceRequire, verbose_name="开票要求", blank=True)
    reimburse_file = models.ManyToManyField(ReimburseFile, verbose_name="报账文件", blank=True)
    # 开票类型暂定三种
    invoice_type = models.SmallIntegerField(choices=invoice_type_choice, verbose_name="开票类型", default=0)
    note = models.CharField(max_length=500, verbose_name="备注", blank=True, null=True)
    linkman = models.CharField(max_length=32, verbose_name="联系人")
    phone = models.BigIntegerField(verbose_name="电话", blank=True, null=True)
    address_linkman = models.CharField(max_length=128, verbose_name="收件地址", blank=True, null=True)
    applicant = models.CharField(max_length=32, verbose_name="申请人", default="销售")
    c_time = models.DateTimeField(verbose_name="申请时间", auto_now_add=True)
    post_date = models.DateField(verbose_name="发票寄送日期", null=True, blank=True)
    express_num = models.CharField(max_length=64, verbose_name="发票快递单号", blank=True, null=True)

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "开票申请"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.serial_number

    def get_invoice(self):
        # 定义对应发票
        link_invoice = InvoiceInfo.objects.filter(link_apply_id=self.id)
        return link_invoice


class InvoiceInfo(models.Model):
    # 定义发票信息模型
    void_red_choice = (
        (0, "无"),
        (1, "冲红"),
        (2, "作废"),
    )
    invoice_num = models.CharField(max_length=32, verbose_name="发票号", blank=True, null=True, unique=True)
    link_apply = models.ForeignKey(ApplyInvoice, verbose_name="关联开票申请", on_delete=models.SET_NULL, null=True)
    unit_invoice = models.CharField(max_length=64, verbose_name="开票单位", default="开票单位")
    linkman = models.CharField(max_length=32, verbose_name="联系人")
    applicant = models.CharField(max_length=32, verbose_name="申请人", default="销售")
    invoice_sum = models.DecimalField(verbose_name="发票金额", max_digits=10, decimal_places=2, blank=True, null=True)
    invoice_date = models.DateField(verbose_name="开票日期", null=True, blank=True)
    void_red = models.SmallIntegerField(choices=void_red_choice, verbose_name="作废/冲红", default=0)
    invoice_callback = models.NullBooleanField(verbose_name="发票是否收回", default=None)
    reason = models.CharField(max_length=128, verbose_name="未收回原因", blank=True, null=True)
    payment_date = models.DateField(verbose_name="回款日期", null=True, blank=True)
    payment_sum = models.DecimalField(verbose_name="回款金额", max_digits=10, decimal_places=2, blank=True, null=True)
    note = models.CharField(max_length=128, verbose_name="备注", blank=True, null=True)
    c_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "发票信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.invoice_num


class VoidRedInfo(models.Model):
    # 定义发票作废/冲红信息模型
    status_choice = (
        (0, "待审批"),
        (1, "已退回"),
        (2, "已审批"),
    )
    treat_choice = (
        (1, "冲红"),
        (2, "作废"),
    )
    serial_number = models.CharField(max_length=32, verbose_name="申请序号", unique=True)
    link_invoice = models.ManyToManyField(InvoiceInfo, verbose_name="原发票号")
    reason = models.CharField(max_length=128, verbose_name="作废/冲红原因", blank=True, null=True)
    treat_type = models.SmallIntegerField(choices=treat_choice, verbose_name="处理类型", default=1)
    applicant = models.CharField(max_length=32, verbose_name="申请人", default="销售")
    c_time = models.DateTimeField(verbose_name="申请时间", auto_now_add=True)
    status = models.SmallIntegerField(choices=status_choice, verbose_name="状态", default=0)

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "发票作废/冲红信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.serial_number
