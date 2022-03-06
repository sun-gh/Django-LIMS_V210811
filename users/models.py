from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.


class UserGroup(models.Model):
    # 用户组
    type_choices = (
        (0, '公司'),
        (1, '部门'),
        (2, '岗位'),
    )
    name = models.CharField(max_length=32, verbose_name="中文名", unique=True)
    group = models.OneToOneField(Group, verbose_name="关联组", on_delete=models.SET_NULL, null=True)
    type = models.SmallIntegerField(choices=type_choices, verbose_name="类型", default=2)

    class Meta:
        verbose_name = "用户组"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Staff(models.Model):
    # 定义员工
    user = models.OneToOneField(User, verbose_name="员工", on_delete=models.CASCADE)
    department = models.ForeignKey(UserGroup, verbose_name="部门", on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "员工"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.user)
