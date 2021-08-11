from django.urls import path
from . import views

#  定义合同相关url
app_name = 'contract_manage'

urlpatterns = [
    # 项目合同列表页
    path('project_contract_page/', views.project_contract_page, name='project_contract_page'),
    path('project_contract_table/', views.project_contract_table, name='project_contract_table'),
    path('project_contract_add/', views.project_contract_add, name='project_contract_add'),
    path('project_contract_del/', views.project_contract_del, name='project_contract_del'),
    path('project_contract_detail/<int:contract_id>/', views.project_contract_detail, name='project_contract_detail'),
    path('project_contract_edit/<int:contract_id>/', views.project_contract_edit, name='project_contract_edit'),
    # 预付款合同列表页
    path('advancepay_contract_page/', views.advancepay_contract_page, name='advancepay_contract_page'),
    path('advancepay_contract_table/', views.advancepay_contract_table, name='advancepay_contract_table'),
    path('advancepay_contract_add/', views.advancepay_contract_add, name='advancepay_contract_add'),
    path('advancepay_contract_del/', views.advancepay_contract_del, name='advancepay_contract_del'),
    path('advancepay_contract_edit/<int:contract_id>/', views.advancepay_contract_edit, name='advancepay_contract_edit'),
    path('advancepay_contract_detail/<int:contract_id>/', views.advancepay_contract_detail, name='advancepay_contract_detail'),
    # 预付款扣款相关
    path('cut_payment_info/', views.cut_payment_info, name='cut_payment_info'),
    path('cut_payment_table/', views.cut_payment_table, name='cut_payment_table'),
    path('apply_cut_payment/', views.apply_cut_payment, name='apply_cut_payment'),
    path('cut_payment_edit/<int:apply_id>/', views.cut_payment_edit, name='cut_payment_edit'),
    path('cut_payment_detail/<int:apply_id>/', views.cut_payment_detail, name='cut_payment_detail'),
    path('cut_payment_del/', views.cut_payment_del, name='cut_payment_del'),
    # 审批和退回扣款
    path('approve_cut_payment/<int:apply_id>/', views.approve_cut_payment, name='approve_cut_payment'),
    path('untread_cut_payment/<int:apply_id>/', views.untread_cut_payment, name='untread_cut_payment'),
    ]
