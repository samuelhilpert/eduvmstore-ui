from django.urls import re_path
from django.urls import path

from myplugin.content.eduvmstore import views

urlpatterns = [

    path('', views.IndexView.as_view(), name='index'),
    path('details/<str:template_id>/', views.DetailsPageView.as_view(), name='details'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('edit/<str:template_id>/', views.EditView.as_view(), name='edit'),
    path('instances/<str:image_id>/', views.InstancesView.as_view(), name='instances'),
    path('validate-name/', views.validate_name, name='validate_name'),
    path('success/', views.InstanceSuccessView.as_view(), name='success'),
    path('favorite_template/', views.GetFavoriteAppTemplateView.as_view(), name='favorite_template'),
    path('delete_favorite_template', views.DeleteFavoriteAppTemplateView.as_view(),
         name='delete_favorite_template'),

]