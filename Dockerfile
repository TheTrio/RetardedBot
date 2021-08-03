# Production docker file

FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install pipenv

WORKDIR /app
COPY . /app

RUN pipenv install --system --deploy --ignore-pipfile --dev

VOLUME [ "/app/data" ]

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser


ENV PYTHONPATH=/app
CMD [ "python", "src/Main.py"]