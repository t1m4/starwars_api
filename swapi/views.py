# Create your views here.

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from swapi.models import File
from swapi.serializers import FileSerializer
from swapi.tasks import task_get_all_in_csv
from swapi.utils.csv_utils.exceptions import EmptyPage, PageNotAnPositiveInteger, FileNotExist
from swapi.utils.csv_utils.petl_utils import CSVReader, aggregate_csv, get_fields
from swapi.utils.model_utils import get_object_or_none


class View(APIView):
    def get(self, request, *args, **kwargs):
        task_get_all_in_csv()
        return Response('ok')


class PersonView(APIView):

    def get(self, request, id, *args, **kwargs):
        filemeta = get_object_or_none(File, id=id)
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if filemeta:
            csv_reader = CSVReader()
            try:
                results = csv_reader.pagination_read(filemeta.filename, filemeta.count_of_people, page=page)
            except (EmptyPage, PageNotAnPositiveInteger, FileNotExist):
                return Response(status=status.HTTP_404_NOT_FOUND)

            return Response(results)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FileList(generics.ListAPIView):
    queryset = File.objects.all().order_by('-id')
    serializer_class = FileSerializer


class PersonAggregateView(APIView):
    def get(self, request, id, *args, **kwargs):
        filemeta = get_object_or_none(File, id=id)
        if filemeta:
            csv_reader = CSVReader()
            try:
                keys = get_fields(request.GET)
            except KeyError:
                return Response(status=status.HTTP_404_NOT_FOUND)

            try:
                results = csv_reader.read_file_from_line(filemeta.filename, start_from_line=0,
                                                         max_page_size=filemeta.count_of_people)

            except (EmptyPage, PageNotAnPositiveInteger, FileNotExist) as e:
                return Response(status=status.HTTP_404_NOT_FOUND)

            response = aggregate_csv(results, keys)
            return Response(response)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
