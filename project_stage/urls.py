from django.urls import path
from . import views

#  定义项目和开票url
app_name = 'project_stage'

urlpatterns = [
    # 样本登记列表页
    path('sample_record/', views.sample_record, name='sample_record'),
    path('sample_record_table/', views.sample_record_table, name='sample_record_table'),
    path('sample_record_add/', views.sample_record_add, name='sample_record_add'),
    path('sample_record_edit/<int:project_id>/', views.sample_record_edit, name='sample_record_edit'),
    path('sample_record_del/', views.sample_record_del, name='sample_record_del'),
    path('view_sample_detail/<int:pro_id>/', views.view_sample_detail, name='view_sample_detail'),
    # 前处理阶段
    path('pretreat_stage/', views.pretreat_stage, name='pretreat_stage'),
    path('pretreat_stage_table/', views.pretreat_stage_table, name='pretreat_stage_table'),
    path('pretreat_stage_edit/<int:project_id>/', views.pretreat_stage_edit, name='pretreat_stage_edit'),
    path('pretreat_stage_detail/<int:pro_id>/', views.view_pretreat_detail, name='view_pretreat_detail'),
    # 检测分析阶段
    path('test_analysis/', views.test_analysis, name='test_analysis'),
    path('test_analysis_table/', views.test_analysis_table, name='test_analysis_table'),
    path('test_analysis_edit/<int:project_id>/', views.test_analysis_edit, name='test_analysis_edit'),
    path('test_analysis_detail/<int:pro_id>/', views.test_analysis_detail, name='test_analysis_detail'),
    ]
