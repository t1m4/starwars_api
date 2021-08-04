import logging
import os

import petl
from django.conf import settings

logger = logging.getLogger('starwars.console_logger')


class CSVWriter():
    def write(self, filename: str, content: dict):
        content = [content]
        table = petl.fromdicts(content, header=content[0].keys())
        exist = os.path.exists(filename)
        if exist:
            petl.appendcsv(table, filename)
        else:
            petl.appendcsv(table, filename, write_header=True)


def write_to_csv(filename: str, array: list):
    """
    Change from matrix to array and save it in CSV
    """
    total_result = []
    for i in range(len(array)):
        total_result.extend(array[i])
    table = petl.fromdicts(total_result, header=total_result[0].keys())
    petl.tocsv(table, settings.STATICFILES_DIRS[0] + filename)
    return len(total_result)


def get_list_from_csv(filename):
    """
    Load all persons from csv
    """
    t = petl.fromcsv(filename)
    return list(petl.data(t))


if __name__ == '__main__':
    d = {'hello': 1, 'world': []}
    csv_writer = CSVWriter()
    csv_writer.write('example.csv', d)
