FROM python:3.9
WORKDIR /app

ENV PYTHONUNBUFFERED 1
COPY ./compose/start.sh /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

COPY ./compose/local/celery/worker/start.sh /start-celeryworker
RUN sed -i 's/\r//' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
