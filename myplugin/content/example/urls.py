from django.urls import re_path

from myplugin.content.example import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),

]
