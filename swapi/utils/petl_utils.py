import logging
import os
import time
from pathlib import Path

import petl
from django.conf import settings

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
    def file_generator(self, file):
        k = 0
        for line in file:
            yield k, line
            k += 1

    def read(self, filename: str, start_from_line: int = 1):
        file = open(filename, "r")
        result_lines = []
        for i, line in self.file_generator(file):
            if i < start_from_line:
                continue
            elif i >= start_from_line + 10:
                break
            else:
                line = line.strip().split(':')
                result_lines.append(line)
        return result_lines


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


if __name__ == '__main__':
    start_time = time.time()
    # filename = Path(__file__).resolve().parent / "small_file.csv"
    # filename = Path(__file__).resolve().parent / "big_file_delimiter.csv"
    filename = Path(__file__).resolve().parent / "small_file_delimiter.csv"
    r = read_file_from_csv_quickly(filename, 2000000)
    print(time.time() - start_time, r)
