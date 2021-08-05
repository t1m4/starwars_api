import time

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# Create your views here.
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from swapi.models import File
from swapi.serializers import FileSerializer
from swapi.tasks import task_get_all_in_csv
from swapi.utils.model_utils import get_object_or_none
from swapi.utils.petl_utils import get_list_from_csv, csv_reader


class View(APIView):
    def get(self, request, *args, **kwargs):
        task_get_all_in_csv.delay()
        return Response("ok")


class PersonView(APIView):

    def get(self, request, id, *args, **kwargs):
        filemeta = get_object_or_none(File, id=id)
        if filemeta:
            # TODO make sure that with large files it will work efficiently. If not do it using generators
            start_time = time.time()
            objects = get_list_from_csv(filemeta.filename)
            page = request.GET.get('page')
            paginator = Paginator(objects, 10)
            try:
                objects_page = paginator.page(page)
            except (PageNotAnInteger, EmptyPage):
                # if not int or out of range return Not found
                return Response("Not found", status=status.HTTP_404_NOT_FOUND)
            print(time.time() - start_time)
            return Response(objects_page.object_list)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FileList(generics.ListAPIView):
    queryset = File.objects.all().order_by('-id')
    serializer_class = FileSerializer
