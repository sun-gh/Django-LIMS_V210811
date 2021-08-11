from django.urls import path
from . import views

#  定义项目和开票url
app_name = 'project_order'

urlpatterns = [
    # 样本登记列表页
    path('project_order_page/', views.project_order_page, name='project_order_page'),
    path('project_order_table/', views.project_order_table, name='project_order_table'),
    path('project_order_detail/<int:pro_id>/', views.project_order_detail, name='project_order_detail'),
    path('project_order_edit/<int:pro_id>/', views.project_order_edit, name='project_order_edit'),
    ]
