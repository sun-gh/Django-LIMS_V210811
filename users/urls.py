from django.urls import path
from . import views


#  定义用户url
app_name = 'users'

urlpatterns = [
    # 登录与退出
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    # 修改密码
    path('password-change/', views.change_pwd, name='password_change'),
    # 添加权限
    path('add_permission/', views.add_permission, name='add_permission'),
    # 数据展示相关
    path('data_show_page/', views.data_show_page, name='data_show_page'),
    path('project_and_sample_statistics/', views.project_and_sample_statistics, name='project_and_sample_statistics'),
    path('project_type_statistics/', views.project_type_statistics, name='project_type_statistics'),
]
