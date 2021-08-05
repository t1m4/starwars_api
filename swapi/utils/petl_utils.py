import logging
import os

import petl
from django.conf import settings

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
            petl.appendcsv(table,  filename)
        else:
            petl.appendcsv(table,  filename, write_header=True)



def get_list_from_csv(filename):
    """
    Load all persons from csv
    """
    filename = settings.STATICFILES_DIRS[0] + filename
    t = petl.fromcsv(filename)
    return list(petl.data(t))


if __name__ == '__main__':
    d = {'hello': 1, 'world': []}
    csv_writer = CSVWriter()
    csv_writer.write('../../example.csv', d)
