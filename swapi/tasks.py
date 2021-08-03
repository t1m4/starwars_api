import datetime
import logging
import math
import time
from pprint import pprint

import requests
from celery import shared_task, group, chord

from starwars.settings import PEOPLE_URL
from swapi.utils import get_json, get_page_persons, write_file

logger = logging.getLogger('starwars.console_logger')


@shared_task
def get_each_page(url):
    response = get_json(url)
    return len(response['results'])


@shared_task
def get_each_person_homeworld(res):
    logger.info("I am getting each hoemworld " + str(len(res)))



def main_start():
    logger.info("I'm just starting")
    total_results = []
    response = get_json(PEOPLE_URL)
    total_results.extend(response['results'])
    count_in_first = len(response['results'])
    count_of_person = response['count']
    count_of_pages = math.ceil(count_of_person / count_in_first)
    print(count_of_pages)

    g = group(get_each_page.s(PEOPLE_URL + "?page=" + str(i)) for i in range(2, count_of_pages + 1))()
    while not g.ready():
        print('ready', g.ready(), g.successful())
        print()
    # result = (group(get_each_page.s(PEOPLE_URL + "?page=" + str(i)) for i in range(2, count_of_pages + 1)) | get_each_person_homeworld.s())()
    # print(result)
    # c = chord(group(get_each_page.s(PEOPLE_URL + "?page=" + str(i)) for i in range(2, count_of_pages + 1)), get_each_person_homeworld.s())()
    # print("helo", c)


    return total_results



@shared_task
def get_people():
    start_time = time.time()
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
