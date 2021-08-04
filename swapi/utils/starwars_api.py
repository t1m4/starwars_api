import logging
import math
import time
from typing import List

import requests

logger = logging.getLogger('starwars.console_logger')


class StarwarsApi:
    PEOPLE_URL = 'https://swapi.dev/api/people'
    PAGE_TIMEOUT = None  # None or int

    def get_page_persons(self, url: str) -> (List, str):
        """
        Get each page people only with required information.
        """
        response = self.__get_json(url)
        if response:
            for person in response['results']:
                # change homeworld
                homeworld_response = self.__get_json(person['homeworld'])
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
            return response['results']
        else:
            return []

    def get_people_urls(self, function):
        """
        Get all people pages url
        """
        response = self.__get_json(self.PEOPLE_URL)
        count_in_first = len(response['results'])
        count_of_person = response['count']
        count_of_pages = math.ceil(count_of_person / count_in_first)

        return [function.s(self.PEOPLE_URL + "?page=" + str(i)) for i in range(1, count_of_pages + 1)]

    def __get_json(self, url: str):
        """
        Get json content from url
        """
        try:
            r = requests.get(url, timeout=self.PAGE_TIMEOUT)
        except:
            logger.info('Something wrong with %s' % url)
            return None

        if r.status_code == 200:
            content = r.json()
            return content
        else:
            logger.info(f'Status code for {url}: {r.status_code}')


if __name__ == '__main__':
    s = StarwarsApi()
    start_time = time.time()
    r = s.get_people_urls()
    print(r)
    print(time.time() - start_time)
