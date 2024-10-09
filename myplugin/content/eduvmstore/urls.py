from django.urls import re_path
from django.urls import path

from myplugin.content.eduvmstore import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
   # path('overveiw/', views.TableView.as_view(), name='overview'),
    path('details/', views.AccountPageView.as_view(), name='details'),

]
