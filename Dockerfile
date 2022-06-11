FROM python:3.10-slim

RUN ln -sf /bin/bash /bin/sh

# To allow the Unicode +- sign to be printed, set IO encoding:
ENV PYTHONIOENCODING UTF-8

# To ensure output printed correctly, alter buffering:
ENV PYTHONUNBUFFERED 0

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

CMD gunicorn --config=checker/server/gunicorn_conf.py checker.server:app
