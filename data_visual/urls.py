from django.urls import path
from . import views


#  定义用户url
app_name = 'data_visual'

urlpatterns = [
    # 数据展示相关
    path('total_data_page/', views.total_data_page, name='total_data_page'),
    path('project_and_sample_statistics/', views.project_and_sample_statistics, name='project_and_sample_statistics'),
    path('project_type_statistics/', views.project_type_statistics, name='project_type_statistics'),
    path('sample_type_statistics/', views.sample_type_statistics, name='sample_type_statistics'),
    path('delay_rate_page/', views.delay_rate_page, name='delay_rate_page'),
    path('analyse_by_finish_time/', views.analyse_by_finish_time, name='analyse_by_finish_time'),
    ]
