import petl
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# Create your views here.
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from swapi.models import File
from swapi.serializers import FileSerializer
from swapi.tasks import main_start
from swapi.utils.model_utils import get_object_or_none


class View(APIView):
    def get(self, request, *args, **kwargs):
        r = main_start()
        return Response(r)


class PersonView(APIView):

    def get(self, request, id, *args, **kwargs):
        filemeta = get_object_or_none(File, id=id)
        if filemeta:
            page = request.GET.get('page')
            # load all persons from csv
            t = petl.fromcsv(filemeta.filename)
            objects = list(petl.data(t))
            paginator = Paginator(objects, 10)
            try:
                objects_page = paginator.page(page)
            except PageNotAnInteger:
                # if not int, return first page
                objects_page = paginator.page(1)
            except EmptyPage:
                # if page is out of range return last page
                objects_page = paginator.page(paginator.num_pages)
            print(objects_page)
            return Response(objects_page.object_list)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FileList(generics.ListAPIView):
    queryset = File.objects.all().order_by('-id')
    serializer_class = FileSerializer
