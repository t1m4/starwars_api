import json
import logging

import petl
from django.conf import settings

logger = logging.getLogger('starwars.console_logger')


def write_to_csv(filename, array: list):
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
    with open("../../tests/data/full.json", 'r') as f:
        r = json.load(f)

    # test many pages
    # for i in range(10):
    #     r.extend([r[0]])
    write_to_csv("../../example.csv", r)
