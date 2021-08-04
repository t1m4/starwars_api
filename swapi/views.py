from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from swapi.tasks import main_start


class View(APIView):
    def get(self, request, *args, **kwargs):
        r = main_start()
        return Response(r)
