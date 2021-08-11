
from django.contrib.auth.models import User

# Create your models here.


class Person(User):
    # 定义用户模型
    class Meta:
        proxy = True  # 表明这是一个代理模型
        verbose_name = "用户账户"
        verbose_name_plural = verbose_name
