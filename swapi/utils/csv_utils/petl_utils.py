import logging
import os

import petl
from django.conf import settings

from swapi.utils.csv_utils.exceptions import EmptyPage, PageNotAnPositiveInteger

logger = logging.getLogger('starwars.console_logger')


class CSVWriter():
    def write(self, filename: str, content: dict):
        """
        Write any dict to csv file. If it doesn't exist then create it with headers
        """
        # filename = settings.STATICFILES_DIRS[0] + filename
        filename = filename
        content = [content]
        table = petl.fromdicts(content, header=content[0].keys())
        exist = os.path.exists(filename)
        # petl.appendcsv(table, filename, write_header=not exist)
        if exist:
            petl.appendcsv(table, filename, delimiter=":")
        else:
            petl.appendcsv(table, filename, delimiter=":", write_header=True)


class CSVReader():
    MAX_PAGE_SIZE = 10

    def __file_generator(self, filename):
        file = open(filename, "r")
        index = 0
        for line in file:
            yield index, line
            index += 1

    def __read(self, filename: str, max_page_size: int, start_from_line: int = 1):
        """
        Read curtain line from file
        """
        filename = settings.STATICFILES_DIRS[0] + filename
        result_lines = []
        for index, line in self.__file_generator(filename):
            if index < start_from_line:
                continue
            elif index >= start_from_line + max_page_size:
                break
            else:
                line = line.strip().split(':')
                result_lines.append(line)
        return result_lines

    def pagination_read(self, filename: str, count_of_people: int, page: int, max_page_size: int = None):
        """
        Read from give CSV file
        :param count_of_people: count of people in file
        :param page: number of page given by use
        :param max_page_size: max page size in pagination
        """
        if page < 1:
            raise PageNotAnPositiveInteger('Page is not an positive number')

        max_page_size = max_page_size or self.MAX_PAGE_SIZE
        start_from_line = (page - 1) * max_page_size + 1

        # If there are more lines than people
        if start_from_line > count_of_people:
            raise EmptyPage("Can't find page")

        result = self.__read(filename, start_from_line=start_from_line, max_page_size=self.MAX_PAGE_SIZE)
        return result


def get_list_from_csv(filename):
    """
    Load all persons from csv
    """
    filename = settings.STATICFILES_DIRS[0] + filename
    exist = os.path.exists(filename)
    if exist:
        t = petl.fromcsv(filename)
        return list(petl.data(t))
    else:
        return []
