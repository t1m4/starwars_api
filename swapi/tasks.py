import logging
import random
import string

from celery import shared_task

from swapi.models import File
from swapi.utils.csv_utils.petl_utils import CSVWriter
from swapi.utils.client_api.api import people_dataset

logger = logging.getLogger('starwars.console_logger')



@shared_task
def task_get_all_in_csv():
    csv_writer = CSVWriter()
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
    filename = f'people_{random_string}.csv'

    count = 0
    for person in people_dataset():
        csv_writer.write(filename, person)
        count += 1
    File.objects.create(filename=filename, count_of_people=count)
