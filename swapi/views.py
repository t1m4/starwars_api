from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from swapi.models import File
from swapi.serializers import (
    FileSerializer,
    PageInputSerializer,
    PersonFieldsInputSerializer,
)
from swapi.services import PersonsService
from swapi.tasks import task_get_all_in_csv


class View(APIView):
    def get(self, request, *args, **kwargs):
        task_get_all_in_csv()
        return Response("ok")


class PersonView(APIView):
    def get(self, request, id, *args, **kwargs):
        filemeta = get_object_or_404(File, id=id)
        serializer = PageInputSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        results = PersonsService().get_persons(filemeta, serializer.validated_data["page"])
        return Response(results)


class FileList(generics.ListAPIView):
    queryset = File.objects.all().order_by("-id")
    serializer_class = FileSerializer


class PersonAggregateView(APIView):
    def get(self, request, id, *args, **kwargs):
        filemeta = get_object_or_404(File, id=id)
        serializer = PersonFieldsInputSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        results = PersonsService().get_aggregated_persons(filemeta, serializer.validated_data["person_fields"])
        return Response(results)
