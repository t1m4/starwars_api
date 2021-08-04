import logging
import math
import time

import requests

from swapi.utils.petl_utils import CSVWriter

logger = logging.getLogger('starwars.console_logger')


class StarwarsApi:
    PEOPLE_URL = 'https://swapi.dev/api/people'
    PAGE_TIMEOUT = None  # None or int

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

    def get_people_urls(self):
        """
        Get all people pages url. Make it only one time
        """
        response = self.__get_json(self.PEOPLE_URL)
        count_in_first = len(response['results'])
        count_of_person = response['count']
        count_of_pages = math.ceil(count_of_person / count_in_first)

        return [(self.PEOPLE_URL + "?page=" + str(i)) for i in range(1, count_of_pages + 1)]

    def get_people_list(self):
        """
        Get all people from all pages
        """
        urls = self.get_people_urls()
        for url in urls:
            response = self.__get_json(url)
            if response:
                results = response['results']
                yield results

    def get_person_information(self, films: list, type: str):
        """
        Get person films, species, vehicles and starships
        """
        types = {
            'films': 'title',
            'species': 'name',
            'vehicles': 'name',
            'starships': 'name',
        }
        field = types[type]
        results = []
        for film_url in films:
            response = self.__get_json(film_url)
            if response:
                results.append(response[field])
        return results


def people_dataset():
    api_client = StarwarsApi()
    for page in api_client.get_people_list():
        for person in page:
            result = {}
            result['name'] = person.get('name')
            result['height'] = person.get('height')
            result['mass'] = person.get('mass')
            result['hair_color'] = person.get('hair_color')
            result['skin_color'] = person.get('skin_color')
            result['eye_color'] = person.get('eye_color')
            result['gender'] = person.get('gender')
            result['films'] = api_client.get_person_information(person.get('films'), type='films')
            result['species'] = api_client.get_person_information(person.get('species'), type='species')
            result['starships'] = api_client.get_person_information(person.get('starships'), type='starships')
            yield result


if __name__ == '__main__':
    csv_writer = CSVWriter()
    for person in people_dataset():
        print(person)
        csv_writer.write('../../example.csv', person)
