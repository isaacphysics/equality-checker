FROM python:3.14-slim

# To ensure output printed correctly, alter buffering:
ENV PYTHONUNBUFFERED=0

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY pyproject.toml /usr/src/app/
RUN pip install --no-cache-dir -e .

COPY . /usr/src/app

EXPOSE 5000

CMD ["gunicorn", "--config", "checker/server/gunicorn_conf.py", "checker.server:app"]
