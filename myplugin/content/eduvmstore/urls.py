from django.urls import path

from myplugin.content.eduvmstore import views
from myplugin.content.eduvmstore.view import index, apptemplate, detail, instances, success

urlpatterns = [

    path('', index.IndexView.as_view(), name='index'),
    path('details/<str:template_id>/', detail.DetailsPageView.as_view(), name='details'),
    path('create/', apptemplate.AppTemplateView.as_view(), name='create_empty'),
    path('create/<str:template_id>/', apptemplate.AppTemplateView.as_view(), name='create_with_template'),
    path('edit/<str:template_id>/', apptemplate.AppTemplateView.as_view(), name='edit'),
    path('instances/<str:image_id>/', instances.InstancesView.as_view(), name='instances'),
    path('validate-name/', views.validate_name, name='validate_name'),
    path('success/', success.InstanceSuccessView.as_view(), name='success'),
    path('favorite_template/', views.GetFavoriteAppTemplateView.as_view(), name='favorite_template'),
    path('delete_template/<str:template_id>/', views.DeleteTemplateView.as_view(), name='delete_template'),
    path('delete_favorite_template', views.DeleteFavoriteAppTemplateView.as_view(),
         name='delete_favorite_template'),
]
