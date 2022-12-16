## Starwars API interview project

### Technical requirements

1. The user should have a way to download the latest  complete  dataset of characters from the API by clicking on a button, the collected and transformed data should be stored as a CSV file in the file system. Metadata for downloaded datasets (e.g. filename, date, etc.) should be stored inside the database. Fetching and transformations should be implemented  efficiently  , minimize the amount of requests, your app should be able to process  large amounts of data  .
2. Add a  date column ( %Y-%m-%d ) based on edited date
Resolve the  homeworld field into the homeworld's name ( /planets/1/ ->
Tatooine )
Fields referencing different resources and date fields other than  date/birth_year
can be dropped
3. The user should be able to inspect all previously downloaded datasets, as well as do simple
exploratory operations on it.
4. By default the table should only show the first 10 rows of the dataset, by clicking on a button
“ Load more  ” additionally 10 rows should be shown - reloading the page is fine.
5. Provide the functionality to count the occurrences of values (combination of values) for columns.
For example when selecting the columns  date and  homeworld the table should show the
counts as follows:

### Tools

- Django and DRF 
- Celery and Redis
- [petl](https://petl.readthedocs.io/en/stable/ "Petl library")
- pytest (WIP)
- Asincio, aiohttp and httpx(WIP)
- Amazon S3 or Minio(WIP)


### Run using shell
1. `python3.9 -m venv venv`
2. `source /venv/bin/activate`
3. `pip install -r requirements.txt`
4. Create .env file base on .env.dev
5. `source docker/export.sh` - export environment variables in your current shell
6. `./docker/start.sh` - start Django application

### Run using docker
1. `docker-compose up app`
2. `docker-compose up flower` - start flower to check celery tasks

### WIP

1. Write more tests using pytest 
2. Asynchronous requests integration
3. Read and write very large files using custom indexes and .seek()
6. Add documentation using sphinx
7. Minio or S3 integration for saving files
