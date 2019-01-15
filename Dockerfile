FROM python:3.7

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

CMD gunicorn --config=checker/server/gunicorn_conf checker.server:app