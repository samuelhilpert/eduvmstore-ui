from django.urls import re_path
from django.urls import path

from myplugin.content.eduvmstore import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    path('details/', views.DetailsPageView.as_view(), name='details'),
    path('create/', views.CreateView.as_view(), name='create'),

]
