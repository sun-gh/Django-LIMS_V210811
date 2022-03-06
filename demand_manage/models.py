from django.db import models

# Create your models here.


class DemandCollect(models.Model):
    # 定义需求收集模型
    status_choices = (
        (1, "待审核"),
        (2, "已审核"),
        (3, "已退回"),
    )
    demand_type_choices = (
        (1, "新增功能"),
        (2, "功能变更"),
        (3, "功能舍弃"),
        (4, "问题"),
    )
    urgent_levels = (
        (0, "不紧急"),
        (1, "紧急"),
    )
    important_levels = (
        (0, "不重要"),
        (1, "重要"),
    )
    verify_result_choices = (
        (0, "无"),
        (1, "确定要做"),
        (2, "确定不做"),
        (3, "再想想"),
        (4, "退回"),
    )
    demand_number = models.CharField(max_length=32, verbose_name="需求编号", unique=True)
    status = models.PositiveSmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    sponsor = models.CharField(max_length=16, verbose_name="提出人", default="")
    department = models.CharField(max_length=32, verbose_name="部门", default="")
    create_time = models.DateTimeField(verbose_name="提出时间", auto_now_add=True)
    demand_type = models.PositiveSmallIntegerField(verbose_name="需求类型", choices=demand_type_choices, default=1)
    demand_describe = models.CharField(max_length=500, verbose_name="需求描述", default="")
    urgent_degree = models.PositiveSmallIntegerField(verbose_name="紧急程度", choices=urgent_levels, default=0)
    important_degree = models.PositiveSmallIntegerField(verbose_name="重要程度", choices=important_levels, default=0)
    # 需求截图
    file = models.ImageField(upload_to='demand_images/', verbose_name="相关截图", max_length=100, blank=True, null=True)
    verify_result = models.PositiveSmallIntegerField(verbose_name="审核结果", choices=verify_result_choices, default=0)
    note = models.CharField(max_length=300, verbose_name="审核建议", null=True, blank=True)

    def __str__(self):
        return self.demand_number

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "需求梳理"
        verbose_name_plural = verbose_name


class DemandDesign(models.Model):
    # 定义需求设计模型
    status_choices = (
        (1, "待评估"),
        (2, "关闭"),
        (3, "待开发"),
        (4, "开发中"),
        (5, "已完成"),
    )
    estimate_result_choices = (
        (0, "无"),
        (1, "通过"),
        (2, "退回"),
        (3, "暂缓"),
    )
    demand = models.OneToOneField(DemandCollect, verbose_name="需求编号", on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    estimate_result = models.PositiveSmallIntegerField(verbose_name="评估结果", choices=estimate_result_choices, default=0)
    note = models.CharField(max_length=300, verbose_name="评估建议", null=True, blank=True)
    predict_cycle = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="预计开发周期", null=True, blank=True)
    start_time = models.DateField(verbose_name="开始时间", null=True, blank=True)
    finish_time = models.DateField(verbose_name="完成时间", null=True, blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return self.demand.demand_number

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "需求设计"
        verbose_name_plural = verbose_name
