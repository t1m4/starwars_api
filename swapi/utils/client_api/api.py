import logging

import requests
import simplejson
from simplejson import JSONDecodeError

from swapi.utils.client_api.exceptions import ClientAPIException
from swapi.utils.petl_utils import CSVWriter

logger = logging.getLogger('starwars.console_logger')


class ClientAPI:
    PEOPLE_URL = 'https://swapi.dev/api/people'
    FIlM_URL = 'https://swapi.dev/api/films/{id}/'
    SPECIE_URL = 'https://swapi.dev/api/species/{id}/'
    VEHICLE_URL = 'https://swapi.dev/api/vehicles/{id}/'
    STARSHIP_URL = 'https://swapi.dev/api/starship/{id}/'

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
            response = requests.get(url, params=params, timeout=timeout)
        except requests.exceptions.RequestException as error:
            raise ClientAPIException(error.args[0], 500)

        if response.status_code == 200:
            return self.__make_json(response)
        else:
            raise ClientAPIException("Invalid status code", response.status_code)

    def __make_json(self, response: requests.Response):
        try:
            return response.json()
        except simplejson.errors.JSONDecodeError as error:
            raise ClientAPIException(error.args[0])

    def get_people_list(self, start_page: int = 1, end_page: int = 100):
        """
        Get all people from all pages
        """
        result = []

        for page_number in range(start_page, end_page + 1):
            page = self.__get_json(self.PEOPLE_URL, params={'page': page_number})
            result.extend(page['results'])
            if not page['next']:
                break
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
            except ClientAPIException as error:
                logger.info(error)
                continue
            else:
                results.append(response[field])
        return results


    def get_film_by_id(self, id: int):
        url = self.FIlM_URL.format(id=id)
        return self.__get_json(url)

    def get_specie_by_id(self, id: int):
        url = self.SPECIE_URL.format(id=id)
        return self.__get_json(url)

    def get_vehicle_by_id(self, id: int):
        url = self.VEHICLE_URL.format(id=id)
        return self.__get_json(url)

    def get_starship_by_id(self, id: int):
        url = self.STARSHIP_URL.format(id=id)
        return self.__get_json(url)

def people_dataset():
    api_client = ClientAPI()
    for person in api_client.get_people_list(1, 10):
        result = {}
        result['name'] = person.get('name')
        result['height'] = person.get('height')
        result['mass'] = person.get('mass')
        result['hair_color'] = person.get('hair_color')
        result['skin_color'] = person.get('skin_color')
        result['eye_color'] = person.get('eye_color')
        result['gender'] = person.get('gender')
        result['films'] = api_client.get_film_by_id(person.get('films'), type='films')
        result['species'] = api_client.get_person_information(person.get('species'), type='species')
        result['starships'] = api_client.get_person_information(person.get('starships'), type='starships')
        yield result


if __name__ == '__main__':
    # csv_writer = CSVWriter()
    # for person in people_dataset():
    #     print(person)
    #     csv_writer.write('../../example.csv', person)
    api = ClientAPI()
