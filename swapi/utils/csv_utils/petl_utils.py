import logging
import os
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple, Union

import petl
from django.conf import settings

from swapi.constants import ALLOWED_PERSON_FIELDS
from swapi.utils.csv_utils.exceptions import (
    EmptyPage,
    FileNotExist,
    PageNotAnPositiveInteger,
)

logger = logging.getLogger("starwars.console_logger")
DEFAULT_DELIMITER = ";"


class CSVWriter:
    def write(self, filename: str, content: Dict):
        """Write any dict to csv file. If it doesn't exist then create it with headers

        Args:
            filename (str): name of file
            content (Dict): Any Dict with content
        """
        filename = settings.STATICFILES_DIRS[0] + filename
        list_content = [content]
        table = petl.fromdicts(list_content, header=list_content[0].keys())
        exist = os.path.exists(filename)
        if exist:
            petl.appendcsv(table, filename, delimiter=DEFAULT_DELIMITER)
        else:
            petl.appendcsv(table, filename, delimiter=DEFAULT_DELIMITER, write_header=True)


class CSVReader:
    MAX_PAGE_SIZE = 10
    DEFAULT_START_LINE = 1

    def read_file(self, filename: str) -> Iterable:
        exist = os.path.exists(filename)
        if not exist:
            raise FileNotExist("File does not exist")

        file = open(filename, "r")
        index = 0
        for line in file:
            yield index, line
            index += 1

    def read_file_from_line(self, filename: str, page_size: int, start_line: int) -> List[List[str]]:
        """Read certain line from file

        Args:
            filename (str): name of file
            page_size (int): lenght of page
            start_line (int): first line to read
        Returns:
            List[List[str]]: list of row person
        """
        filename = settings.STATICFILES_DIRS[0] + filename
        result_lines = []
        for index, line in self.read_file(filename):
            if index < start_line:
                continue
            elif index >= start_line + page_size:
                break
            else:
                line = line.strip().split(DEFAULT_DELIMITER)
                result_lines.append(line)
        return result_lines

    def read_with_pagination(
        self, filename: str, count_of_lines: int, page: int, page_size: Union[int, None] = None
    ) -> List[List[str]]:
        """Read from given CSV file with pagination

        Args:
            filename (str): name of file
            count_of_lines (int): number of people in file
            page (int): number of page given by user
            page_size (int): lenght of page
        Raises:
            PageNotAnPositiveInteger: If `page` not positive number
            EmptyPage: If `page` more than count_of_lines

        Returns:
            List[List[str]]: list of persons
        """
        if page < 1:
            raise PageNotAnPositiveInteger("Page is not an positive number")

        page_size = page_size or self.MAX_PAGE_SIZE
        page_size = page_size if page_size < self.MAX_PAGE_SIZE else self.MAX_PAGE_SIZE
        start_line = (page - 1) * page_size + 1

        # If there are more lines than people count
        if start_line > count_of_lines:
            raise EmptyPage("Can't find page")

        return self.read_file_from_line(filename, start_line=start_line, page_size=page_size)

    def read_with_fields_combination(self, filename: str, fields: List[str]):
        """Read from given CSV file only give fields. Count the occurrences of values (combination of values) for fields

        Args:
            filename (str): name of file
            fields (List[str]): fields
        Returns:
            List[List[str]]: List of unique fields values and each unique fields occurrences count
        """
        fields_with_indexes: List[Tuple[int, str]] = self.__add_fields_indexes(fields)
        filename = settings.STATICFILES_DIRS[0] + filename
        occurrences_count: Dict[Tuple, int] = defaultdict(int)
        for index, line in self.read_file(filename):
            if index == 0:
                continue

            line_as_list = line.strip().split(DEFAULT_DELIMITER)
            fields_values = []
            for field in fields_with_indexes:
                fields_values.append(line_as_list[field[0]])
            tuple_field_values = tuple(fields_values)
            occurrences_count[tuple_field_values] += 1

        return self.__to_list(occurrences_count, fields)

    @staticmethod
    def __add_fields_indexes(initial_fields: List[str]) -> List[Tuple[int, str]]:
        """Add indexes to the fields.

        Args:
            initial_fields (List[str]): fields
        Returns:
            List[Tuple[int, str]]: fields with the indexes like [(0, 'name'), ...]

        """
        result_fields: List[Tuple[int, str]] = []
        for index, field_name in enumerate(ALLOWED_PERSON_FIELDS):
            if field_name in initial_fields:
                result: Tuple[int, str] = (index, field_name)
                result_fields.append(result)
        return result_fields

    def __to_list(self, occurrences_count: Dict[Tuple, int], initial_fields: List[str]) -> List[List[str]]:
        """Change Dict[Tuple, int] to List[List[str]]. And first row with fields name

        Args:
            occurrences_count: (Dict[Tuple, int]): dict of fields count
            initial_fields (List[str]): fields
        Returns:
            List[List[str]]: List of unique fields values and each unique fields occurrences count
        """
        initial_fields.extend(["count"])
        list_result = [initial_fields]

        for field_values, field_values_count in occurrences_count.items():
            row_list = list(field_values)
            row_list.append(field_values_count)
            list_result.append(row_list)
        return list_result
