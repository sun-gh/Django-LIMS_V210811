from django.urls import path
from . import views

#  定义临床意向相关url
app_name = 'clinic_intention'

urlpatterns = [
    path('intention_page/<msg>/', views.intention_page, name='intention_page'),
    path('intention_table/', views.intention_table, name='intention_table'),
    path('add_intention/', views.add_intention, name='add_intention'),
    path('del_intention/', views.del_intention, name='del_intention'),
    path('edit_intention/<int:intention_id>/', views.edit_intention, name='edit_intention'),
    path('intention_detail/<int:intention_id>/', views.intention_detail, name='intention_detail'),
    # 添加意向跟进记录
    path('add_followup_record/', views.add_followup_record, name='add_followup_record'),
    ]
