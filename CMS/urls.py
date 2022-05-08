"""CMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf.urls import url
from django.views.static import serve
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    # 用户账户
    path('user/', include('users.urls')),
    # 客户及单位相关
    path('customer/', include('customer.urls')),
    # 项目进度相关
    path('project_stage/', include('project_stage.urls')),
    # 项目结算相关
    path('project_order/', include('project_order.urls')),
    # 合同相关
    path('contract_manage/', include('contract_manage.urls')),
    # 发票相关
    path('invoice_manage/', include('invoice_manage.urls')),
    # 临床意向
    path('clinic_intention/', include('clinic_intention.urls')),
    # 需求管理
    path('demand_manage/', include('demand_manage.urls')),
    # 数据可视化
    path('data_visual/', include('data_visual.urls')),
    # 文件下载链接
    url('media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
]
