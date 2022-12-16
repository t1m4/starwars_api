from typing import List

from django.http import Http404

from swapi.models import File
from swapi.utils.csv_utils.exceptions import (
    EmptyPage,
    FileNotExist,
    PageNotAnPositiveInteger,
)
from swapi.utils.csv_utils.petl_utils import CSVReader


class PersonsService:
    def get_persons(self, filemeta: File, page: int) -> List[List[str]]:
        """Return list of persons

        Args:
            filemeta (File): object with file metadata
            page (int): number of page
        Returns:
            List[List[str]]: list of persons
        """
        csv_reader = CSVReader()
        try:
            results = csv_reader.read_with_pagination(filemeta.filename, filemeta.count_of_people, page=page)
        except (EmptyPage, PageNotAnPositiveInteger, FileNotExist):
            raise Http404

        return results

    def get_aggregated_persons(self, filemeta: File, person_fields: List[str]):
        """Return list of persons chosen fields"""
        csv_reader = CSVReader()
        return csv_reader.read_with_fields_combination(filemeta.filename, person_fields)
