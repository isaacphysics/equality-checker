FROM python:2.7

# To allow the Unicode +- sign to be printed, set IO encoding:
ENV PYTHONIOENCODING UTF-8

# To ensure output printed correctly, alter buffering:
ENV PYTHONUNBUFFERED 0

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

RUN ln -sf /bin/bash /bin/sh

WORKDIR /usr/src/app/checker
CMD gunicorn --config=gunicorn_conf.py server:app