from django.urls import path

from swapi import views

urlpatterns = [
    path('', views.View.as_view(), name='swapi-example'),
    path('file/<int:id>/persons/', views.PersonView.as_view(), name='swapi-file_person'),
    path('files/', views.FileList.as_view(), name='swapi-file_list'),
]
