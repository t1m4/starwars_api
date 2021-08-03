from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from swapi.tasks import main_start, get_people


class View(APIView):
    def get(self, request, *args, **kwargs):
        # r = get_people()
        r = main_start()
        return Response(r)
