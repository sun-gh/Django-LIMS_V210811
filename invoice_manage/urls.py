from django.urls import path
from . import views

#  定义发票相关url
app_name = 'invoice_manage'

urlpatterns = [
    # 开票申请记录相关
    path('apply_invoice/', views.apply_invoice, name='apply_invoice'),
    path('apply_invoice_record/<msg>/', views.apply_invoice_record, name='apply_invoice_record'),
    path('apply_invoice_table/', views.apply_invoice_table, name='apply_invoice_table'),
    path('apply_invoice_detail/<int:apply_id>/', views.apply_invoice_detail, name='apply_invoice_detail'),
    path('apply_invoice_edit/<int:apply_id>/', views.apply_invoice_edit, name='apply_invoice_edit'),
    path('apply_invoice_del/', views.apply_invoice_del, name='apply_invoice_del'),
    # 申请审批和退回路由
    path('approve_apply_invoice/<int:apply_id>/', views.approve_apply_invoice, name='approve_apply_invoice'),
    path('untread_apply_invoice/<int:apply_id>/', views.untread_apply_invoice, name='untread_apply_invoice'),
    path('file_apply_invoice/<int:apply_id>/', views.file_apply_invoice, name='file_apply_invoice'),
    # 已开发票相关
    path('invoice_info/<msg>/', views.invoice_info, name='invoice_info'),
    path('invoice_info_table/', views.invoice_info_table, name='invoice_info_table'),
    path('edit_invoice_info/<int:invoice_id>/', views.edit_invoice_info, name='edit_invoice_info'),
    path('edit_pay_info/<int:invoice_id>/', views.edit_pay_info, name='edit_pay_info'),
    path('invoice_info_detail/<int:invoice_id>/', views.invoice_info_detail, name='invoice_info_detail'),
    # 发票作废相关
    path('void_red_info/<msg>/', views.void_red_info, name='void_red_info'),
    path('void_red_info_table/', views.void_red_info_table, name='void_red_info_table'),
    path('apply_void_red/', views.apply_void_red, name='apply_void_red'),
    path('edit_void_red/<int:apply_id>/', views.edit_void_red, name='edit_void_red'),
    path('void_red_detail/<int:apply_id>/', views.void_red_detail, name='void_red_detail'),
    path('apply_void_del/', views.apply_void_del, name='apply_void_del'),
    # 审批和退回作废申请路由
    path('approve_apply_void/<int:apply_id>/', views.approve_apply_void, name='approve_apply_void'),
    path('untread_apply_void/<int:apply_id>/', views.untread_apply_void, name='untread_apply_void'),

    ]
