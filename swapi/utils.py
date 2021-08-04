import json
import logging
from typing import List

import petl
import requests

from starwars.settings import PAGE_TIMEOUT

logger = logging.getLogger('starwars.console_logger')


def get_json(url: str):
    """
    Get json content from url
    """
    try:
        r = requests.get(url, timeout=PAGE_TIMEOUT)
    except:
        logger.info('Something wrong with %s' % url)
        return None
    if r.status_code == 200:
        content = r.json()
        return content


def get_page_persons(url: str) -> (List, str):
    response = get_json(url)
    if response:
        for person in response['results']:
            # change homeworld
            homeworld_response = get_json(person['homeworld'])
            if homeworld_response:
                person['homeworld'] = homeworld_response['name']
            else:
                person['homeworld'] = None
            # change edited date
            person['date'] = person['edited'][:10]
            # delete
            del person['films']
            del person['species']
            del person['vehicles']
            del person['starships']
            del person['edited']
            del person['created']
            del person['url']
        return (response['results'], response['next'])
    else:
        return ([], "")


def write_to_csv(filename, array: list):
    total_result = []
    for i in range(len(array)):
        total_result.extend(array[i])
    table = petl.fromdicts(total_result, header=total_result[0].keys())
    petl.tocsv(table, filename)
    return len(total_result)

if __name__ == '__main__':
    with open("../tests/data/full.json", 'r') as f:
        r = json.load(f)

    # test many pages
    # for i in range(10):
    #     r.extend([r[0]])
    write_to_csv("../example.csv", r)
