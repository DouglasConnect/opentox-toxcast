FROM python:3
MAINTAINER Daniel Bachler <daniel@douglasconnect.com>
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y unzip wget jq
COPY requirements.txt /code/requirements.txt
RUN cd /code && pip install -r requirements.txt --upgrade
COPY . /code
RUN chmod u+x /code/tests.py
ENTRYPOINT python /code/tests.py
