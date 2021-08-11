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
]
