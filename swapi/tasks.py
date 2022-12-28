import asyncio

from celery import shared_task

from external_api.starwars_api.services import save_people_in_csv
from swapi.models import File


@shared_task
def task_get_all_in_csv():
    filename, people_count = asyncio.run(save_people_in_csv())
    File.objects.create(filename=filename, count_of_people=people_count)
