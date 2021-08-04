from django.urls import path

from swapi import views

urlpatterns = [
    path('', views.View.as_view(), name='swapi-example'),
    path('files/', views.FileList.as_view(), name='swapi-file_list'),
]
