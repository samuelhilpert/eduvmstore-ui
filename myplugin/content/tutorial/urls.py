from django.urls import re_path
from django.urls import path

from myplugin.content.tutorial import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    path('tutorial1/', views.TutorialPanelOneView.as_view(), name='tutorial_1'),
    path('tutorial2/', views.TutorialPanelTwoView.as_view(), name='tutorial_2'),
    path('tutorial3/', views.TutorialPanelThreeView.as_view(), name='tutorial_3'),
    path('tutorial4/', views.TutorialPanelFourView.as_view(), name='tutorial_4'),

]
