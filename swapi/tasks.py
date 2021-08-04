import logging
import random
import string
import time

import celery.exceptions
from celery import shared_task, group, chord

from swapi.models import File
from swapi.utils.petl_utils import write_to_csv
from swapi.utils.starwars_api import StarwarsApi

logger = logging.getLogger('starwars.console_logger')


@shared_task
def task_get_each_page(url):
    api = StarwarsApi()
    result = api.get_page_persons(url)
    return result


@shared_task
def save_in_csv(result):
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
    filename = f'people_{random_string}.csv'
    count = write_to_csv(filename, result)
    logger.info('Write to file ' + filename)
    File.objects.create(filename=filename, count_of_pages=count)
    return filename


def main_start():
    start_time = time.time()
    api = StarwarsApi()

    tasks = group(api.get_people_urls(task_get_each_page))
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
    api = StarwarsApi()
    tasks = group(api.get_people_urls(task_get_each_page))
    callback = save_in_csv.s()
    chord(tasks, callback)()
