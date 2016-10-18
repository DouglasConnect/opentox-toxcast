FROM python:3
MAINTAINER Daniel Bachler <daniel@douglasconnect.com>
LABEL description="ToxCast data import container to import ToxCast CVS files into Elasticsearch"
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y unzip wget jq
COPY requirements.txt /code/requirements.txt
RUN cd /code && pip install -r requirements.txt --upgrade
COPY . /code
RUN chmod u+x /code/importer.sh
ENTRYPOINT /code/importer.sh
