from django.urls import re_path
from django.urls import path

from myplugin.content.mypanel import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    path('second_page/', views.SecondPageView.as_view(), name='second_page'),

]
