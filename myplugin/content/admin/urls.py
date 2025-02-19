from django.urls import re_path
from django.urls import path

from myplugin.content.admin import views


urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    path('update_roles/', views.UpdateRolesView.as_view(), name='update_roles'),
    path('approve_template/', views.ApproveTemplateView.as_view(), name='approve_template'),
    path('delete_template/', views.DeleteTemplateView.as_view(), name='delete_template'),
    path('delete_user/', views.DeleteUserView.as_view(), name='delete_user'),
    path('create_role/', views.CreateRoleView.as_view(), name='create_role'),


]
