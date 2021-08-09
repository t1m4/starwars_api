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
        Read from given CSV file with pagination
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

    def aggregation_read(self, filename, keys: list):
        """
        Aggregate csv file result
        """
        filename = settings.STATICFILES_DIRS[0] + filename
        aggregation_result = {}
        for index, line in self.__file_read(filename):
            if index == 0:
                continue
            row = line.strip().split(';')

            aggregate_row = []
            for key in keys:
                aggregate_row.append(row[key[0]])

            # add to the dict
            tuple_row = tuple(aggregate_row)
            if tuple_row not in aggregation_result:
                aggregation_result[tuple_row] = 1
            else:
                aggregation_result[tuple_row] += 1

        return aggregation_result

    def to_list(self, result, keys):
        """
        Change dict to list. And first row in results
        """
        first_row = self.__get_first_row(keys)
        list_result = [first_row]

        for key, value in result.items():
            row_list = list(key)
            row_list.append(value)
            list_result.append(row_list)
        return list_result

    def __get_first_row(self, keys_with_index: list):
        """
        Get first row
        """
        keys = []
        for i in range(len(keys_with_index)):
            keys.append(keys_with_index[i][1])
        keys.append('count')
        return keys


def get_keys(request_fields):
    """
    Try to get certain fields from request.GET
    """
    list_of_fields = ['name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender',
                      'homeworld', 'date']
    keys = []
    for i in range(len(list_of_fields)):
        if request_fields.get(list_of_fields[i]):
            keys.append((i, list_of_fields[i]))
    if len(keys) == 0:
        raise KeyError("Can't find fields. You must use them")
    return keys




def aggregate_csv(file_output, keys: list):
    """
    Aggregate csv file output using keys
    """

    key_length = len(keys)
    key = []
    for i in range(key_length):
        key.append(keys[i][1])

    if key_length > 1:
        aggregate_results = petl.aggregate(file_output, key=key, aggregation=len, )
    elif key_length == 1:
        aggregate_results = petl.aggregate(file_output, key=key[0], aggregation=len, )
    results = []
    for row in aggregate_results:
        results.append(row)

    return results
