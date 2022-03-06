from django.urls import path
from . import views

#  定义需求管理url
app_name = 'demand_manage'

urlpatterns = [
    # 需求梳理相关链接
    path('demand_page/<msg>/', views.demand_page, name='demand_page'),
    path('demand_table/', views.demand_table, name='demand_table'),
    path('add_demand/', views.add_demand, name='add_demand'),
    path('del_demand/', views.del_demand, name='del_demand'),
    path('edit_demand/<int:demand_id>/', views.edit_demand, name='edit_demand'),
    path('demand_detail/<int:demand_id>/', views.demand_detail, name='demand_detail'),
    path('demand_verify/<int:demand_id>/', views.demand_verify, name='demand_verify'),
    # 需求设计相关链接
    path('demand_design_page/<msg>/', views.demand_design_page, name='demand_design_page'),
    path('demand_design_table/', views.demand_design_table, name='demand_design_table'),
    path('demand_design_detail/<int:design_id>/', views.demand_design_detail, name='demand_design_detail'),
    path('demand_design_estimate/<int:design_id>/', views.demand_design_estimate, name='demand_design_estimate'),
    path('edit_demand_design/<int:design_id>/', views.edit_demand_design, name='edit_demand_design'),
]
