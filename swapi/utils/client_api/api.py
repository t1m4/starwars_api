import logging
import re
from json import JSONDecodeError
from typing import Any, Dict, Iterable, List, Tuple, Union

import requests

from swapi.utils.client_api.exceptions import ClientAPIException
from swapi.utils.csv_utils.petl_utils import CSVWriter

logger = logging.getLogger("starwars.console_logger")


class ClientAPI:
    PEOPLE_URL = "https://swapi.dev/api/people"

    PAGE_TIMEOUT = None
    TYPES_OF_TOOL_FIELDS = {
        "films": "title",
        "species": "name",
        "vehicles": "name",
        "starships": "name",
        "homeworld": "name",
    }
    TYPES_OF_TOOL_URL = {
        "films": "https://swapi.dev/api/films/{id}/",
        "species": "https://swapi.dev/api/species/{id}/",
        "vehicles": "https://swapi.dev/api/vehicles/{id}/",
        "starships": "https://swapi.dev/api/starships/{id}/",
        "homeworld": "https://swapi.dev/api/planets/{id}/",
    }

    def __get_json(self, url: str, params: Union[Dict, None] = None, timeout: Union[int, None] = None) -> Dict:
        """Get json content from url"""
        try:
            response = requests.get(url, params=params, timeout=timeout)
        except requests.exceptions.RequestException as error:
            raise ClientAPIException(error.args[0], 500)

        if response.status_code == 200:
            return self.__make_json(response)
        else:
            raise ClientAPIException("Invalid status code", response.status_code)

    def __make_json(self, response: requests.Response) -> Dict:
        try:
            return response.json()
        except JSONDecodeError as error:
            raise ClientAPIException(error.args[0])

    def get_page_by_number(self, page_number: int) -> Dict:
        """Get page by given number"""
        page = self.__get_json(self.PEOPLE_URL, params={"page": page_number})
        return page

    def get_person_tool_by_id(self, id: int, type_of_tool: str) -> Dict:
        """Get person tool by id"""
        try:
            url = self.TYPES_OF_TOOL_URL[type_of_tool]
        except KeyError:
            raise ValueError("Can't find type of person tool: " + type_of_tool)
        url = url.format(id=id)
        return self.__get_json(url)

    def get_person_tools(self, ids: List, type_of_tool: str) -> List[Dict]:
        """Get person films, species, vehicles and starships"""
        try:
            field = self.TYPES_OF_TOOL_FIELDS[type_of_tool]
        except KeyError:
            raise ValueError("Can't find type of person tool: " + type_of_tool)

        results = []
        for id in ids:
            response = self.get_person_tool_by_id(id, type_of_tool)
            results.append(response[field])
        return results


def get_id_from_url(url: str) -> int:
    """Get object id from given url"""
    id_pattern = r"/(\d+)/?$"
    result = re.search(id_pattern, url)
    if result:
        return int(result.group(1))
    else:
        raise ValueError("Can't find id in url")


def get_all_person_tool_ids(urls: List) -> List[int]:
    """
    Get list of ids from list of urls
    """
    result = []
    for url in urls:
        id = get_id_from_url(url)
        result.append(id)
    return result


def retry(exception, function, func_args) -> Tuple[bool, Any]:
    """Try to call function again and check results"""
    try:
        result = function(*func_args)
        return True, result
    except exception as error:
        logger.error(error)
        return False, None


def get_tools(api_client: ClientAPI, urls: List, type: str):
    """Get each types of tools"""
    ids: List = []
    try:
        ids = get_all_person_tool_ids(urls)
        return api_client.get_person_tools(ids, type)
    except ClientAPIException as error:
        logger.warning(error)
        answer, tools = retry(ClientAPIException, api_client.get_person_tools, (ids, type))
        if answer is False:
            return []
        else:
            return tools


def get_people_from_page(data: List, api_client: ClientAPI) -> Iterable:
    """Return people from page one by one"""
    for person in data:
        result = {}
        result["name"] = person.get("name")
        result["height"] = person.get("height")
        result["mass"] = person.get("mass")
        result["hair_color"] = person.get("hair_color")
        result["skin_color"] = person.get("skin_color")
        result["eye_color"] = person.get("eye_color")
        result["birth_year"] = person.get("birth_year")
        result["gender"] = person.get("gender")

        homeworld_id = get_id_from_url(person.get("homeworld"))
        field = api_client.TYPES_OF_TOOL_FIELDS["homeworld"]
        result["homeworld"] = api_client.get_person_tool_by_id(homeworld_id, "homeworld")[field]
        result["date"] = person.get("edited")[:10]

        result["films"] = get_tools(api_client, person.get("films", []), type="films")
        result["species"] = get_tools(api_client, person.get("species", []), type="species")
        result["vehicles"] = get_tools(api_client, person.get("vehicles", []), type="vehicles")
        result["starships"] = get_tools(api_client, person.get("starships", []), type="starships")

        yield result


def people_dataset():
    """Collect people and its' tools page by page"""
    api_client = ClientAPI()

    page_number = 1
    while True:
        try:
            page = api_client.get_page_by_number(page_number)
        except ClientAPIException as error:
            logger.warning(error)
            answer, page = retry(ClientAPIException, api_client.get_page_by_number, (page_number,))
            if answer is False:
                break

        yield from get_people_from_page(page["results"], api_client)
        if not page["next"]:
            break
        page_number += 1


if __name__ == "__main__":
    csv_writer = CSVWriter()

    for person in people_dataset():
        csv_writer.write("../../example.csv", person)
