import datetime
import logging
import math
import time

import celery.exceptions
from celery import shared_task, group, chord

from starwars.settings import PEOPLE_URL
from swapi.models import File
from swapi.utils.celery_utils import get_json, get_page_persons, write_to_csv

logger = logging.getLogger('starwars.console_logger')


@shared_task
def get_each_page(url):
    result, next = get_page_persons(url)
    return result


@shared_task
def save_in_csv(result):
    filename = 'static/people' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + '.csv'
    count = write_to_csv(filename, result)
    logger.info('Write to file '+ filename)
    File.objects.create(filename=filename, count_of_pages=count)
    return filename


def get_count_of_page():
    response = get_json(PEOPLE_URL)
    count_in_first = len(response['results'])
    count_of_person = response['count']
    count_of_pages = math.ceil(count_of_person / count_in_first)
    return count_of_pages

def main_start():
    start_time = time.time()

    count_of_pages = get_count_of_page()
    tasks = group(get_each_page.s(PEOPLE_URL + "?page=" + str(i)) for i in range(1, count_of_pages + 1))
    callback = save_in_csv.s()
    c = chord(tasks, callback)()
    try:
        total_results = c.get(timeout=10)
    except celery.exceptions.TimeoutError:
        total_results = []

    print(time.time() - start_time)
    return total_results



@shared_task
def get_people_periodic():
    logger.info("Start task for collecting people")

    count_of_pages = get_count_of_page()

    tasks = group(get_each_page.s(PEOPLE_URL + "?page=" + str(i)) for i in range(1, count_of_pages + 1))
    callback = save_in_csv.s()
    chord(tasks, callback)()
