import datetime
import logging
import math
import time

import celery.exceptions
from celery import shared_task, group, chord

from starwars.settings import PEOPLE_URL
from swapi.utils import get_json, get_page_persons, write_file, write_to_csv

logger = logging.getLogger('starwars.console_logger')


@shared_task
def get_each_page(url):
    result, next = get_page_persons(url)
    return result


@shared_task
def save_in_csv(result):
    filename = '/app/people' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + '.csv'
    write_to_csv(filename, result)
    logger.info('Write to file '+ filename)
    return filename


def main_start():
    start_time = time.time()

    total_results = []
    response = get_json(PEOPLE_URL)
    total_results.extend(response['results'])
    count_in_first = len(response['results'])
    count_of_person = response['count']
    count_of_pages = math.ceil(count_of_person / count_in_first)

    tasks = group(get_each_page.s(PEOPLE_URL + "?page=" + str(i)) for i in range(1, count_of_pages + 1))
    callback = save_in_csv.s()
    c = chord(tasks, callback)()
    try:
        total_results = c.get(timeout=10)
    except celery.exceptions.TimeoutError:
        pass
    print(time.time() - start_time)
    return total_results


@shared_task
def get_people():
    total_results = []

    result, next = get_page_persons(PEOPLE_URL)
    total_results.extend(result)

    while next:
        result, next = get_page_persons(next)
        total_results.extend(result)

    write_file('test.json', total_results)
    return total_results


@shared_task
def add(a, b):
    logger.info("hello")
    return a + b
