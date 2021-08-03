import json
import logging
from typing import List

import requests

logger = logging.getLogger('starwars.console_logger')


def get_json(url: str):
    """
    Get json content from url
    """
    try:
        r = requests.get(url)
    except:
        logger.info('Something wrong with %s' % url)
        return None
    if r.status_code == 200:
        content = r.json()
        return content


def get_page_persons(url: str) -> (List, str):
    response = get_json(url)
    if response:
        for result in response['results']:
            # change homeworld
            homeworld_response = get_json(result['homeworld'])
            result['homeworld'] = homeworld_response['name']
            # change edited date
            result['date'] = result['edited'][:10]
            # delete
            del result['films']
            del result['species']
            del result['vehicles']
            del result['starships']
            del result['edited']
            del result['created']
            del result['url']
        return (response['results'], response['next'])
    else:
        return ([], "")


def write_file(filename, content):
    with open(filename, "w") as f:
        json.dumps({"results": content})
