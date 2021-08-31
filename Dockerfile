FROM m.docker-registry.ir/python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN mkdir /app
COPY . /app
WORKDIR /app
