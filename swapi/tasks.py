import logging
import random
import string

from celery import shared_task

from swapi.utils.petl_utils import CSVWriter
from swapi.utils.starwars_api import people_dataset

logger = logging.getLogger('starwars.console_logger')



@shared_task
def task_get_all_in_csv():
    csv_writer = CSVWriter()
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
    filename = f'people_{random_string}.csv'
    # TODO save into DB
    for person in people_dataset():
        print(person)
        csv_writer.write(filename, person)