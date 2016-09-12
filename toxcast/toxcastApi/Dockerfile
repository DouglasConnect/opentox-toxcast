FROM python:3
MAINTAINER Daniel Bachler <daniel@douglasconnect.com>
ENV PYTHONUNBUFFERED 1
COPY requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt
COPY . /code/
ENTRYPOINT python app.py
EXPOSE 8080
