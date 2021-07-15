FROM python:3.9.5-slim

# Set pip to have no saved cache
ENV PIP_NO_CACHE_DIR=false \
    POETRY_VIRTUALENVS_CREATE=false \
    MAX_WORKERS=10

# Install poetry
RUN pip install -U poetry

# Create the working directory
WORKDIR /app

# Install project dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

# Copy in the Gunicorn config
COPY ./gunicorn_conf.py /gunicorn_conf.py

# Set Git SHA build argument
ARG git_sha="development"

# Set Git SHA environment variable
ENV GIT_SHA=$git_sha

# Copy the source code in last to optimize rebuilding the image
COPY . /app

EXPOSE 80

CMD ./scripts/start.sh
