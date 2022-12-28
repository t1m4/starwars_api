import asyncio
import logging
import random
import re
import string
from typing import Any, AsyncGenerator, Dict, List, Tuple, Union

import aiohttp

from external_api.starwars_api.api import AsyncAPIClient
from external_api.starwars_api.async_utils import async_timed
from external_api.starwars_api.exceptions import ClientAPIException
from swapi.models import File
from swapi.utils.csv_utils.petl_utils import CSVWriter


def get_id_from_url(url: str) -> int:
    """Get object id from given url"""
    id_pattern = r"/(\d+)/?$"
    result = re.search(id_pattern, url)
    if result:
        return int(result.group(1))
    else:
        raise ValueError("Can't find id in url")


def get_all_person_tool_ids(urls: List) -> List[int]:
    """Get list of ids from list of urls"""
    result = []
    for url in urls:
        id = get_id_from_url(url)
        result.append(id)
    return result


async def retry(exception, function, func_args) -> Tuple[bool, Any]:
    """Try to call function again and check results"""
    try:
        result = await function(*func_args)
        return True, result
    except exception as error:
        logging.error(error)
        return False, None


async def get_tools(api_client: AsyncAPIClient, urls: List, type: str) -> Tuple[str, List[Any]]:
    """Get each types of tools"""
    ids = get_all_person_tool_ids(urls)
    return type, await api_client.get_person_tools(ids, type)


async def get_person_homeworld(api_client: AsyncAPIClient, person: Dict) -> Union[str, None]:
    """Get homeworld name"""
    homeworld_id = get_id_from_url(person["homeworld"])
    field = api_client.TYPES_OF_TOOL_FIELDS["homeworld"]
    try:
        result = await api_client.get_person_tool_by_id(homeworld_id, "homeworld")
        return result[field]
    except ClientAPIException as error:
        logging.error(error)
        return None


async def get_people_from_page(page_data: List[Dict], api_client: AsyncAPIClient) -> AsyncGenerator:
    """Return people from page one by one"""
    for person in page_data:
        result = {}
        result["name"] = person.get("name")
        result["height"] = person.get("height")
        result["mass"] = person.get("mass")
        result["hair_color"] = person.get("hair_color")
        result["skin_color"] = person.get("skin_color")
        result["eye_color"] = person.get("eye_color")
        result["birth_year"] = person.get("birth_year")
        result["gender"] = person.get("gender")
        result["date"] = person["edited"][:10]
        result['homeworld'] = await get_person_homeworld(api_client, person)

        # exclude homeworld
        tool_types = list(api_client.TYPES_OF_TOOL_FIELDS.keys())[:-1]
        # tool_types = ['films', 'species', 'vehicles']
        awaitables = [
            asyncio.create_task(get_tools(api_client, person.get(tool_type, []), type=tool_type))
            for tool_type in tool_types
        ]
        for task in awaitables:
            tool_type, tools = await task
            result[tool_type] = tools

        yield result


async def async_people_dataset() -> AsyncGenerator:
    """Collect people and its' tools page by page"""
    async with aiohttp.ClientSession() as session:
        api_client = AsyncAPIClient(session)
        page_number = 1
        while True:
            try:
                page = await api_client.get_page_by_number(page_number)
            except ClientAPIException as error:
                logging.error(error)
                answer, page = await retry(ClientAPIException, api_client.get_page_by_number, (page_number,))
                if answer is False:
                    break

            async for person in get_people_from_page(page["results"], api_client):
                yield person
            if not page["next"]:
                break
            page_number += 1


@async_timed()
async def save_people_in_csv() -> Tuple[str, int]:
    """Saving peoples into csv"""
    csv_writer = CSVWriter()
    random_string = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
    filename = f"people_{random_string}.csv"

    count = 0
    async for person in async_people_dataset():
        csv_writer.write(filename, person)
        count += 1
    return filename, count


def main():
    """Test main function"""
    filename, people_count = asyncio.run(save_people_in_csv())
    File.objects.create(filename=filename, count_of_people=people_count)


if __name__ == "__main__":
    main()
