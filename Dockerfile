FROM python:3.5
ENV PYTHONUNBUFFERED 1

COPY requirements*.txt /
COPY ./ccstore /app

WORKDIR /app

RUN pip install -r /requirements.txt
