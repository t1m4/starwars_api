import logging

import requests

from swapi.utils.client_api.exceptions import ClientAPIException
from swapi.utils.petl_utils import CSVWriter

logger = logging.getLogger('starwars.console_logger')


class ClientAPI:
    PEOPLE_URL = 'https://swapi.dev/api/people'
    PAGE_TIMEOUT = None
    PERSON_INFO_TYPES = {
        'films': 'title',
        'species': 'name',
        'vehicles': 'name',
        'starships': 'name',
    }

    def __get_json(self, url: str, params=None, timeout=None):
        """
        Get json content from url
        """
        try:
            r = requests.get(url, params=params, timeout=timeout)
        except requests.exceptions.RequestException as e:
            raise ClientAPIException(500, e.args[0])

        if r.status_code == 200:
            return r.json()
        else:
            raise ClientAPIException(r.status_code, "Invalid status code")

    def get_people_list(self, start: int = 1, end: int = 100):
        """
        Get all people from all pages
        """
        result = []
        page_number = 1

        while True:
            try:
                page = self.__get_json(self.PEOPLE_URL, params={'page': page_number})
            except ClientAPIException as e:
                # or check status code and decide what do you need to do next
                logger.info(e)
                break
            result.extend(page['results'])
            if not page['next']:
                break
            page_number += 1
        return result

    def get_person_information(self, info_urls: list, type: str):
        """
        Get person films, species, vehicles and starships
        """

        field = self.PERSON_INFO_TYPES[type]
        results = []
        for url in info_urls:
            try:
                response = self.__get_json(url)
            except ClientAPIException as e:
                logger.info(e)
                continue
            else:
                results.append(response[field])
        return results


def people_dataset():
    api_client = ClientAPI()
    for person in api_client.get_people_list():
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
