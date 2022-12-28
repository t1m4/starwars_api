import asyncio
from typing import Dict, List, Union

import aiohttp

from external_api.starwars_api.async_utils import execute_until_first_exception
from external_api.starwars_api.exceptions import ClientAPIException


class AsyncAPIClient:
    PEOPLE_URL = "https://swapi.dev/api/people"

    DEFAULT_TIMEOUT = 10
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

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def __get_json(self, url: str, params: Union[Dict, None] = None, timeout: Union[int, None] = None) -> Dict:
        try:
            async with self.session.get(url, params=params, timeout=timeout) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ClientAPIException("Invalid status code", response.status)

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            raise ClientAPIException(str(error), 500)

    async def get_page_by_number(self, page_number: int) -> Dict:
        """Get page by given number"""
        page = await self.__get_json(self.PEOPLE_URL, params={"page": page_number})
        return page

    async def get_person_tool_by_id(self, id: int, type_of_tool: str) -> Dict:
        """Get person tool by id"""
        try:
            url = self.TYPES_OF_TOOL_URL[type_of_tool]
        except KeyError:
            raise ValueError("Can't find type of person tool: " + type_of_tool)
        url = url.format(id=id)
        return await self.__get_json(url, timeout=self.DEFAULT_TIMEOUT)

    async def get_person_tools(self, ids: List[int], type_of_tool: str) -> List[Dict]:
        """Get person films, species, vehicles and starships"""
        if ids == []:
            return []
        try:
            field = self.TYPES_OF_TOOL_FIELDS[type_of_tool]
        except KeyError:
            raise ValueError("Can't find type of person tool: " + type_of_tool)

        awaitables = [asyncio.create_task(self.get_person_tool_by_id(tool_id, type_of_tool)) for tool_id in ids]
        results = await execute_until_first_exception(awaitables, result_callback=lambda x: x[field])
        return results


async def test_main():
    session = aiohttp.ClientSession()
    try:
        api_client = AsyncAPIClient(session)
        print(await api_client.get_page_by_number(1))
    except ClientAPIException:
        pass
    finally:
        await session.close()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(test_main())
    finally:
        loop.close()
