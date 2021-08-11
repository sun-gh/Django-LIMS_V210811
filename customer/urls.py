from django.urls import path
from . import views

#  定义项目和开票url
app_name = 'customer'

urlpatterns = [
    # 主页
    path('index/', views.index, name='index'),
    # 单位相关链接
    path('unit_list/', views.unit_list, name='unit_list'),
    path('unit_list_table/', views.unit_list_table, name='unit_list_table'),
    path('unit_add/', views.unit_add, name='unit_add'),
    path('unit_del/', views.unit_del, name='unit_del'),
    path('unit_edit/<int:unit_id>/', views.unit_edit, name='unit_edit'),
    path('unit_import/', views.unit_import, name='unit_import'),

    # 客户相关链接
    path('customer_list/', views.customer_list, name='customer_list'),
    path('customer_list_table/', views.customer_list_table, name='customer_list_table'),
    path('customer_add/', views.customer_add, name='customer_add'),
    path('customer_del/', views.customer_del, name='customer_del'),
    path('customer_edit/<int:customer_id>/', views.customer_edit, name='customer_edit'),

]
