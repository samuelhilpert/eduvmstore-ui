from django.urls import re_path
from django.urls import path

from myplugin.content.eduvmstore import views

urlpatterns = [

    path('', views.IndexView.as_view(), name='index'),
    path('details/<str:template_id>/', views.DetailsPageView.as_view(), name='details'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('instances/<str:image_id>/', views.InstancesView.as_view(), name='instances'),

]