import os
import django
from celery import Celery
from django.conf import settings


# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CMS.settings')
django.setup()

# 实例化
app = Celery('CMS')
# namespace = 'CELERY'
app.config_from_object('django.conf.settings', namespace='CELERY')
# 自动从已注册的app中发现任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
