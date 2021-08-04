from django.shortcuts import render

# Create your views here.
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from swapi.models import File
from swapi.serializers import FileSerializer
from swapi.tasks import main_start


class View(APIView):
    def get(self, request, *args, **kwargs):
        r = main_start()
        return Response(r)

class FileView(APIView):
    serializer = 1
    def get(self, request, *args, **kwargs):
        return Response('hello')

class FileList(generics.ListAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer