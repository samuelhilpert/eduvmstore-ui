from django.urls import re_path

from myplugin.content.mypanel import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^second/$', views.second_page, name='second_page'),
]


