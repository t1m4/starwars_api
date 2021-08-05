import logging
import re

import requests
import simplejson

from swapi.utils.client_api.exceptions import ClientAPIException
from swapi.utils.petl_utils import CSVWriter

logger = logging.getLogger('starwars.console_logger')


class ClientAPI:
    PEOPLE_URL = 'https://swapi.dev/api/people'

    PAGE_TIMEOUT = None
    TYPES_OF_TOOL_FIELDS = {
        'films': 'title',
        'species': 'name',
        'vehicles': 'name',
        'starships': 'name',
    }
    TYPES_OF_TOOL_URL = {
        'films': 'https://swapi.dev/api/films/{id}/',
        'species': 'https://swapi.dev/api/species/{id}/',
        'vehicles': 'https://swapi.dev/api/vehicles/{id}/',
        'starships': 'https://swapi.dev/api/starships/{id}/',
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

    def get_person_tool_by_id(self, id: int, type_of_tool: str):
        try:
            url = self.TYPES_OF_TOOL_URL[type_of_tool]
        except:
            raise ValueError("Can't find type of person tool: " + type_of_tool)
        url = url.format(id=id)
        return self.__get_json(url)

    def get_person_tools(self, ids: list, type_of_tool: str):
        """
        Get person films, species, vehicles and starships
        """
        try:
            field = self.TYPES_OF_TOOL_FIELDS[type_of_tool]
        except:
            raise ValueError("Can't find type of person tool: " + type_of_tool)

        results = []
        for id in ids:
            response = self.get_person_tool_by_id(id, type_of_tool)
            results.append(response[field])
        return results


def get_id_from_url(url: str):
    """
    Get object id from given url
    :param url:
    :return:
    """
    id_pattern = r'/(\d+)/?$'
    result = re.search(id_pattern, url)
    if result:
        return int(result.group(1))
    else:
        # TODO what if don't find it. Are you sure about it?
        raise ValueError("Can't find id in url")


def get_all_person_tool_ids(films_url: list):
    """
    Get list of ids from list of urls
    """
    result = []
    for i in films_url:
        id = get_id_from_url(i)
        result.append(id)
    return result


def people_dataset():
    api_client = ClientAPI()
    try:
        data = api_client.get_people_list(1, 10)
    except ClientAPIException as error:
        return

    for person in data:
        result = {}
        result['name'] = person.get('name')
        result['height'] = person.get('height')
        result['mass'] = person.get('mass')
        result['hair_color'] = person.get('hair_color')
        result['skin_color'] = person.get('skin_color')
        result['eye_color'] = person.get('eye_color')
        result['gender'] = person.get('gender')

        film_ids = get_all_person_tool_ids(person.get('films'))
        result['films'] = api_client.get_person_tools(film_ids, type_of_tool='films')

        species_ids = get_all_person_tool_ids(person.get('species'))
        result['species'] = api_client.get_person_tools(species_ids, type_of_tool='species')

        vehicles_ids = get_all_person_tool_ids(person.get('vehicles'))
        result['vehicles'] = api_client.get_person_tools(vehicles_ids, type_of_tool='vehicles')

        starships_ids = get_all_person_tool_ids(person.get('starships'))
        result['starships'] = api_client.get_person_tools(starships_ids, type_of_tool='starships')
        yield result


if __name__ == '__main__':
    csv_writer = CSVWriter()
    for person in people_dataset():
        print(person)
        csv_writer.write('../../example.csv', person)
