import csv
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

def rows_from_csv_file(filename, skip_first_line=True):
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        if skip_first_line:
            next(reader, None)
        for row in reader:
            yield row


def csv_reader(filename):
    for row in open(settings.STATICFILES_DIRS[0] + filename, "r"):
        yield row


def read_csv_file(filename: str, skip: int, count: int = 10):
    """
    Simple read file
    """
    result = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        # ship first line
        next(reader, None)
        # ship lines
        while reader.line_num != skip + 1:
            next_line = next(reader, None)
            if not next_line:
                break
        k = 1
        for row in reader:
            # print(row, len(row))
            if k >= count:
                break
            result.append(row)
            k += 1

    return result
from itertools import dropwhile


def tool_function(x, start_from_line):
    print(x)
    return x[0] < start_from_line
def iterate_from_line(f, start_from_line):
    for i, l in enumerate(f):
        if i < start_from_line:
            continue
        elif i >= start_from_line + 10:
            break
        else:
            print(i, len(l.strip().split(':')), l )

    return (l for i, l in dropwhile(lambda x: x[0] < start_from_line and x[0] > start_from_line + 10, enumerate(f)))
    # return (l for i, l in dropwhile(lambda x: tool_function(x, start_from_line), enumerate(f)))




def read_csv_file_quickly(filename):
    file = open(filename, "r")
    for line in iterate_from_line(file, 0):
        pass
if __name__ == '__main__':
    # 0.0008
    # start_time = time.time()
    # filename = Path(__file__).resolve().parent / "small_file.csv"
    # r = read_csv_file(filename, 90)
    # print(time.time() - start_time, r)

    # 0.0031
    start_time = time.time()
    filename = Path(__file__).resolve().parent / "big_file.csv"
    r = read_csv_file(filename, 1000)
    print(time.time() - start_time, r)


    start_time = time.time()
    filename = Path(__file__).resolve().parent / "small_file.csv"
    filename = Path(__file__).resolve().parent / "big_file_delimiter.csv"
    r = read_csv_file_quickly(filename)
    print(time.time() - start_time, r)
