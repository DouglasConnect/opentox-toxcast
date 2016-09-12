FROM python:2.7
MAINTAINER Daniel Bachler <daniel@douglasconnect.com>
LABEL description="Toxcast data import container to fill elasticsearch with data from Toxcast csv files"
RUN apt-get update && apt-get install -y unzip wget jq
COPY requirements.txt /code/requirements.txt
RUN cd /code && pip install -r requirements.txt --upgrade
COPY . /code
RUN chmod u+x /code/import-toxcast.sh
ENTRYPOINT /code/import-toxcast.sh
