from django.urls import re_path
from django.urls import path

from myplugin.content.eduvmstore import views

urlpatterns = [
    re_path(r'^$', views.TableView.as_view(), name='overview'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('details/', views.AccountPageView.as_view(), name='details'),
    path('createImage/', views.CreateImageView.as_view(), name='createImage'),

]
