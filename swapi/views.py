# Create your views here.
from django.core.exceptions import ValidationError
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from starwars import settings
from swapi.models import File
from swapi.serializers import FileSerializer
from swapi.utils.model_utils import get_object_or_none
from swapi.utils.petl_utils import CSVReader
from swapi.tasks import task_get_all_in_csv
from swapi.validators import validate_positive


class View(APIView):
    def get(self, request, *args, **kwargs):
        csv_reader = CSVReader()
        csv_reader.read(settings.STATICFILES_DIRS[0] + 'people_yfhrnl3gb34fmosqgmqd.csv', 10)
        return Response('ok')


class PersonView(APIView):

    def get(self, request, id, *args, **kwargs):
        filemeta = get_object_or_none(File, id=id)
        try:
            page = int(request.GET.get('page', 1))
            page = validate_positive(page)
        except (ValueError, ValidationError):
            return Response(status=status.HTTP_404_NOT_FOUND)


        if filemeta:
            csv_reader = CSVReader()
            # results = csv_reader.read(filemeta.filename, start_from_line=1)
            # results = csv_reader.pagination_read("big_file_delimiter.csv", page=page)
            results = csv_reader.pagination_read("small_file.csv", page=page)
            return Response(results)
        # if filemeta:
        #     # TODO make sure that with large files it will work efficiently. If not do it using generators
        #     start_time = time.time()
        #     objects = get_list_from_csv(filemeta.filename)
        #     page = request.GET.get('page', 1)
        #     paginator = Paginator(objects, 10)
        #     try:
        #         objects_page = paginator.page(page)
        #     except (PageNotAnInteger, EmptyPage):
        #         # if not int or out of range return Not found
        #         return Response("Not found", status=status.HTTP_404_NOT_FOUND)
        #     print(time.time() - start_time)
        #     return Response(objects_page.object_list)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FileList(generics.ListAPIView):
    queryset = File.objects.all().order_by('-id')
    serializer_class = FileSerializer
