from django.urls import path
from . import views

#  定义项目和开票url
app_name = 'project_order'

urlpatterns = [
    # 样本登记列表页(之后表示已分配项目)
    path('project_order_page/<msg>/', views.project_order_page, name='project_order_page'),
    path('project_order_table/', views.project_order_table, name='project_order_table'),
    path('project_order_detail/<int:pro_id>/', views.project_order_detail, name='project_order_detail'),
    path('project_order_edit/<int:pro_id>/', views.project_order_edit, name='project_order_edit'),
    path('untread_project/<int:pro_id>/', views.untread_project_order, name='untread_project'),
    # 未分配项目相关路径
    path('order_not_distribute_page/<msg>/', views.order_not_distribute_page, name='order_not_distribute_page'),
    path('order_not_distribute_table', views.order_not_distribute_table, name='order_not_distribute_table'),
    path('distribute_project_order/<int:pro_id>/', views.distribute_project_order, name='distribute_project_order'),
    path('fetch_project_order/<int:pro_id>/', views.fetch_project_order, name='fetch_project_order'),
    ]
