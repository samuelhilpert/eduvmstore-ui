from django.urls import re_path
from django.urls import path

from myplugin.content.admin import views
from myplugin.content.admin.views import change_user_role

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    path('change_user_role/', change_user_role, name='change_user_role'),

]
