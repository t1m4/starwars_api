import logging
import os

import petl
from django.conf import settings

from swapi.utils.csv_utils.exceptions import EmptyPage, PageNotAnPositiveInteger, FileNotExist

logger = logging.getLogger('starwars.console_logger')


class CSVWriter():
    def write(self, filename: str, content: dict):
        """
        Write any dict to csv file. If it doesn't exist then create it with headers
        """
        filename = settings.STATICFILES_DIRS[0] + filename
        content = [content]
        table = petl.fromdicts(content, header=content[0].keys())
        exist = os.path.exists(filename)
        # petl.appendcsv(table, filename, write_header=not exist)
        if exist:
            petl.appendcsv(table, filename, delimiter=";")
        else:
            petl.appendcsv(table, filename, delimiter=";", write_header=True)


class CSVReader():
    MAX_PAGE_SIZE = 10

    def __file_read(self, filename):
        exist = os.path.exists(filename)
        if not exist:
            raise FileNotExist('File does not exist')

        file = open(filename, "r")
        index = 0
        for line in file:
            yield index, line
            index += 1

    def read_file_from_line(self, filename: str, max_page_size: int, start_from_line: int = 1):
        """
        Read curtain line from file
        """
        filename = settings.STATICFILES_DIRS[0] + filename
        result_lines = []
        for index, line in self.__file_read(filename):
            if index < start_from_line:
                continue
            elif index >= start_from_line + max_page_size:
                break
            else:
                line = line.strip().split(';')
                result_lines.append(line)
        return result_lines

    def pagination_read(self, filename: str, count_of_people: int, page: int, max_page_size: int = None):
        """
        Read from give CSV file
        :param count_of_people: count of people in file
        :param page: number of page given by user
        :param max_page_size: max page size in pagination
        """
        if page < 1:
            raise PageNotAnPositiveInteger('Page is not an positive number')

        max_page_size = max_page_size or self.MAX_PAGE_SIZE
        start_from_line = (page - 1) * max_page_size + 1

        # If there are more lines than people
        if start_from_line > count_of_people:
            raise EmptyPage("Can't find page")

        result = self.read_file_from_line(filename, start_from_line=start_from_line, max_page_size=max_page_size)
        return result


def get_fields(request_fields):
    """
    Try to get certain fields from request.GET
    """
    list_of_fields = ['name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender',
                      'homeworld', 'date']
    keys = []
    for field in list_of_fields:
        if request_fields.get(field):
            keys.append(field)
    if len(keys) == 0:
        raise KeyError("Can't find fields")
    return keys


def aggregate_csv(file_output, keys):
    """
    Aggregate csv file output using keys
    """

    key_length = len(keys)
    if key_length > 1:
        aggregate_results = petl.aggregate(file_output, key=keys, aggregation=len, )
    elif key_length == 1:
        aggregate_results = petl.aggregate(file_output, key=keys[0], aggregation=len, )
    results = []
    for row in aggregate_results:
        results.append(row)

    return results
