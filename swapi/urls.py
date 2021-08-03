from django.urls import path

from swapi import views

urlpatterns = [
    path('', views.View.as_view(), name='swapi-example'),
]
