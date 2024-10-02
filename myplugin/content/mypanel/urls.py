from django.urls import re_path
from django.urls import path

from myplugin.content.mypanel import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    path('mylist/', views.mylist, name='mylist'),
]
