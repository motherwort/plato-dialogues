FROM python:3.11.3-slim-buster

ARG ENVIRONMENT

ENV ENVIRONMENT=${ENVIRONMENT} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.5.1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

# System deps:
RUN apt-get update && \
  apt-get install --no-install-recommends -y \
  bash \
  build-essential \
  curl \
  gettext \
  git \
  libpq-dev \
  wget \
  # drop gdal
  gdal-bin \
  # Cleaning cache:
  && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*
# Installing `poetry` package manager:
# https://github.com/python-poetry/poetry
RUN pip install "poetry-core==1.6.1" "poetry==$POETRY_VERSION" && poetry --version

# Copy only requirements, to cache them in docker layer
WORKDIR /code
COPY ./pyproject.toml ./poetry.lock*  /code/
RUN echo "$ENVIRONMENT"
# Project initialization:
RUN echo "$ENVIRONMENT" \
  && python -m pip install pip==22.1.2 \
  && poetry install \
  $(if [ "$ENVIRONMENT" = 'production' ]; then echo '--no-dev'; fi) \
  --no-interaction --no-ansi \
  # Cleaning poetry installation's cache for production:
  && if [ "$ENVIRONMENT" = 'production' ]; then rm -rf "$POETRY_CACHE_DIR"; fi

# Creating folders, and files for a project:
COPY ./src /code/src/

COPY ./docker/start-web.sh /start-web.sh

# Setting up proper permissions:
RUN chmod +x /start-web.sh \
  && mkdir -p /code/media /code/static/ \
  && chmod +x /code/media/ /code/static/

WORKDIR /code
