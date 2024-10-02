from django.urls import re_path

from myplugin.content.mypanel import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^second/$', views.SecondPageView.as_view(), name='second_page'),
]
