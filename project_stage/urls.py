from django.urls import path
from . import views
from .tests import species_import

#  定义项目和开票url
app_name = 'project_stage'

urlpatterns = [
    # 样本登记列表页
    # path('sample_record/', views.sample_record, name='sample_record'),
    path('sample_record/<msg>/', views.sample_record, name='sample_record'),
    path('sample_record_table/', views.sample_record_table, name='sample_record_table'),
    path('sample_record_add/', views.sample_record_add, name='sample_record_add'),
    path('sample_record_edit/<int:project_id>/', views.sample_record_edit, name='sample_record_edit'),
    path('sample_record_del/', views.sample_record_del, name='sample_record_del'),
    path('view_sample_detail/<int:pro_id>/', views.view_sample_detail, name='view_sample_detail'),
    # 前处理阶段
    path('pretreat_stage/<msg>/', views.pretreat_stage, name='pretreat_stage'),
    path('pretreat_stage_table/', views.pretreat_stage_table, name='pretreat_stage_table'),
    path('pretreat_stage_edit/<int:project_id>/', views.pretreat_stage_edit, name='pretreat_stage_edit'),
    path('pretreat_stage_detail/<int:pro_id>/', views.view_pretreat_detail, name='view_pretreat_detail'),
    # 质谱检测阶段
    path('test_stage/<msg>/', views.test_stage, name='test_stage'),
    path('test_stage_table/', views.test_stage_table, name='test_stage_table'),
    path('test_stage_edit/<int:pro_id>/', views.test_stage_edit, name='test_stage_edit'),
    path('test_stage_detail/<int:pro_id>/', views.test_stage_detail, name='test_stage_detail'),
    # 数据分析阶段
    path('analysis_stage/<msg>/', views.analysis_stage, name='analysis_stage'),
    path('analysis_stage_table/', views.analysis_stage_table, name='analysis_stage_table'),
    path('analysis_stage_edit/<int:project_id>/', views.analysis_stage_edit, name='analysis_stage_edit'),
    path('analysis_stage_detail/<int:pro_id>/', views.analysis_stage_detail, name='analysis_stage_detail'),
    path('edit_analysis_info/<int:pro_id>/', views.edit_analysis_info, name='edit_analysis_info'),
    # 定义物种信息导入功能
    path('species_import/', species_import, name='species_import'),
    path('species_info_page/<msg>', views.species_info_page, name='species_info_page'),
    path('species_info_table/', views.species_info_table, name='species_info_table'),
    path('species_add/', views.species_add, name='species_add'),
    path('species_edit/<int:species_id>/', views.species_edit, name='species_edit'),
    path('species_del/', views.species_del, name='species_del'),
    ]
